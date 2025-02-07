# main.py
from scanner import *
from parser import *
from compiler import *

def main():
    scanner = Scanner()
    scanner.run_scanner()
    parser = Parser()
    parser.run_parser()
    compiler = Compiler()
    compiler.run_compiler()

if __name__ == "__main__":
    main()