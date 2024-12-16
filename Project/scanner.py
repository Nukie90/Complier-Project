import re

class Lexeme:
    def __init__(self, token, lexeme):
        self.token = token
        self.lexeme = lexeme

    def __str__(self):
        return f"{self.lexeme}/{self.token}"

    def __repr__(self):
        return str(self)
    
class Scanner:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.token_list = {
            "list": r"list",
            "REAL": r"[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?",
            "INT": r"[0-9]+",
            "VAR": r"[a-zA-Z_][a-zA-Z0-9_]*",
            "ASSIGN": r"=",
            "+": r"\+",
            "-": r"-",
            "*": r"\*",
            "/": r"/",
            "POW": r"\^",
            "!=": r"!=",
            "==": r"==",
            ">": r">",
            "<": r"<",
            ">=": r">=",
            "<=": r"<=",
            "LPAREN": r"\(",
            "RPAREN": r"\)",
            "LBRACKET": r"\[",
            "RBRACKET": r"\]",
            "WHITESPACE": r"\s+",
        }
        
    def scan(self):
        self.tokens = []
        while self.pos < len(self.text):
            # Skip whitespace
            whitespace_match = re.match(self.token_list["WHITESPACE"], self.text[self.pos:])
            if whitespace_match:
                self.pos += len(whitespace_match.group(0))
                continue
            
            # Try to match tokens
            matched = False
            for token, pattern in self.token_list.items():
                if token == "WHITESPACE":
                    continue
                
                match = re.match(pattern, self.text[self.pos:])
                if match:
                    lexeme = match.group(0)
                    self.tokens.append(Lexeme(token, lexeme))
                    self.pos += len(lexeme)
                    matched = True
                    break
            
            # Handle unrecognized characters
            if not matched:
                # Instead of raising an error, create an ERR token
                self.tokens.append(Lexeme("ERR", self.text[self.pos]))
                self.pos += 1
        
        return self.tokens
    
    def __str__(self):
        return " ".join(str(token) for token in self.tokens)
    
    def __repr__(self):
        return str(self)
    
def process_file():
    with open("input.txt", "r") as f:
        lines = f.readlines()
    
    with open("output.tok", "w") as f:
        for line in lines:
            scanner = Scanner(line)
            tokens = scanner.scan()
            f.write(str(scanner) + "\n")
            print(tokens)
            
    #grammar
    with open("output.lex", "w") as f:
        for value, regex in scanner.token_list.items():
            f.write(f"{value}: {regex}\n")
            
if __name__ == "__main__":
    process_file()
    print("Tokenized output written to output.tok")
            

    