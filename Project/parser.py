from scanner import Scanner
from Project.strings_with_arrows import *
import csv

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
##########################################
##########################################

class Error:
		def __init__(self, pos_start, pos_end, error_name, details):
				self.pos_start = pos_start
				self.pos_end = pos_end
				self.error_name = error_name
				self.details = details
		
		def as_string(self):
				result  = f'{self.error_name}: {self.details}\n'
				result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
				result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
				return result

class IllegalCharError(Error):
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
		def __init__(self, pos_start, pos_end, details=''):
				super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
                        

#######################################
# POSITION
#######################################

class Position:
		def __init__(self, idx, ln, col, fn, ftxt):
				self.idx = idx
				self.ln = ln
				self.col = col
				self.fn = fn
				self.ftxt = ftxt

		def advance(self, current_char=None):
				self.idx += 1
				self.col += 1

				if current_char == '\n':
						self.ln += 1
						self.col = 0

				return self

		def copy(self):
				return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)
            
            
##########################################
##########################################

class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'
    

class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'({self.left} {self.op} {self.right})'
    

class VarNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

class AssignmentNode:
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr

    def __repr__(self):
        return f"({self.var_name}={self.expr})"
    
##########################################
##########################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

##########################################
##########################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = 0
        self.current_tok = self.tokens[self.tok_index]
        # self.advance()

    def advance(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_tok = self.tokens[self.tok_index]
        return self.current_tok
    
    ##########################################

    def parse(self):
        res = self.expr()
        if res.error:
            return res.failure(f"SyntaxError at line {self.current_tok.pos_start}, pos {self.current_tok.pos_end}")
        return res
    
    def factor(self):
        res = ParseResult()
        token = self.current_tok

        if token.token == "INT" or token.token == "REAL":
            res.register(self.advance())
            return res.success(NumberNode(token))
        
        if token.token == "VAR":
            res.register(self.advance())
            return res.success(VarNode(token))

        if token.token == "LPAREN":
            res.register(self.advance())
            expr = self.expr()
            if res.error:
                return res.failure(f"SyntaxError at line {self.current_tok.pos_start}, pos {self.current_tok.pos_end}")
            if self.current_tok.token != "RPAREN":
                return res.failure(f"SyntaxError at line {self.current_tok.pos_start}, pos {self.current_tok.pos_end}")
            res.register(self.advance())
            return res.success(expr)

        return res.failure(f"Invalid syntax at {token.pos_start}, {token.pos_end}")

    def term(self):
        return self.bin_op(self.factor, ("*", "/"))

    def expr(self):
        return self.bin_op(self.term, ("+", "-"))
    
    def assignment(self):
        res = ParseResult()
        if self.current_tok.token == "VAR":
            var_name = self.current_tok
            res.register(self.advance())
            if self.current_tok.token == "ASSIGN":
                res.register(self.advance())
                expr = res.register(self.expr())
                if res.error: return res
                return res.success(AssignmentNode(var_name, expr))
        return res.failure(f"Invalid assignment at {self.current_tok.pos_start}")
    
    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.token in ops:
            op = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op, right)

        return res.success(left)

##########################################
##########################################

def run(fn, text):
    lexer = Scanner(text)
    tokens = lexer.scan()
    
    print("Tokens:", tokens)

    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node

def process_file():
    with open("input.txt", "r") as f:
        lines = f.readlines()
    
    with open("output.tok", "w") as f:
        for line in lines:
            scanner = Scanner(line)
            tokens = scanner.scan()
            f.write(str(scanner) + "\n")
            print("\ntokens: ", tokens)

            parser = Parser(tokens)
            ast = parser.parse()

            print("parser: ", ast.node)
            
    #grammar
    # with open("output.lex", "w") as f:
    #     for value, regex in scanner.token_list.items():
    #         f.write(f"{value}: {regex}\n")
            
if __name__ == "__main__":
    process_file()