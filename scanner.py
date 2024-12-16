import re

# Define token types with their regex patterns
TOKEN_SPEC = [
    ("INT", r"\b[0-9]+\b"),  # Integer
    ("REAL", r"\b[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\b"),  # Real number
    ("VAR", r"\b[a-zA-Z][a-zA-Z0-9_]*\b"),  # Variable
    ("LIST", r"\blist\b"),  # Keyword 'list'
    ("POW", r"\^"),  # Exponentiation
    ("ADD", r"\+"),  # Addition
    ("SUB", r"-"),  # Subtraction
    ("MUL", r"\*"),  # Multiplication
    ("DIV", r"/"),  # Division
    ("IDIV", r"//"),  # Integer division
    ("GT", r">"),  # Greater than
    ("GTE", r">="),  # Greater than or equal to
    ("LT", r"<"),  # Less than
    ("LTE", r"<="),  # Less than or equal to
    ("EQ", r"=="),  # Equal to
    ("NEQ", r"!="),  # Not equal to
    ("ASSIGN", r"="),  # Assignment
    ("LPAREN", r"\("),  # Left parenthesis
    ("RPAREN", r"\)"),  # Right parenthesis
    ("LBRACKET", r"\["),  # Left bracket
    ("RBRACKET", r"\]"),  # Right bracket
    ("ERR", r"."),  # Any invalid character
]

# Compile regex patterns
TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
token_re = re.compile(TOKEN_REGEX)

def tokenize(line):
    """
    Tokenize a single line of input and return tokens as a formatted string.
    """
    tokens = []
    for match in token_re.finditer(line):
        token_type = match.lastgroup
        value = match.group()
        tokens.append(f"{value}/{token_type}")
    return " ".join(tokens)

def process_file(input_file, output_file):
    """
    Read input file line by line, tokenize each line, and write the results to an output file.
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            # Remove extra spaces and tokenize the line
            tokenized_line = tokenize(line.strip())
            # Write the tokenized line to the output file
            outfile.write(tokenized_line + "\n")

# Example usage
if __name__ == "__main__":
    input_file = "input.txt"  # Replace with your input file path
    output_file = "output.txt"  # Replace with your output file path
    
    # Process the input file and generate the output
    process_file(input_file, output_file)
    print(f"Tokenized output written to {output_file}")
