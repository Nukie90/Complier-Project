import ply.lex as lex
import ply.yacc as yacc

tokens = (  # Define tokens FIRST
    "REAL", "INT", "ID", "LIST", # ADD LIST TOKEN
    "ADD", "SUB", "MUL", "DIV", "EQUALS", "NE",
    "LBRACKET", "RBRACKET" # Add brackets for list access
)

t_LIST = r"list" # DEFINE LIST KEYWORD
t_ADD = r"\+"
t_SUB = r"-"
t_MUL = r"\*"
t_DIV = r"/"
t_EQUALS = r"="
t_NE = r"!="
t_LBRACKET = r"\[" # Define left bracket
t_RBRACKET = r"\]" # Define right bracket


t_ignore = " \t"

# ... (rest of your lexer functions t_REAL, t_INT, t_ID, t_newline, t_error) ...
def t_REAL(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t

def t_INT(t):
    r"\b\d+\b"
    t.value = int(t.value)
    return t

def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    if t.value == "list": # Handle 'list' keyword to avoid ID tokenization
        t.type = "LIST"
        return t
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"ERROR")
    t.lexer.skip(1)
    raise SyntaxError(f"Lexical ERROR: Unexpected character '{t.value[0]}' at line {t.lineno}")

lexer = lex.lex()

precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
)

symbol_table = {}

def p_statement(p):
    """
    statement : statement statement
              | statement_expr
              | statement_assign
              | statement_list_decl
              | expression
    """
    if len(p) == 3:
        p[0] = (p[1] or "") + ("" if not p[2] else "\n" + p[2])  # Avoids double newlines
    else:
        p[0] = p[1]

def p_statement_expr(p):
    """statement_expr : expression""" # Renamed to statement_expr
    p[0] = p[1]

def is_id(p):
    return isinstance(p, str) and p in symbol_table

def p_statement_assign(p):
    """statement_assign : ID EQUALS expression""" #Renamed to statement_assign
    if isinstance(p[3], str) and p[3] not in symbol_table:
        p[0] = "ERROR"
        print(f"ERROR: Undefined variable '{p[3]}' in assignment.")
        return

    symbol_table[p[1]] = (p[3], type(p[3]) if not isinstance(p[3],str) else type(symbol_table.get(p[3])[0]) if symbol_table.get(p[3]) is not None else None) # Store value AND type

    if isinstance(p[3], (int, float)):
        p[0] = f"LD R0 #{p[3]}\nST @{p[1]} R0"
    elif isinstance(p[3], str) and p[3] in symbol_table:
        p[0] = f"LD R0 @{p[3]}\nST @{p[1]} R0"
    else:
        p[0] = "ERROR"
        print("ERROR: Invalid assignment type.")
        return

def p_statement_list_decl(p):
    """statement_list_decl : LIST ID LBRACKET INT RBRACKET"""
    list_name = p[2]
    list_size = int(p[4])
    
    if list_size <= 0:
        p[0] = "ERROR"
        print(f"ERROR: List size must be greater than 0 for list '{list_name}'.")
        return

    # If 'x' exists in symbol_table, allow re-declaration as a list
    if list_name in symbol_table:
        del symbol_table[list_name]  # Remove old variable (int, float, or string)

    # Store the list in the symbol table
    symbol_table[list_name] = {
        'type': 'list',
        'size': list_size,
        'base_address': list_name  # Placeholder for assembler
    }

    p[0] = ""  # Initialize output

    # First iteration: Full initialization
    p[0] += f"LD R0 #0\n"  # Load value 0
    p[0] += f"LD R1 @{list_name}\n"  # Load base address
    p[0] += f"LD R2 #0\n"  # Load index
    p[0] += f"LD R3 #4\n"  # Load element size (assuming 4 bytes per element)
    p[0] += f"MUL.i R4 R2 R3\n"  # Calculate offset
    p[0] += f"ADD.i R5 R1 R4\n"  # Compute address
    p[0] += f"ST @R5 R0\n"  # Store 0 at computed address

    # Subsequent iterations: Avoid reloading R0 and R1
    for i in range(1, list_size):
        p[0] += f"LD R2 #{i}\n"  # Load index
        p[0] += f"LD R3 #4\n"  # Load element size
        p[0] += f"MUL.i R4 R2 R3\n"  # Calculate offset
        p[0] += f"ADD.i R5 R1 R4\n"  # Compute address
        p[0] += f"ST @R5 R0\n"  # Store 0 at computed address

def p_expression_binop(p):
    """
    expression : expression ADD expression
               | expression SUB expression
               | expression MUL expression
               | expression DIV expression
    """
    op_map = {"+": "ADD.i", "-": "SUB.i", "*": "MUL.i", "/": "DIV.i"}
    float_ops = {"*": "MUL.f", "/": "DIV.f", "+": "ADD.f", "-": "SUB.f"}

    p[0] = ""

    # Load left operand
    if isinstance(p[1], (int, float)):
        p[0] += f"LD R0 #{p[1]}\n"
        left_type = type(p[1])
    elif isinstance(p[1], str) and p[1] in symbol_table:  # Check symbol table!
        p[0] += f"LD R0 @{p[1]}\n"
        left_type = type(symbol_table[p[1]])
    else:
        left_type = None  # Handle undefined variables

    # Load right operand
    if isinstance(p[3], (int, float)):
        p[0] += f"LD R1 #{p[3]}\n"
        right_type = type(p[3])
    elif isinstance(p[3], str) and p[3] in symbol_table:  # Check symbol table!
        p[0] += f"LD R1 @{p[3]}\n"
        right_type = type(symbol_table[p[3]])
    else:
        right_type = None  # Handle undefined variables

    if left_type is float or right_type is float or (left_type is int and right_type is None) or (right_type is int and left_type is None):
        if left_type is int and right_type is not None: #added right_type check
            p[0] += "FL.i R0 R0\n"
        if right_type is int and left_type is not None: #added left_type check
            p[0] += "FL.i R1 R1\n"
        p[0] += f"{float_ops[p[2]]} R2 R0 R1\nST @print R2"
    else:
        p[0] += f"{op_map[p[2]]} R2 R0 R1\nST @print R2"

def p_expression_ne(p):
    """expression : expression NE expression"""
    p[0] = ""

    # Load right operand into R0 (CHANGED ORDER - as per user request for x!=5 output)
    if isinstance(p[3], (int, float)):
        p[0] += f"LD R0 #{p[3]}\n"
        right_type = type(p[3])
    elif isinstance(p[3], str) and p[3] in symbol_table:
        p[0] += f"LD R0 @{p[3]}\n"
        right_type = symbol_table[p[3]][1]  # Get type from symbol table
    else:
        right_type = None

    # Load left operand into R1 (CHANGED ORDER)
    if isinstance(p[1], (int, float)):
        p[0] += f"LD R1 #{p[1]}\n"
        left_type = type(p[1])
    elif isinstance(p[1], str) and p[1] in symbol_table:
        p[0] += f"LD R1 @{p[1]}\n"
        left_type = symbol_table[p[1]][1]  # Get type from symbol table
    else:
        left_type = None

    # Always float convert and use NE.f (FORCED FLOAT - to address user's x!=5 issue)
    if right_type is int: # now right_type is checked first and R0 is converted first
        p[0] += "FL.i R0 R0\n"
    if left_type is int: # then left_type is checked and R1 is converted second
        p[0] += "FL.i R1 R1\n"
    p[0] += "NE.f R2 R0 R1\nST @print R2"

def p_expression_number(p):
    """
    expression : INT
               | REAL
    """
    p[0] = p[1]

def p_expression_id(p): #added for ID
    """expression : ID"""
    p[0] = p[1]

def p_expression_list_access(p):
    """expression : ID LBRACKET INT RBRACKET"""
    list_name = p[1]
    index = int(p[3])

    # Check if the list exists in the symbol table
    if list_name not in symbol_table or symbol_table[list_name]['type'] != 'list':
        p[0] = "ERROR"
        print(f"ERROR: '{list_name}' is not a declared list.")
        return

    # Ensure the index is within bounds
    list_size = symbol_table[list_name]['size']
    if index < 0 or index >= list_size:
        p[0] = "ERROR"
        print(f"ERROR: Index {index} out of bounds for list '{list_name}' (size {list_size}).")
        return
    
    # Generate assembly code for accessing x[index]
    p[0] = f"LD R0 @{list_name}\n"  # Load base address of the list
    p[0] += f"LD R1 #{index}\n"  # Load index
    p[0] += f"LD R2 #4\n"  # Load element size (assuming 4 bytes per element)
    p[0] += f"MUL.i R3 R1 R2\n"  # Calculate offset (index * 4)
    p[0] += f"ADD.i R4 R0 R3\n"  # Compute address of x[index]
    p[0] += f"ST $print R4\n"  # Print the value stored at x[index]

def p_error(p):
    print("ERROR")

parser = yacc.yacc()

def process_input(input_text):
    try:
        result = parser.parse(input_text)
        return str(result) if result else "ERROR"
    except SyntaxError as e:
        return "ERROR"
    except Exception:
        return "ERROR"

if __name__ == "__main__":
    with open("input.txt", "r") as infile, open("output.asm", "w") as outfile:
        for line in infile:
            line = line.strip()
            if line:
                result = process_input(line)
                outfile.write(result.strip() + "\n\n")  # Ensure only one newline