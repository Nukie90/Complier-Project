import re

token_list = {
    "list": r"list",
    
    "REAL": r"[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?",
    
    "INT": r"[0-9]+",
    
    "VAR": r"[a-zA-Z_][a-zA-Z0-9_]*",
    
    "ASSIGN": r"=",
    
    #Operators
    "+": r"\+",
    "-": r"-",
    "*": r"\*",
    "/": r"/",
    "%": r"%",
    "POW": r"\^",
    
    #Comparison
    "!=": r"!=",
    "==": r"==",
    ">": r">",
    "<": r"<",
    ">=": r">=",
    "<=": r"<=",
    
    #Brackets
    "(": r"LPAREN",
    ")": r"RPAREN",
    "[": r"LBRACKET",
    "]": r"RBRACKET",
    
    #Others
    "WHITESPACE": r"\s+",
    
}
