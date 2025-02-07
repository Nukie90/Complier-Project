# main.py
from scanner import run as run_scanner
from parser import run as run_parser
from compiler import run as run_compiler

def main():
    run_scanner()
    run_parser()
    run_compiler()

if __name__ == "__main__":
    main()