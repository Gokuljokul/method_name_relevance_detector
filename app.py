import os
import sys
import json
from name_relevance_detector import analyze_file


def print_results(results, detailed=False):
    """Print the analysis results in a readable format."""
    print("\n===== NAME RELEVANCE ANALYSIS =====")
    print(f"Overall Score: {results['overall_score']:.2f}/1.00\n")
    
    print("CLASSES:")
    for cls in results["classes"]:
        score_display = f"{cls['relevance_score']:.2f}"
        print(f"  - {cls['name']}: {score_display}/1.00 - {cls['reasons'][0]}")
        if detailed and cls.get('suggestion'):
            print(f"    Suggestion: {cls['suggestion']}")
    
    print("\nFUNCTIONS:")
    for func in results["functions"]:
        score_display = f"{func['relevance_score']:.2f}"
        print(f"  - {func['name']}: {score_display}/1.00 - {func['reasons'][0]}")
        if detailed and func.get('suggestion'):
            print(f"    Suggestion: {func['suggestion']}")


def main():
    """Run the name relevance analysis tool."""
    # Check if a file is provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to analyzing all_func.py
        file_path = os.path.join(os.path.dirname(__file__), "all_func.py")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    # Check if file has .py extension
    if not file_path.endswith('.py'):
        print(f"Error: File '{file_path}' is not a Python file.")
        return
    
    print(f"Analyzing: {file_path}")
    results = analyze_file(file_path)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    # Get detail level from arguments
    detailed = "--detailed" in sys.argv or "-d" in sys.argv
    
    # Print results
    print_results(results, detailed)
    
    # Save results to a JSON file if requested
    if "--save" in sys.argv or "-s" in sys.argv:
        output_file = os.path.basename(file_path).replace('.py', '_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
