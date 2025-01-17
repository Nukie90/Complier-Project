# Lexical and Syntax Analyzer

## Requirements
- Python 3.x
- PLY (Python Lex-Yacc) library

## Installation

1. Install PLY using pip:
```bash
pip install ply
```

## Files Structure
- `parser.py`: The main program containing lexer and parser implementation
- `input.txt`: Input file containing expressions to analyze

## Running the Program

1. Place your input expressions in `input.txt`, one expression per line
2. Run the program:
```bash
python Project/parser.py 
```

## Output Files
The program generates four files:

1. `ChocolateLava.bracket`: Contains the parsed expressions with proper bracketing
2. `ChocolateLava.tok`: Contains the tokenized version of each input line
3. `ChocolateLava.lex`: Contains the lexical grammar rules
4. `ChocolateLava.grammar`: Contains the syntax grammar rules
5. `ChocolateLava.csv`: Contains the symbol table information

## Input File Format
- Each expression should be on a new line
- Supported operations: +, -, *, /, ^, !=
- Supports integers, real numbers, variables, and list operations
- Example input:
```
23+8
2.5 * 0
x=5
x = list[2]
x[0] + x[1]
```
