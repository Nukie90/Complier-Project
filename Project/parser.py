import ply.lex as lex
import ply.yacc as yacc
import csv

# Global line counter
current_line = 0

# Define token types
tokens = (
    "REAL", 
    "INT", 
    "VAR", 
    "ASSIGN",
    "ADD", 
    "SUB", 
    "MUL", 
    "DIV", 
    "IDIV", 
    "POW",
    "LT", 
    "LE", 
    "GT", 
    "GE", 
    "EQ", 
    "NE",
    "LPAREN", 
    "RPAREN", 
    "LBRACKET", 
    "RBRACKET",
    "LIST", 
    "DIV_ASSIGN", 
    "ERROR"
)

# Token regex patterns
t_REAL = r"-?[0-9]*\.[0-9]+([eE][+-]?[0-9]+)?"
t_INT = r"-?[0-9]+"
t_DIV_ASSIGN = r"/="
t_ASSIGN = r"="
t_ADD = r"\+"
t_SUB = r"-"
t_MUL = r"\*"
t_DIV = r"/"
t_IDIV = r"//"
t_POW = r"\^"
t_LT = r"<"
t_LE = r"<="
t_GT = r">"
t_GE = r">="
t_EQ = r"=="
t_NE = r"!="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"

def t_VAR(t):
    r"[a-zA-Z][a-zA-Z0-9_]*"
    if t.value == "list":
        t.type = "LIST"
    return t

t_ignore = " \t"

def t_ERROR(t):
    r"[^\s\w\.\+\-\*/=<>!()\[\]^]"
    raise Exception(f"SyntaxError at line {current_line}, pos {t.lexpos + 1}")

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise Exception(f"SyntaxError at line {current_line}, pos {t.lexpos + 1}")

lexer = lex.lex()

# Define precedence
precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
    ('right', 'POW'),
)

# Symbol table as dictionary
symbol_table = {}

def p_program(p):
    """program : statement
               | expression"""
    p[0] = p[1]

def p_statement_assign(p):
    "statement : VAR ASSIGN expression"
    # Store variable in symbol table with its current line info
    symbol_table[p[1]] = {
        "lexeme": p[1],
        "line_number": current_line,
        "start_pos": p.lexpos(1) + 1,
        "length": len(p[1]),
        "type": "VAR",
        "value": p[3]
    }
    p[0] = f"({p[1]}={p[3]})"

def p_statement_list_assign(p):
    "statement : VAR ASSIGN LIST LBRACKET expression RBRACKET"
    # Store list variable in symbol table with its current line info
    symbol_table[p[1]] = {
        "lexeme": p[1],
        "line_number": current_line,
        "start_pos": p.lexpos(1) + 1,
        "length": len(p[1]),
        "type": "LIST",
        "value": "ARRAY"
    }
    p[0] = f"({p[1]} = (list[({p[5]})]))"

def p_expression_operation(p):
    """expression : expression ADD expression
                 | expression SUB expression
                 | expression MUL expression
                 | expression DIV expression
                 | expression POW expression
                 | expression NE expression"""
    if p[2] == '^':
        p[0] = f"({p[1]}**{p[3]})"
    else:
        # Keep all parentheses intact for proper list access handling
        p[0] = f"({p[1]}{p[2]}{p[3]})"

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    # Don't add extra parentheses if expression is already wrapped
    if p[2].startswith('(') and p[2].endswith(')'):
        p[0] = p[2]
    else:
        p[0] = f"({p[2]})"
        
def p_expression_var(p):
    "expression : VAR"
    if p[1] not in symbol_table:
        raise Exception(f"Undefined variable {p[1]} at line {current_line}, pos {p.lexpos(1) + 1}")
    p[0] = p[1]

def p_expression_number(p):
    """expression : INT
                 | REAL"""
    p[0] = p[1]

def p_expression_list_access(p):
    "expression : VAR LBRACKET expression RBRACKET"
    if p[1] not in symbol_table:
        raise Exception(f"Undefined variable {p[1]} at line {current_line}, pos {p.lexpos(1) + 1}")
    p[0] = f"({p[1]}[({p[3]})])"

def p_error(p):
    if p:
        raise Exception(f"SyntaxError at line {current_line}, pos {p.lexpos + 1}")
    else:
        raise Exception("Syntax error at EOF")

parser = yacc.yacc()

def process_input(input_text, line_num):
    global current_line
    current_line = line_num
    try:
        lexer.lineno = line_num
        result = parser.parse(input_text)
        return result
    except Exception as e:
        return str(e)

def process_input_files():
    # Process input file and write output
    with open("input.txt", "r") as infile, open("ChocolateLava.bracket", "w") as outfile:
        line_num = 1
        lines = infile.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                result = process_input(line, i)
                outfile.write(f"{result}\n")
    
    # Write symbol table to CSV
    with open("ChocolateLava.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, 
                              fieldnames=["lexeme", "line_number", "start_pos", "length", "type", "value"])
        writer.writeheader()
        for lexeme, entry in symbol_table.items():
            writer.writerow(entry)
            
def tokenize_input():
    with open("input.txt", "r") as infile, open("ChocolateLava.tok", "w") as outfile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if line:
                lexer.input(line)
                tokens = []
                try:
                    for tok in lexer:
                        tokens.append(f"{tok.value}/{tok.type}")
                    outfile.write(" ".join(tokens) + "\n")
                except Exception as e:
                    outfile.write(f"{line}/ERR\n")
                    
def write_lexical_grammar():
    lexical_rules = [
        "REAL (0-9)*\\.(0-9)*",
        "INT (0-9)*",
        "DIV_ASSIGN /=",
        "ASSIGN =",
        "ADD \\+",
        "SUB -",
        "MUL \\*",
        "DIV /",
        "IDIV //",
        "POW \\^",
        "LT <",
        "LE <=",
        "GT >",
        "GE >=",
        "EQ ==",
        "NE !=",
        "LPAREN \\(",
        "RPAREN \\)",
        "LBRACKET \\[",
        "RBRACKET \\]",
        "VAR [a-zA-Z][a-zA-Z0-9_]*",
        "LIST list",
        "WHITESPACE [ \\t]+",
        "NEWLINE \\n+",
        "ERROR [^\\s\\w\\.\\+\\-\\*/=<>!()\\[\\]^]"
    ]
    
    with open("ChocolateLava.lex", "w") as outfile:
        for rule in lexical_rules:
            outfile.write(f"{rule}\n")
            
def write_grammar():
    grammar_rules = [
    "<program> ::= <statement> | <expression> | <statement> <program> | <expression> <program>",
    "<statement> ::= <VAR> <ASSIGN> <expression>",
    "<statement> ::= <VAR> <ASSIGN> <LIST> <LBRACKET> <expression> <RBRACKET>",
    "<expression> ::= <SUB> <expression> %prec UMINUS",
    "<expression> ::= <SUB> <VAR> %prec UMINUS",
    "<expression> ::= <expression> <ADD> <expression> | <expression> <SUB> <expression>",
    "<expression> ::= <expression> <MUL> <expression> | <expression> <DIV> <expression>",
    "<expression> ::= <expression> <IDIV> <expression>",
    "<expression> ::= <expression> <POW> <expression>",
    "<expression> ::= <LPAREN> <expression> <RPAREN>",
    "<expression> ::= <INT> | <REAL>",
    "<expression> ::= <VAR>",
    "<expression> ::= <VAR> <LBRACKET> <expression> <RBRACKET>",
    "<expression> ::= <expression> <LT> <expression> | <expression> <LE> <expression>",
    "<expression> ::= <expression> <GT> <expression> | <expression> <GE> <expression>",
    "<expression> ::= <expression> <EQ> <expression> | <expression> <NE> <expression>",
    "<expression> ::= <VAR> <DIV_ASSIGN> <expression>",
    ]
    
    with open("ChocolateLava.grammar", "w") as outfile:
        for rule in grammar_rules:
            outfile.write(f"{rule}\n")

def main():
    process_input_files()
    tokenize_input()
    write_lexical_grammar()
    write_grammar()

if __name__ == "__main__":
    main()