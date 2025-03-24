import ast
import re
from collections import Counter
from typing import List, Dict, Tuple, Any, Optional


class NameRelevanceDetector:
    """Detects if function and class names are relevant to their implementation."""
    
    def __init__(self, code_file: str):
        """Initialize with file path to analyze."""
        self.code_file = code_file
        self.code = None
        self.tree = None
        self.load_file()
        
    def load_file(self):
        """Load and parse the Python file."""
        try:
            with open(self.code_file, 'r', encoding='utf-8') as file:
                self.code = file.read()
            self.tree = ast.parse(self.code)
        except Exception as e:
            print(f"Error loading or parsing file: {e}")
            
    def analyze(self) -> Dict:
        """Analyze the code and return relevance scores."""
        if not self.tree:
            return {"error": "Failed to parse the file"}
            
        results = {
            "classes": self._analyze_classes(),
            "functions": self._analyze_functions(),
            "overall_score": 0.0
        }
        
        # Calculate overall score
        class_scores = [c["relevance_score"] for c in results["classes"]]
        func_scores = [f["relevance_score"] for f in results["functions"]]
        all_scores = class_scores + func_scores
        
        if all_scores:
            results["overall_score"] = sum(all_scores) / len(all_scores)
            
        return results
    
    def _analyze_classes(self) -> List[Dict]:
        """Analyze class names versus their implementation."""
        classes = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_docstring = ast.get_docstring(node) or ""
                
                # Extract implementation details
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                attributes = self._extract_class_attributes(node)
                
                # Create implementation summary
                impl_summary = f"{class_docstring} {' '.join(methods)} {' '.join(attributes)}"
                
                # Calculate relevance score
                score, reasons = self._calculate_relevance(class_name, impl_summary)
                
                classes.append({
                    "name": class_name,
                    "relevance_score": score,
                    "reasons": reasons,
                    "suggestion": self._generate_suggestion(class_name, impl_summary) if score < 0.7 else None
                })
                
        return classes
    
    def _analyze_functions(self) -> List[Dict]:
        """Analyze function names versus their implementation."""
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and not self._is_method(node):
                func_name = node.name
                func_docstring = ast.get_docstring(node) or ""
                
                # Get function body as text
                func_body = self._get_node_source(node)
                
                # Create implementation summary
                impl_summary = f"{func_docstring} {func_body}"
                
                # Calculate relevance score
                score, reasons = self._calculate_relevance(func_name, impl_summary)
                
                functions.append({
                    "name": func_name,
                    "relevance_score": score,
                    "reasons": reasons,
                    "suggestion": self._generate_suggestion(func_name, impl_summary) if score < 0.7 else None
                })
                
        return functions
    
    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a method within a class."""
        return any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(self.tree) 
                   if hasattr(parent, 'body') and node in parent.body)
    
    def _extract_class_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract attribute names from a class definition."""
        attributes = []
        for n in node.body:
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        return attributes
    
    def _get_node_source(self, node: ast.AST) -> str:
        """Get the source code for a node as a string."""
        if not self.code:
            return ""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            lines = self.code.splitlines()[node.lineno-1:node.end_lineno]
            return " ".join(lines)
        return ""
    
    def _calculate_relevance(self, name: str, implementation: str) -> Tuple[float, List[str]]:
        """Calculate a relevance score between a name and its implementation."""
        reasons = []
        score = 0.0
        
        # Convert camelCase or PascalCase to snake_case for analysis
        name_parts = self._split_name(name)
        
        # Remove common prefixes/suffixes that don't add semantic meaning
        filtered_parts = [p for p in name_parts if p not in ('get', 'set', 'is', 'has', 'on', 'class')]
        
        # Count meaningful parts found in implementation
        found_parts = 0
        for part in filtered_parts:
            if len(part) > 2 and re.search(r'\b' + re.escape(part) + r'\b', implementation, re.IGNORECASE):
                found_parts += 1
            elif part in implementation.lower():
                found_parts += 0.5
        
        if not filtered_parts:
            score = 0.5
            reasons.append("Name doesn't contain meaningful parts")
        else:
            score = found_parts / len(filtered_parts) if filtered_parts else 0.0
        
        # Adjust score based on additional factors
        if name.lower() in ('test', 'helper', 'util', 'utility', 'misc'):
            score -= 0.2
            reasons.append("Name is too generic")
            
        if len(name) <= 2:
            score -= 0.3
            reasons.append("Name is too short")
            
        if score < 0.3:
            reasons.append("Name different from implementation - Wrong name")
        elif score < 0.5:
            reasons.append("Name somewhat reflects implementation - Consider changing")
                           
        elif score < 0.6:
            reasons.append("Name reflects implementation - needs improvement")                           
        
        elif score < 0.7:
            reasons.append("Name reflects implementation - good")
        else:
            reasons.append("Name reflects implementation well")
            
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, reasons
    
    def _split_name(self, name: str) -> List[str]:
        """Split a name into parts based on common naming conventions."""
        # Handle snake_case
        if '_' in name:
            return [part.lower() for part in name.split('_') if part]
        
        # Handle camelCase and PascalCase
        parts = []
        current = ""
        for char in name:
            if char.isupper() and current:
                parts.append(current.lower())
                current = char
            else:
                current += char
        if current:
            parts.append(current.lower())
            
        return parts
    
    def _generate_suggestion(self, original_name: str, implementation: str) -> str:
        """Generate a name suggestion based on implementation."""
        # Extract most common words from implementation
        words = re.findall(r'\b[a-zA-Z]{3,}\b', implementation.lower())
        word_counts = Counter(words)
        
        # Remove stop words and code-specific words
        stop_words = {'the', 'and', 'for', 'with', 'from', 'self', 'none', 'true', 'false', 'return'}
        for word in stop_words:
            if word in word_counts:
                del word_counts[word]
                
        # Get most common remaining words
        common_words = [word for word, _ in word_counts.most_common(3)]
        
        if not common_words:
            return "Consider adding a clear docstring to help determine a better name"
            
        # Format based on original casing style
        if '_' in original_name:
            return f"Consider: {'_'.join(common_words)}"
        elif original_name[0].isupper():
            return f"Consider: {''.join(word.capitalize() for word in common_words)}"
        else:
            return f"Consider: {common_words[0]}{''.join(word.capitalize() for word in common_words[1:])}"


def analyze_file(file_path: str) -> Dict:
    """Analyze a Python file and return relevance results."""
    detector = NameRelevanceDetector(file_path)
    return detector.analyze()
