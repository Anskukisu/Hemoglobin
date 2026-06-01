# Compiler for Hemoglobin (.hmg)
# Imports
from comperrors import error
# Tokenizer
OP_TOKENS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "+": "PLUS",
    "-": "MINUS",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD",
    "&": "AND",
    "|": "OR",
    "^": "XOR",
    "!": "NOT",
    ":": "COLON",
    ".": "DOT",
    ",": "COMMA",
    "[": "SOLIDLPAREN",
    "]": "SOLIDRPAREN",
    "{": "CURLYLPAREN",
    "}": "CURLYRPAREN",
    "<": "LESSTHAN",
    ">": "GREATERTHAN",
    "=": "SET"
}
class Token:
    def __init__(self, type_, value=None):
        self.kind = type_
        self.value = value
        if self.value is not None:
            self.me = (self.kind, self.value)
        else:
            self.me = (self.kind)
        
#    def __repr__(self, formal=False):
#        if formal:
#            if self.value is not None:
#                return f"Token [{self.kind}, {self.value}]"
#            else:
#                return f"Token [{self.kind}]"
#        else:
#            if self.value is not None:
#                return (self.kind, self.value)
#            else:
#                return (self.kind)
def peek(line, pos, offset=1):
    if pos + offset < len(line):
        return line[pos + offset]
    return None
def tokenize(line, EOF, line_i):
    cursor = 0
    length = len(line)
    tokens = []
    while cursor < length:
        c = line[cursor]
        # Handle blanks
        if c in (" ", "\n"):
            cursor += 1
            continue
        # Handle comments
        if c == "#":
            while cursor < length and line[cursor] != "\n":
                cursor += 1
            continue
        # Handle macros
        if c == "@":
            macro = ""
            cursor += 1
            while cursor < length and (line[cursor].isalnum() or line[cursor] == '_'):
                    macro += line[cursor]
                    cursor += 1
            tokens.append(Token('MACRO', macro))
            continue
        # Handle strings
        if c == '"' or c == "'":
            quote = c
            string = ""
            cursor += 1
            while cursor < length:
                current = line[cursor]
                if current == "\\":
                    next_c = peek(line, cursor)
                    string += next_c
                    cursor += 2
                    continue
                if current == quote:
                    cursor += 1
                    break
                string += current
                cursor += 1
            tokens.append(Token("STR", string))
            continue
        # Handle multichar logical ops
        if c == "*" and peek(line, cursor) == "*":
            tokens.append(Token("OP", "POW"))
            cursor += 2
            continue
        if c == "/" and peek(line, cursor) == "/":
            tokens.append(Token("OP", "FDIV"))
            cursor += 2
            continue
        if c == "=" and peek(line, cursor) == "=":
            tokens.append(Token("OP", "EQUAL"))
            cursor += 2
            continue
        if c == "+" and peek(line, cursor) == "=":
            tokens.append(Token("OP", "ADDTO"))
            cursor += 2
            continue
        if c == "-" and peek(line, cursor) == "=":
            tokens.append(Token("OP", "SUBTO"))
            cursor += 2
            continue
        if c == "*" and peek(line, cursor) == "=":
            tokens.append(Token("OP", "MULTO"))
            cursor += 2
            continue
        if c == "/" and peek(line, cursor) == "=":
            tokens.append(Token("OP", "DIVTO"))
            cursor += 2
            continue
        # Handle keywords & identifiers
        if c.isalpha() or c == "_":
            word = ""
            while cursor < length and (line[cursor] in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890_"):
                word += line[cursor]
                cursor += 1
            keywords = {"num", "str", "lst", "arr", "while", "if", "else", "repeat", "def"}
            if word in keywords:
                tokens.append(Token('KEYWORD', word))
            else:
                tokens.append(Token('IDENTIFIER', word))
            continue
        # Handle numbers
        if c in "0123456789":
            num = ""
            f = False
            floatErr = False
            while cursor < length and (line[cursor] in "0123456789" or line[cursor] == "."):
                if line[cursor] == "." and not f:
                    f = True
                elif f and line[cursor] == ".":
                    floatErr = True
                num += line[cursor]
                cursor += 1
            if floatErr:
                error(line_i, cursor, "Syntax", f"Float ({num})can have a maximum of 1 decimal point")
            val = float(num)
            tokens.append(Token("NUMBER", val))
            continue
        # Handle single ops
        if c in "+-*/%&|^!:.,()[]{}<>=":
            tokens.append(Token("OP", OP_TOKENS[c]))
            cursor += 1
            continue
        # Errors
        error(line_i, cursor, "Syntax", f"Token ({c}) not recognized")
    if EOF:
        tokens.append(Token("EOF"))
    else:
        tokens.append(Token("EOL"))
    return tokens
# Parser
def parse(tokens):
    # Get token lines
    lines = []
    types = []
    current = []
    typecurrent = []
    token = -1
    while token < len(tokens) - 1:
        token += 1
        val = tokens[token].me
        current.append(val)
        typecurrent.append(val[0])
        if (val == ("EOL") or val == ("EOF")) and current != []:
            lines.append(current)
            types.append(typecurrent)
            current = []
            typecurrent = []
    # Parse lines
    parsed = []
    for i in range(len(lines)):
        line = lines[i]
        kind = types[i]
        # Handle macros
        if kind[0] == "MACRO":
            parsed.append(f"MACRO|{line[0][1]}")
            continue
        # Handle assigning
        if kind[0] == "KEYWORD":
            if line[0][1] == "num":
                parse = f"CREATENUM|{line[1]}|{line[2]}"
                j = 2
                while j < len(line) - 1:
                    parse += f"|{line[j]}"
                    j += 1
                parsed.append(parse)
            elif line[0][1] == "str":
                parse = f"CREATESTR|{line[1]}|{line[2]}"
                j = 2
                while j < len(line) - 1:
                    parse += f"|{line[j]}"
                    j += 1
                parsed.append(parse)
            elif line[0][1] == "lst":
                parse = f"CREATELST|{line[1]}|{line[2]}"
                j = 2
                while j < len(line) - 1:
                    parse += f"|{line[j]}"
                    j += 1
                parsed.append(parse)
            elif line[0][1] == "arr":
                parse = f"CREATEARR|{line[1]}|{line[2]}"
                j = 2
                while j < len(line) - 1:
                    parse += f"|{line[j]}"
                    j += 1
                parsed.append(parse)
            else:
                block_type = line[0][1].upper()
                condition_parts = [str(t[1]) for t in line[1:-1] if isinstance(t, tuple)]
                condition_str = " ".join(condition_parts).replace(" :", "")
                parsed.append(f"KEYWORD|{block_type}|{condition_str}")
            continue
        # Handle identifiers
        if kind[0] == "IDENTIFIER":
            name = line[0][1]
            args = []
            for arg in line[1:]:
                if arg not in ("EOL", "EOF"):
                    args.append(arg)
            parsed.append(f"IDENT|{name}|{"|".join(map(str, args))}")
            continue
    return parsed
# AST builder
class Node:
    #def __repr__():
    #    return f"{self.__class__.__name__}({str(self.__dict__)})"
    def txt(self):
        return ""
class Macro(Node):
    def __init__(self, name):
        self.name = name
    def txt(self):
        return f"AST_MACRO|{self.name}"
class VarDecl(Node):
    def __init__(self, var_type, name, assignment_tokens):
        self.type = var_type   
        self.name = name              
        self.tokens = assignment_tokens  
    def txt(self):
        clean_tokens = []
        for t in self.tokens:
            if isinstance(t, tuple):
                clean_tokens.append(f"{t[0]}:{t[1]}")
            else:
                clean_tokens.append(str(t))
        return f"AST_VAR|{self.type}|{self.name}|{'|'.join(clean_tokens)}"
class KeyWord(Node):
    def __init__(self, block_type, condition_str):
        self.type = block_type       
        self.condition = condition_str
    def txt(self):
        return f"AST_KEYWORD|{self.type}|{self.condition}"
class Identifier(Node):
    def __init__(self, name, arg_tokens):
        self.name = name              
        self.args = arg_tokens    
    def txt(self):
        clean_args = []
        for a in self.args:
            if isinstance(a, tuple):
                clean_args.append(f"{a[0]}:{a[1]}")
            else:
                clean_args.append(str(a))
        return f"AST_IDENT|{self.name}|{'|'.join(clean_args)}"    
def get_ast(parsed):
    tree = []
    for line in parsed:
        if not line.strip():
            continue
        parts = line.split("|")
        cmd = parts[0]
        if cmd == "MACRO":
            if len(parts) > 2:
                error(None, None, "Syntax", "Macro has too many arguments")
            tree.append(Macro(parts[1]).txt())
        elif cmd in ("CREATENUM", "CREATESTR", "CREATELST", "CREATEARR"):
            var_type = cmd.replace("CREATE", "")
            if parts[1].startswith("(") and parts[1].endswith(")"):
                if "'" in parts[1]:
                    p = parts[1].split("'")
                    if len(p) >= 4:
                        var_name = p[3]
                else:
                    p = parts[1].split(",")
                    if len(p) >= 2:
                        var_name = p[1].replace(")", "").strip()
            else:
                var_name = parts[1]
            args = parts[2:]
            tree.append(VarDecl(var_type, var_name, args).txt())
        elif cmd == "KEYWORD":
            block_type = parts[1]
            condition = parts[2] if len(parts) > 2 else ""
            tree.append(KeyWord(block_type, condition).txt())
        elif cmd == "IDENT":
            func_name = parts[1]
            raw_args = parts[2:]
            tree.append(Identifier(func_name, raw_args).txt())
    return tree
# Compiler
def comp(filename):
    file = None
    with open(filename, 'r') as f:
        file = f.readlines()
    tokens = []
    for i, line in enumerate(file):
        tokens += tokenize(line, i == len(file) - 1, i)
    parsed = parse(tokens)
    AST = get_ast(parsed)
    return AST
