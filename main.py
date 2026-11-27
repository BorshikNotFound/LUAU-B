#!/usr/bin/env python3
#
# LUAU:B
# LUAU: BORSHIKIFIED
# BY BorshikNotFound
# https://borshik.is-a.dev/luaub

from PySide6 import QtWidgets, QtGui, QtCore
import random
import os
import sys
import string as streeeng

version = "shik/dev-0.1"

if len(sys.argv) < 2:
    print("No script specified. Use --help for usage.")
    sys.exit(1)

script = os.path.abspath(sys.argv[1])
verbose = ("-v" in sys.argv)

# terminal bs
if sys.argv[1] == "--help" or sys.argv[1] == "/?":
    print(f"""\033[1;31mLuau: Borshikified\033[0m
{__file__}

\033[1mluaub\033[0m <script> <-- Runs <script>
\033[1mluaub\033[0m <script> -v <-- Runs <script>, prints debug data

\033[1mluaub --help\033[0m <-- Opens this menu
\033[1mluaub --version\033[0m <-- Returns Luau:B version""")
    sys.exit(0)
if sys.argv[1] == "--version":
    print(version)
    sys.exit(0)
if not os.path.isfile(script):
    print("\033[1;31mFATAL:\033[0m Invalid script path")
    sys.exit(1)

contents = ""
try:
    with open(script, "r", encoding="utf-8") as file:
        contents = file.read()
except OSError as e:
    print(f"\033[1;31mFATAL:\033[0m failed to read script\n(OSError; {e})")
    sys.exit(1)

keywords = ["if", "end", "then", "while", "self", "function", "break", "continue", "return", "else", "elseif", "for", "do", "in", "local", "and", "or", "not"]
def lexer ():
    result = []

    def getline (n):
        linenumber = 1
        for index in range(len(contents)):
            if index > n:
                break

            if contents[index] == "\n":
                linenumber += 1
        return linenumber

    instring, incomment, escaped, lastescaped = False, False, False, False
    rstring, stringtype, commenttype, last = "", "", "", ""
    divider = [" ", "(", "[", "{", ")", "]", "}", "\n", "\t", ".", ",", ":", ";"]
    x = 0
    while x < len(contents):
        char = contents[x]

        if incomment and commenttype ==  "--":
            if char == "\n":
                incomment = False
                last = char
                lastescaped, escaped = False, False
                x += 1
                continue
            else:
                last = ""
                x += 1
                continue
        if incomment and commenttype == "[[":
            if len(contents) > x + 1:
                if contents[x] == "]" and contents[x+1] == "]":
                    incomment = False
                    last = char
                    lastescaped, escaped = False, False
                    x += 2
                    continue
                else:
                    last = ""
                    x += 1
                    continue
            else:
                print(f"\033[1;31mFATAL:\033[0m Unterminated multiline comment")
                sys.exit(1)

        if not (instring or escaped):
            if len(contents) > x + 3:
                if char == "-" and contents[x+1] == "-" and contents[x+2] == "[" and contents[x+3] == "[":
                    incomment = True
                    commenttype = "[["
                    x += 4
                    continue
        if char == "-" and last == "-" and not (escaped or lastescaped) and not instring:
            incomment = True
            commenttype = "--"
            x += 1
            if result and result[-1] == ["operator", "-"]: result.pop(-1)
            continue

        if not (instring and stringtype == "[[") and char == "\n":
            if instring:
                print(f"\033[1;31mFATAL:\033[0m Unterminated string\n\033[1mLine {getline(x)}\033[0m")
                sys.exit(1)
            lastescaped = escaped
            last, escaped = char, False
            x += 1
            continue
        if char == "\\" and not escaped and not (instring and stringtype == "[["):
            lastescaped = escaped
            last, escaped = char, True
            x += 1
            continue

        if instring:
            if char == stringtype and stringtype != "[[" and not escaped:
                result.append(["string", rstring])
                rstring, stringtype, last = "", "", char
                lastescaped = escaped
                escaped = False
                instring = False
                x += 1
                continue
            if char == "]" and last == char and stringtype == "[[":
                rstring = rstring[:-1]
                if result and result[-1] == ["symbol", "["]: result.pop(-1)
                result.append(["string", rstring])
                rstring, stringtype, last = "", "", char
                lastescaped = escaped
                escaped = False
                instring = False
                x += 1
                continue

            if char == "n" and escaped and stringtype != "[[":
                rstring += "\n"
                last = "n"
                lastescaped = True
                escaped = False
                x += 1
                continue
            if char == "t" and escaped and stringtype != "[[":
                rstring += "\t"
                last = "t"
                lastescaped = True
                escaped = False
                x += 1
                continue

            rstring += char
            last = char
            lastescaped = escaped
            escaped = False
            x += 1
            continue

        if char in ["\"", "'"]:
            if not escaped:
                instring = True
                stringtype = char
                rstring = ""
                x += 1
                continue
        if char == "[" and last == char:
            if not (escaped or lastescaped):
                instring = True
                stringtype = "[["
                rstring = ""
                x += 1
                continue

        tcontinue = False
        if char == "/" and not escaped:
            if x + 1 < len(contents):
                if contents[x+1] == "/":
                    result.append(["operator", "//"])
                    x += 2
                    lastescaped = False
                    last = "/"
                    continue
        for check in ["=", "<", ">", "+", "-", "/", "*"]:
            if char == check and not escaped:
                if x + 1 < len(contents):
                    if contents[x+1] == "=":
                        result.append(["operator", f"{check}="])
                        last = "="
                        x += 2
                        tcontinue = True
                        lastescaped = False
                        continue
                    else:
                        result.append(["operator", check])
                        x += 1
                        tcontinue = True
                        last = check
                        lastescaped = False
                        continue
                else:
                    result.append(["operator", check])
                    x += 1
                    tcontinue = True
                    last = check
                    lastescaped = False
                    continue
        if tcontinue == True: continue
        if char == "~" and not escaped:
            if x + 1 < len(contents):
                if contents[x+1] == "=":
                    result.append(["operator", "~="])
                    last = "="
                    x += 2
                    lastescaped = False
                    continue
        if char == "." and not escaped:
            if x + 2 < len(contents):
                if contents[x+2] == contents[x+1] and contents[x+1] == ".":
                    result.append(["operator", "..."])
                    last = "."
                    x += 3
                    lastescaped = False
                    continue
                elif contents[x+2] == "=" and contents[x+1] == ".":
                    result.append(["operator", "..="])
                    last = "="
                    x += 3
                    lastescaped = False
                    continue
                else:
                    if contents[x+1] == ".":
                        result.append(["operator", ".."])
                        last = "."
                        x += 2
                        lastescaped = False
                        continue
                    else:
                        result.append(["symbol", "."])
                        last = "."
                        x += 1
                        lastescaped = False
                        continue
            else:
                if x + 1 < len(contents):
                    if contents[x+1] == ".":
                        result.append(["operator", ".."])
                        last = "."
                        x += 2
                        lastescaped = False
                        continue
                    else:
                        result.append(["symbol", "."])
                        last = "."
                        x += 1
                        lastescaped = False
                        continue
                else:
                    result.append(["symbol", "."])
                    last = "."
                    x += 1
                    lastescaped = False
                    continue
        tcontinue = False
        for check in ["^", "%", "#", "!"]:
            if char == check and not escaped:
                result.append(["operator", check])
                last = check
                x += 1
                tcontinue = True
                lastescaped = False
                continue
        if tcontinue == True: continue
        tcontinue = False
        for check in ["(", ")", "{", "}", "[", "]", ",", ":", ";"]:
            if char == check and not escaped:
                result.append(["symbol", check])
                last = check
                x += 1
                tcontinue = True
                lastescaped = False
                continue
        if tcontinue == True: continue

        if not escaped:
            tokens = {"true": ["bool", "true"], "True": ["bool", "true"], "false": ["bool", "false"], "False": ["bool", "false"], "nil": ["nil", "nil"]}

            tcontinue = False
            for valuetype, token in tokens.items():
                length = len(valuetype)

                if not len(contents) > x + length - 1: continue

                def check (valuetype, token):
                    nonlocal x, result, lastescaped, last

                    length = len(valuetype)
                    matches = (valuetype == contents[x:x+length])

                    if matches:
                        result.append(token)
                        x += length
                        lastescaped = False
                        last = valuetype[-1]

                    return matches

                if len(contents) > x + length and x != 0:
                    if not contents[x-1] in divider or not contents[x+length] in divider: continue

                    tcontinue = check(valuetype, token)
                if len(contents) > x + length and x == 0:
                    if not contents[x+length] in divider: continue

                    tcontinue = check(valuetype, token)
                if not len(contents) > x + length and x != 0:
                    if not contents[x-1] in divider: continue

                    tcontinue = check(valuetype, token)

            if tcontinue: continue
        if char in [str(n) for n in range(10)] and not escaped:
            candidate, includesexb = "", False
            for l in range(len(contents) - x):
                if not contents[x+l].lower() in ([str(n) for n in range(10)] + ["e", "x", "b", "-"]):
                    if "x" in candidate and contents[x+l].upper() in ([str(n) for n in range(10)] + ["A", "B", "C", "D", "E", "F"]):
                        candidate += contents[x+l].upper()
                        continue
                    break
                if contents[x+l] in ["e", "x", "b"]:
                    if includesexb == True:
                        break
                    else:
                        includesexb = True

                candidate += contents[x+l]

            if not includesexb:
                if "-" in candidate:
                    args = candidate.split("-")

                    result.append(["number", args[0]])
                    x += len(args[0])
                    last = args[0][-1]
                    lastescaped = False
                    continue
                else:
                    result.append(["number", candidate])
                    x += len(candidate)
                    last = candidate[-1]
                    lastescaped = False
                    continue
            else:
                if "e" in candidate:
                    candidate = candidate.lower()
                    args = candidate.split("e")
                    if len(args) != 2 or args[1] == "":
                        print(f"\033[1;31mFATAL:\033[0m Invalid scientific notation format\nExample of the correct format: 12e4\n\033[1mLine {getline(x)}\033[0m")
                        sys.exit(1)
                    try:
                        num = str(float(args[0]) * (10 ** int(args[1])))
                    except:
                        print(f"\033[1;31mFATAL:\033[0m Failed to convert {candidate} to scientific notation.\n\033[1mLine {getline(x)}\033[0m")
                        sys.exit(1)

                    result.append(["number", num])
                    x += len(candidate)
                    last = args[1][-1]
                    lastescaped = False
                    continue

                if len(candidate) > 2:
                    if candidate[0] + candidate[1].lower() == "0x":
                        num = 0

                        try:
                            num = str(int(candidate, 16))
                        except ValueError:
                            print(f"\033[1;31mFATAL:\033[0m Failed to convert {candidate} into Base 16 (Hexadecimals)\n\033[1mLine {getline(x)}\033[0m")
                            sys.exit(1)

                        result.append(["number", num])
                        x += len(candidate)
                        last = candidate[-1]
                        lastescaped = False
                        continue
                    if candidate[0] + candidate[1].lower() == "0b":
                        num = 0

                        try:
                            num = str(int(candidate, 2))
                        except ValueError:
                            print(f"\033[1;31mFATAL:\033[0m Failed to convert {candidate} into Base 2 (Binary)\n\033[1mLine {getline(x)}\033[0m")
                            sys.exit(1)

                        result.append(["number", num])
                        x += len(candidate)
                        last = candidate[-1]
                        lastescaped = False
                        continue
                else:
                    if "b" in candidate:
                        print(f"\033[1;31mFATAL:\033[0m Invalid binary format\nExample of the correct format: 0b11010\n\033[1mLine {getline(x)}\033[0m")
                        sys.exit(1)
                    if "x" in candidate:
                        print(f"\033[1;31mFATAL:\033[0m Invalid base 16 format\nExample of the correct format: 0xA911\n\033[1mLine {getline(x)}\033[0m")
                        sys.exit(1)

        if char in list(streeeng.ascii_letters) + ["_"] and not escaped:
            identifier = ""
            for n in range(len(contents) - x):
                if contents[x+n] in list(streeeng.ascii_letters) + list(streeeng.digits) + ["_"]:
                    identifier += contents[x+n]
                else:
                    break

            if identifier in keywords:
                isidentifier = False
                if len(contents) > x + len(identifier):
                    if contents[x+len(identifier)] == ".": isidentifier = True
                if x != 0:
                    if contents[x-1] == ".": isidentifier = True

                if isidentifier:
                    result.append(["identifier", identifier])
                    lastescaped = False
                    last = identifier[-1]
                    x += len(identifier)
                    continue
                else:
                    result.append(["keyword", identifier])
                    lastescaped = False
                    last = identifier[-1]
                    x += len(identifier)
                    continue
            else:
                result.append(["identifier", identifier])
                lastescaped = False
                last = identifier[-1]
                x += len(identifier)
                continue


        if not char in streeeng.ascii_letters + "01234567890_~*=-+/^#%.(){}[]\n\t:;\"',! ":
            print(f"WARNING: Unknown character {char!r}\n\033[1mLine {getline(x)}\033[0m")

        last, lastescaped = char, escaped
        escaped = False
        x += 1

    if instring:
        print("\033[1;31mFATAL:\033[0m Unterminated string")
        sys.exit(1)
    if result == []:
        print("\033[33mWARNING:\033[0m Empty script")
        return

    if verbose == True: print(f"\033[1mLEXER TOKENS:\033[0m\n\n{result}")
    return result


class nodetype: pass
class number (nodetype):
    def __init__ (self, n):
        self.value = n
class string (nodetype):
    def __init__ (self, s):
        self.value = s
class assignment (nodetype):
    def __init__ (self, type, name, contents):
        self.left = name
        self.right = contents
        self.type = type
class OR (nodetype):
    def __init__ (self, left, right):
        self.left = left
        self.right = right
class AND (nodetype):
    def __init__ (self, left, right):
        self.left = left
        self.right = right
class IFstatement (nodetype):
    def __init__ (self, condition, body):
        self.condition = condition
        self.body = body
class Bexpression (nodetype):
    def __init__ (self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
class varieable (nodetype):
    def __init__ (self, name):
        self.name = name
class functioncall (nodetype):
    def __init__ (self, name, args):
        self.function = name
        self.args = args
class functiondef (nodetype):
    def __init__ (self, name, args, body):
        self.name = name
        self.args = args
        self.body = body
class RETURN (nodetype):
    def __init__ (self, value):
        self.value = value
class memberaccess (nodetype):
    def __init__ (self, obj, child):
        self.object = obj
        self.child = child
class boolean (nodetype):
    def __init__ (self, value):
        self.value = value
class nil:
    pass

def visualiseAST (nodes):
    result = ""
    treesymbol = ["├", "─", "└"]
    depth = 0

    def self (nodes, selfdepth):
        nonlocal result

        for node in nodes:
            if isinstance(node, (nodetype, list)):
                if isinstance(node, (number, string, boolean)):
                    result += ("    "*selfdepth) + f"{treesymbol[2]}{treesymbol[1]} value: '{node.value}'\n"
                if isinstance(node, Bexpression):
                    nl = node.left
                    if isinstance(node.left, (nodetype, list)): nl = f"{type(node.left).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} left: '{nl}'\n"
                    self([node.left], selfdepth+1)
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} operator: '{node.operator}'\n"
                    self([node.operator], selfdepth+1)
                    nr = node.right
                    if isinstance(node.right, (nodetype, list)): nr = f"{type(node.right).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[2]}{treesymbol[1]} right: '{nr}'\n"
                    self([node.right], selfdepth+1)
                if isinstance(node, assignment):
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} type: '{node.type}'\n"
                    nl = node.left
                    if isinstance(node.left, (nodetype, list)): nl = f"{type(node.left).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} left: '{nl}'\n"
                    self([node.left], selfdepth+1)
                    nr = node.right
                    if isinstance(node.right, (nodetype, list)): nr = f"{type(node.right).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[2]}{treesymbol[1]} right: '{nr}'\n"
                    self([node.right], selfdepth+1)
                if isinstance(node, list):
                    for n in node:
                        nt = n
                        if isinstance(n, (nodetype, list)): nt = f"{type(nt).__name__}"
                        if node != [] and n == node[-1]:
                            result += ("    "*selfdepth) + f"{treesymbol[2]}{treesymbol[1]} {nt}\n"
                        else:
                            result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} {nt}\n"
                        self([n], selfdepth+1)
                if isinstance(node, varieable):
                    result += ("    "*selfdepth) + f"{treesymbol[2]}{treesymbol[1]} name: '{node.name}'\n"
                if isinstance(node, functioncall):
                    fun = node.function
                    if isinstance(node.function, (nodetype, list)): fun = f"{type(node.function).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} function: '{fun}'\n"
                    self([node.function], selfdepth+1)
                    args = node.args
                    if isinstance(node.args, (nodetype, list)): args = f"{type(node.args).__name__}"
                    result += ("    "*selfdepth) + f"{treesymbol[0]}{treesymbol[1]} args: '{args}'\n"
                    self([node.args], selfdepth+1)

    for node in nodes:
        result += f"{type(node).__name__}\n"
        self([node], 1)

    return result
def parser (tokens, where):
    result = [] # fun fact: this is called AST (abstract syntax tree)

    def parseexpression (tokens, where):
        while where < len(tokens): #ignorethisloopkthx
            token = tokens[where]
            tokentype, tokenvalue = token[0], token[1]

            if tokentype == "string":
                if len(tokens) > where + 2 and tokens[where+1][0] == "operator" and not tokens[where+1][1] in ["="]:
                    right, nw = parseexpression(tokens, where+2)

                    return Bexpression(string(tokenvalue), tokens[where+1][1], right), nw
                return string(tokenvalue), where+1
            if tokentype == "bool":
                return boolean(tokenvalue), where+1
            if tokentype == "nil":
                return nil(), where+1
            if tokentype == "number":
                num = tokenvalue
                add = 1
                if len(tokens) > where + 2:
                    if tokens[where+1] == ["symbol", "."] and tokens[where+2][0] == "number":
                        num = f"{num}.{tokens[where+2][1]}"
                        add = 3

                if len(tokens) > where + 2 and tokens[where+1][0] == "operator" and not tokens[where+1][1] in ["="]:
                    right, nw = parseexpression(tokens, where+2)

                    return Bexpression(number(num), tokens[where+1][1], right), nw
                return number(num), where + add
            if tokentype == "identifier":
                if len(tokens) > where + 1 and tokens[where+1] == ["symbol", "("]:
                    args = []

                    tmpwhere, x = where + 2, 0
                    expectingargument = True
                    while tmpwhere + x < len(tokens):
                        if tokens[tmpwhere+x] == ["symbol", ","]:
                            if expectingargument and len(args) != 0:
                                print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected argument, got ','\n{tokenvalue}(...,) <-- HERE")
                                sys.exit(1)
                            expectingargument = True
                            x += 1
                            continue

                        if tokens[tmpwhere+x] == ["symbol", ")"]:
                            if expectingargument and len(args) != 0:
                                print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected argument, got ')'\n{tokenvalue}(...,) <-- HERE")
                                sys.exit(1)
                            break

                        argument, nw = parseexpression(tokens, tmpwhere+x)
                        x = nw - tmpwhere
                        args.append(argument)
                        expectingargument = False

                    node = functioncall(varieable(tokenvalue), args)
                    where = tmpwhere + x + 1

                    y = 0
                    while len(tokens) > where + y:
                        if tokens[where+y] == ["symbol", "("]:
                            args = []
                            tmpwhere = where + 2
                            expectingargument = True
                            x = 0
                            while tmpwhere + x < len(tokens):
                                if tokens[tmpwhere+x] == ["symbol", ","]:
                                    if expectingargument and len(args) != 0:
                                        print(f"\033[1;31mFATAL:\033[0m Syntax Error")
                                        sys.exit(1)
                                    expectingargument = True
                                    x += 1
                                    y += 1
                                    continue

                                if tokens[tmpwhere+x] == ["symbol", ")"]:
                                    if expectingargument and len(args) != 0:
                                        print(f"\033[1;31mFATAL:\033[0m Syntax Error")
                                        sys.exit(1)
                                    break

                                argument, nw = parseexpression(tokens, tmpwhere+x)
                                x = nw - tmpwhere
                                args.append(argument)
                                y += x
                                expectingargument = False

                            node = functioncall(node, args)
                            where = tmpwhere + x + 1
                        else:
                            break
                    return node, where
                return varieable(tokenvalue), where+1

            if token == ["symbol", "("]:
                node, nw = parseexpression(tokens, where+1)

                if tokens[nw] != ["symbol", ")"]:
                    print(f"\033[1;31mFATAL:\033[0m Syntax Error\nUnterminated parenthesis, missing ')'")
                    sys.exit(1)
                if nw == where + 2:
                    print(f"\033[1;31mFATAL:\033[0m Syntax Error\nEmpty parenthesis")
                    sys.exit(1)

                return node, nw+1

            print(f"\033[1;31mFATAL:\033[0m Syntax Error\nUnknown token type '{tokentype}' value '{tokenvalue}' (parsing as expression)")
            sys.exit(1)

    while where < len(tokens): #ignorethislooptookthx
        token = tokens[where]
        tokentype, tokenvalue = token[0], token[1]

        if token == ["keyword", "local"]:
            x = 1
            left = []
            expectingargument = True
            newwhere = 0
            while where+x < len(tokens):
                if expectingargument and tokens[where+x] == ["operator", "="]:
                    print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the left side)")
                    sys.exit(1)

                if tokens[where+x] == ["operator", "="]:
                    break

                if tokens[where+x] == ["symbol", ","]:
                    if expectingargument:
                        print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the left side)")
                        sys.exit(1)
                    x += 1
                    expectingargument = True
                    continue

                if expectingargument:
                    arg, nw = parseexpression(tokens, where+x)
                    newwhere = nw
                    left.append(arg)
                    x = nw-where
                    expectingargument = False
                    continue

                if not expectingargument:
                    break

            right = []
            expectingargument = True
            x = 1
            nnewwhere = newwhere
            while newwhere+x < len(tokens):
                if tokens[newwhere+x] == ["operator", "="] and expectingargument:
                    print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the right side)")
                    sys.exit(1)

                if tokens[newwhere+x] == ["symbol", ","]:
                    if expectingargument:
                        print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the right side)")
                        sys.exit(1)
                    x += 1
                    expectingargument = True
                    continue

                if expectingargument:
                    arg, nw = parseexpression(tokens, newwhere+x)
                    nnewwhere = nw
                    right.append(arg)
                    x = nw-newwhere
                    expectingargument = False
                    continue

                if not expectingargument:
                    break

            result.append(assignment("local", left, right))
            where = nnewwhere
            continue
        else:
            if tokentype == "identifier":
                isassignment = False

                x = 0
                expectingargument = True
                while where+x < len(tokens):
                    if tokens[where+x] == ["operator", "="]:
                        isassignment = True
                        break
                    if tokens[where+x] == ["symbol", ","]:
                        if expectingargument:
                            break
                        expectingargument = True
                        x += 1
                        continue

                    if not expectingargument and tokens[where+x][0] != "identifier":
                        break
                    else:
                        x += 1
                        expectingargument = False

                if isassignment:
                    x = 0
                    expectingargument = True
                    left = []
                    newwhere = 0
                    while len(tokens) > where+x:
                        if tokens[where+x] == ["operator", "="]:
                            if expectingargument:
                                print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the left side)")
                                sys.exit(1)
                            break

                        if tokens[where+x] == ["symbol", ","]:
                            if expectingargument:
                                print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the left side)")
                                sys.exit(1)
                            x += 1
                            expectingargument = True
                            continue

                        if expectingargument:
                            arg, nw = parseexpression(tokens, where+x)
                            newwhere = nw
                            left.append(arg)
                            x = nw-where
                            expectingargument = False
                            continue

                        if not expectingargument:
                            break

                    right = []
                    expectingargument = True
                    x = 1
                    nnewwhere = newwhere
                    while newwhere+x < len(tokens):
                        if tokens[newwhere+x] == ["operator", "="] and expectingargument:
                            print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the right side)")
                            sys.exit(1)

                        if tokens[newwhere+x] == ["symbol", ","]:
                            if expectingargument:
                                print(f"\033[1;31mFATAL:\033[0m Syntax Error\nExpected an argument while assigning a value (on the right side)")
                                sys.exit(1)
                            x += 1
                            expectingargument = True
                            continue

                        if expectingargument:
                            arg, nw = parseexpression(tokens, newwhere+x)
                            nnewwhere = nw
                            right.append(arg)
                            x = nw-newwhere
                            expectingargument = False
                            continue

                        if not expectingargument:
                            break

                    result.append(assignment("global", left, right))
                    where = nnewwhere
                    continue
        print(f"\033[1;31mFATAL:\033[0m Syntax Error\nUnknown token type '{tokentype}' value '{tokenvalue}' (parsing as statement)")
        sys.exit(1)

    if len(result) == 0:
        print("\033[33mWARNING:\033[0m Parser returned nothing (empty list)")
        return
    if verbose == True: print(f"\n\033[1mPARSER NODES:\033[0m\n\n{visualiseAST(result)}")
    return result, None


# RUNTIME STARTS HERE

tokens = lexer()
nodes = parser(tokens, 0)[0]

#
