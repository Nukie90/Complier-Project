
from ply import lex, yacc

# Symbol table to store variable information
symbol_table = {}

# Token list
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'POWER',
    'LPAREN',
    'RPAREN',
    'EQUALS',
    'NOTEQUALS',
    'IDENTIFIER',
    'LBRACKET',
    'RBRACKET',
)

# Token rules
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_POWER = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_NOTEQUALS = r'!='
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

# Line tracking
line_number = 1
char_position = 1

def t_NUMBER(t):
    r'\d*\.?\d+'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)  # Parse integers as `int`
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_newline(t):
    r'\n+'
    global line_number, char_position
    line_number += len(t.value)
    char_position = 1

# Ignore whitespace
t_ignore = ' \t'

def t_error(t):
    global char_position
    print(f"SyntaxError at line {line_number}, pos {t.lexpos + 1}")
    char_position += 1
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Parsing rules
def p_expression(p):
    '''
    expression : term
               | expression PLUS term
               | expression MINUS term
               | assignment
               | array_element
               | comparison
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"({p[1]}{p[2]}{p[3]})"

def p_term(p):
    '''
    term : factor
         | term TIMES factor
         | term DIVIDE factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"({p[1]}{p[2]}{p[3]})"

def p_factor(p):
    '''
    factor : NUMBER
           | IDENTIFIER
           | LPAREN expression RPAREN
           | array_element
    '''
    if len(p) == 2:  # Single token (NUMBER or IDENTIFIER)
        if isinstance(p[1], (int, float)):
            p[0] = str(p[1])
        else:
            # Check for undefined variables
            if p[1] not in symbol_table:
                raise Exception(f"Undefined variable {p[1]} at line {line_number}, pos {p.lexpos(1) + 1}")
            p[0] = p[1]
    else:  # Parenthesized expression
        p[0] = p[2]

def p_assignment(p):
    '''
    assignment : IDENTIFIER EQUALS expression
    '''
    # Add to symbol table
    symbol_table[p[1]] = {
        'lexeme': p[1],
        'line_number': line_number,
        'start_pos': char_position,
        'length': len(p[1]),
        'type': 'variable',
        'value': None  # Placeholder for actual value
    }
    p[0] = f"({p[1]}{p[2]}{p[3]})"

def p_array_element(p):
    '''
    array_element : IDENTIFIER LBRACKET expression RBRACKET
    '''
    # Format the index expression properly
    p[0] = f"({p[1]}[({p[3]})])"

def p_comparison(p):
    '''
    comparison : expression NOTEQUALS factor
    '''
    p[0] = f"({p[1]}{p[2]}{p[3]})"

def p_error(p):
    if p:
        raise Exception(f"SyntaxError at line {line_number}, pos {p.lexpos + 1}")
    else:
        raise Exception("SyntaxError at EOF")

# Build the parser
parser = yacc.yacc()

def parse_input(input_text):
    global line_number, char_position
    line_number = 1
    char_position = 1
    
    for line in input_text.split('\n'):
        if line.strip():
            try:
                result = parser.parse(line.strip())
                if result:
                    print(f"{result}")
            except Exception as e:
                print(f"{str(e)}")
        line_number += 1

# Read input from file
def read_input_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Could not find file {filename}")
        return ""
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return ""

# Main execution
input_text = read_input_file('input.txt')
if input_text:
    parse_input(input_text)