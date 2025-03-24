# method_name_relevance_detector
Solution for Name Relevance Detector
I'll create a tool that analyzes Python code to determine if class and function names are relevant to their implementations. This will help identify naming issues that could make the code harder to understand.

Step-by-step solution:
Create a name relevance detector module that uses Python's AST (Abstract Syntax Tree) module to parse and analyze code
Implement functions to extract class and function definitions
Use NLP techniques to analyze name relevance against implementation
Provide a scoring system and recommendations
Set up a simple app to run the tool
name_relevance_detector.py
This is the core module that will analyze code and determine name relevance.

## app.py - simple application that uses the name relevance detector 
## name_relevance_detector.py This is the core module that will analyze code and determine name relevance.



How to use the tool:
Run the tool with the following command:
```
python app.py
```

This will analyze the all_func.py file by default.

To analyze a specific file:
```
python app.py path/to/your/file.py
```

For detailed output with suggestions:
```
python app.py --detailed
```

To save the results to a JSON file:
```
python app.py --save
```

The tool will evaluate each class and function in the file and provide a relevance score between 0 and 1, along with reasons for the score and suggestions for improvement when the score is below 0.7.