import ply.lex as lex
import ply.yacc as yacc

class Compiler:
    def __init__(self):
        # Define tokens
        self.tokens = (
            "REAL", "INT", "ID", "LIST",
            "ADD", "SUB", "MUL", "DIV", "EXP",
            "EQUALS", "NE",
            "LBRACKET", "RBRACKET"
        )
        
        # Token regex patterns
        self.t_LIST = r"list"
        self.t_ADD = r"\+"
        self.t_SUB = r"-"
        self.t_MUL = r"\*"
        self.t_DIV = r"/"
        self.t_EQUALS = r"="
        self.t_NE = r"!="
        self.t_LBRACKET = r"\["
        self.t_RBRACKET = r"\]"
        self.t_EXP = r"\^"
        self.t_ignore = " \t"

        # Set up precedence rules
        self.precedence = (
            ('left', 'ADD', 'SUB'),
            ('left', 'MUL', 'DIV'),
            ('right', 'EXP'),
        )

        # Initialize symbol table
        self.symbol_table = {}

        # Build lexer and parser
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    # Lexer methods
    def t_REAL(self, t):
        r"\d+\.\d+"
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r"\b\d+\b"
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        if t.value == "list":
            t.type = "LIST"
        return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"ERROR")
        t.lexer.skip(1)
        raise SyntaxError(f"Lexical ERROR: Unexpected character '{t.value[0]}' at line {t.lineno}")

    # Parser methods
    def p_statement(self, p):
        """
        statement : statement statement
                 | statement_expr
                 | statement_assign
                 | statement_list_decl
                 | expression
        """
        if len(p) == 3:
            p[0] = (p[1] or "") + ("" if not p[2] else "\n" + p[2])
        else:
            p[0] = p[1]

    def p_statement_expr(self, p):
        """statement_expr : expression"""
        p[0] = p[1]

    def is_id(self, p):
        return isinstance(p, str) and p in self.symbol_table

    def p_statement_assign(self, p):
        """statement_assign : ID EQUALS expression"""
        if isinstance(p[3], str) and p[3] not in self.symbol_table:
            p[0] = "ERROR"
            print(f"ERROR: Undefined variable '{p[3]}' in assignment.")
            return

        self.symbol_table[p[1]] = (p[3], type(p[3]) if not isinstance(p[3], str) 
                                  else type(self.symbol_table.get(p[3])[0]) 
                                  if self.symbol_table.get(p[3]) is not None else None)

        if isinstance(p[3], (int, float)):
            p[0] = f"LD R0 #{p[3]}\nST @{p[1]} R0"
        elif isinstance(p[3], str) and p[3] in self.symbol_table:
            p[0] = f"LD R0 @{p[3]}\nST @{p[1]} R0"
        else:
            p[0] = "ERROR"
            print("ERROR: Invalid assignment type.")
            return

    def p_statement_list_decl(self, p):
        """statement_list_decl : LIST ID LBRACKET INT RBRACKET"""
        list_name = p[2]
        list_size = int(p[4])
        
        if list_size <= 0:
            p[0] = "ERROR"
            print(f"ERROR: List size must be greater than 0 for list '{list_name}'.")
            return

        if list_name in self.symbol_table:
            del self.symbol_table[list_name]

        self.symbol_table[list_name] = {
            'type': 'list',
            'size': list_size,
            'base_address': list_name
        }

        p[0] = self._generate_list_initialization(list_name, list_size)

    def _generate_list_initialization(self, list_name, list_size):
        """Helper method to generate list initialization assembly code"""
        asm_code = []
        # First iteration
        asm_code.extend([
            f"LD R0 #0",
            f"LD R1 @{list_name}",
            f"LD R2 #0",
            f"LD R3 #4",
            f"MUL.i R4 R2 R3",
            f"ADD.i R5 R1 R4",
            f"ST @R5 R0"
        ])

        # Subsequent iterations
        for i in range(1, list_size):
            asm_code.extend([
                f"LD R2 #{i}",
                f"LD R3 #4",
                f"MUL.i R4 R2 R3",
                f"ADD.i R5 R1 R4",
                f"ST @R5 R0"
            ])

        return "\n".join(asm_code)

    def p_expression_binop(self, p):
        """
        expression : expression ADD expression
                  | expression SUB expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression EXP expression
        """
        op_map = {"+": "ADD.i", "-": "SUB.i", "*": "MUL.i", "/": "DIV.i", "^": "EXP.i"}
        float_ops = {"*": "MUL.f", "/": "DIV.f", "+": "ADD.f", "-": "SUB.f", "^": "EXP.f"}

        p[0] = self._generate_binop_code(p[1], p[2], p[3], op_map, float_ops)

    def _generate_binop_code(self, left, op, right, op_map, float_ops):
        """Helper method to generate binary operation assembly code"""
        code = []

        # Load operands and determine types
        left_type, left_code = self._load_operand(left, "R0")
        right_type, right_code = self._load_operand(right, "R1")

        code.extend([left_code, right_code])

        if op == "^":
            code.extend(self._handle_exponentiation(left_type, right_type))
        else:
            code.extend(self._handle_arithmetic(op, left_type, right_type, op_map, float_ops))

        return "\n".join(filter(None, code))

    def _load_operand(self, operand, register):
        """Helper method to load operands and determine their types"""
        if isinstance(operand, (int, float)):
            return type(operand), f"LD {register} #{operand}"
        elif isinstance(operand, str) and operand in self.symbol_table:
            return (type(self.symbol_table[operand][0]), 
                   f"LD {register} @{operand}")
        return None, ""

    def _handle_exponentiation(self, left_type, right_type):
        """Helper method to handle exponentiation operations"""
        code = []
        if left_type is float or right_type is float:
            if left_type is int:
                code.append("FL.i R0 R0")
            if right_type is int:
                code.append("FL.i R1 R1")
            code.append("EXP.f R2 R0 R1\nST @print R2")
        else:
            code.append("EXP.i R2 R0 R1\nST @print R2")
        return code

    def _handle_arithmetic(self, op, left_type, right_type, op_map, float_ops):
        """Helper method to handle arithmetic operations"""
        code = []
        if left_type is float or right_type is float:
            if left_type is int:
                code.append("FL.i R0 R0")
            if right_type is int:
                code.append("FL.i R1 R1")
            code.append(f"{float_ops[op]} R2 R0 R1\nST @print R2")
        else:
            code.append(f"{op_map[op]} R2 R0 R1\nST @print R2")
        return code

    def p_expression_ne(self, p):
        """expression : expression NE expression"""
        p[0] = self._generate_ne_comparison(p[1], p[3])

    def _generate_ne_comparison(self, left, right):
        """Helper method to generate not-equal comparison assembly code"""
        code = []
        
        # Load operands and determine types
        right_type, right_code = self._load_operand(right, "R0")
        left_type, left_code = self._load_operand(left, "R1")
        
        code.extend([right_code, left_code])
        
        # Convert to float if necessary
        if right_type is int:
            code.append("FL.i R0 R0")
        if left_type is int:
            code.append("FL.i R1 R1")
            
        code.append("NE.f R2 R0 R1\nST @print R2")
        
        return "\n".join(filter(None, code))

    def p_expression_number(self, p):
        """
        expression : INT
                  | REAL
        """
        p[0] = p[1]

    def p_expression_id(self, p):
        """expression : ID"""
        p[0] = p[1]

    def p_expression_list_access(self, p):
        """expression : ID LBRACKET INT RBRACKET"""
        list_name = p[1]
        index = int(p[3])

        p[0] = self._generate_list_access(list_name, index)

    def _generate_list_access(self, list_name, index):
        """Helper method to generate list access assembly code"""
        if list_name not in self.symbol_table or self.symbol_table[list_name]['type'] != 'list':
            print(f"ERROR: '{list_name}' is not a declared list.")
            return "ERROR"

        list_size = self.symbol_table[list_name]['size']
        if index < 0 or index >= list_size:
            print(f"ERROR: Index {index} out of bounds for list '{list_name}' (size {list_size}).")
            return "ERROR"

        return "\n".join([
            f"LD R0 @{list_name}",
            f"LD R1 #{index}",
            f"LD R2 #4",
            f"MUL.i R3 R1 R2",
            f"ADD.i R4 R0 R3",
            f"ST $print R4"
        ])

    def p_error(self, p):
        print("ERROR")

    def process_input(self, input_text):
        """Process a single line of input"""
        try:
            result = self.parser.parse(input_text)
            return str(result) if result else "ERROR"
        except SyntaxError as e:
            return "ERROR"
        except Exception:
            return "ERROR"

    def run_compiler(self):
        """Compile input file to assembly"""
        with open("input.txt", "r") as infile, open("ChocolateLava.asm", "w") as outfile:
            for line in infile:
                line = line.strip()
                if line:
                    result = self.process_input(line)
                    outfile.write(result.strip() + "\n\n")
