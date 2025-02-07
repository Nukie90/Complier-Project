import ply.lex as lex
import ply.yacc as yacc
import csv

class Parser:
    tokens = (
        "REAL", "INT", "VAR", "ASSIGN",
        "ADD", "SUB", "MUL", "DIV", "IDIV", "POW",
        "LT", "LE", "GT", "GE", "EQ", "NE",
        "LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
        "LIST", "DIV_ASSIGN", "ERROR"
    )

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
    t_ignore = " \t"

    precedence = (
        ('left', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'IDIV'),
        ('right', 'POW'),
    )

    def __init__(self):
        self.current_line = 0
        self.symbol_table = {}
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def t_VAR(self, t):
        r"[a-zA-Z][a-zA-Z0-9_]*"
        if t.value == "list":
            t.type = "LIST"
        return t

    def t_ERROR(self, t):
        r"[^\s\w\.\+\-\*/=<>!()\[\]^]"
        raise Exception(f"SyntaxError at line {self.current_line}, pos {t.lexpos + 1}")

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise Exception(f"SyntaxError at line {self.current_line}, pos {t.lexpos + 1}")

    def p_program(self, p):
        """program : statement
                  | expression"""
        p[0] = p[1]

    def p_statement_assign(self, p):
        "statement : VAR ASSIGN expression"
        self.symbol_table[p[1]] = {
            "lexeme": p[1],
            "line_number": self.current_line,
            "start_pos": p.lexpos(1) + 1,
            "length": len(p[1]),
            "type": "VAR",
            "value": p[3]
        }
        p[0] = f"({p[1]}={p[3]})"

    def p_statement_list_assign(self, p):
        "statement : VAR ASSIGN LIST LBRACKET expression RBRACKET"
        self.symbol_table[p[1]] = {
            "lexeme": p[1],
            "line_number": self.current_line,
            "start_pos": p.lexpos(1) + 1,
            "length": len(p[1]),
            "type": "LIST",
            "value": "ARRAY"
        }
        p[0] = f"({p[1]} = (list[({p[5]})]))"

    def p_expression_operation(self, p):
        """expression : expression ADD expression
                     | expression SUB expression
                     | expression MUL expression
                     | expression DIV expression
                     | expression POW expression
                     | expression LT expression
                     | expression LE expression
                     | expression GT expression
                     | expression GE expression
                     | expression EQ expression
                     | expression NE expression"""
        if p[2] == '^':
            p[0] = f"({p[1]}**{p[3]})"
        else:
            p[0] = f"({p[1]}{p[2]}{p[3]})"

    def p_expression_group(self, p):
        "expression : LPAREN expression RPAREN"
        if p[2].startswith('(') and p[2].endswith(')'):
            p[0] = p[2]
        else:
            p[0] = f"({p[2]})"

    def p_expression_var(self, p):
        "expression : VAR"
        if p[1] not in self.symbol_table:
            raise Exception(f"Undefined variable {p[1]} at line {self.current_line}, pos {p.lexpos(1) + 1}")
        p[0] = p[1]

    def p_expression_number(self, p):
        """expression : INT
                     | REAL"""
        p[0] = p[1]

    def p_expression_list_access(self, p):
        "expression : VAR LBRACKET expression RBRACKET"
        if p[1] not in self.symbol_table:
            raise Exception(f"Undefined variable {p[1]} at line {self.current_line}, pos {p.lexpos(1) + 1}")
        p[0] = f"({p[1]}[({p[3]})])"

    def p_error(self, p):
        if p:
            raise Exception(f"SyntaxError at line {self.current_line}, pos {p.lexpos + 1}")
        else:
            raise Exception("Syntax error at EOF")

    def process_input(self, input_text, line_num):
        """Process a single line of input"""
        self.current_line = line_num
        try:
            self.lexer.lineno = line_num
            result = self.parser.parse(input_text)
            return result
        except Exception as e:
            return str(e)

    def process_input_files(self, input_file="input.txt", output_file="ChocolateLava.bracket", symbol_table_file="ChocolateLava.csv"):
        """Process input files and generate output files"""
        # Process input file and write output
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            lines = infile.readlines()
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line:
                    result = self.process_input(line, i)
                    outfile.write(f"{result}\n")

        # Write symbol table to CSV
        with open(symbol_table_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, 
                                  fieldnames=["lexeme", "line_number", "start_pos", "length", "type", "value"])
            writer.writeheader()
            for lexeme, entry in self.symbol_table.items():
                writer.writerow(entry)

    def write_grammar(self, output_file="ChocolateLava.grammar"):
        """Write grammar rules to file"""
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

        with open(output_file, "w") as outfile:
            for rule in grammar_rules:
                outfile.write(f"{rule}\n")

    def run_parser(self):
        """Run the complete parsing process"""
        self.process_input_files()
        self.write_grammar()
