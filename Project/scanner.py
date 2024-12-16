import re
from token_lexeme import token_list

class Lexeme:
    def __init__(self, token, lexeme):
        self.token = token
        self.lexeme = lexeme

    def __str__(self):
        return f"({self.token}, {self.lexeme})"

    def __repr__(self):
        return str(self)
    
class Scanner:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.lexeme = ""
        
    def scan(self):
        while self.pos < len(self.text):
            for token, lexeme in token_list.items():
                match = re.match(lexeme, self.text[self.pos:])
                if match:
                    self.lexeme = match.group(0)
                    self.tokens.append(Lexeme(token, self.lexeme))
                    self.pos += len(self.lexeme)
                    break
            else:
                raise ValueError(f"Invalid character found: {self.text[self.pos]}")
        return self.tokens
    
    def __str__(self):
        return str(self.tokens)
    
    def __repr__(self):
        return str(self)
    
    
#Lexical grammar file
with open("Mango1234.lex", "w") as lexfile:
    for token_name, regex in token_list.items():
        lexfile.write(f"{token_name}: {regex}\n")
    
    