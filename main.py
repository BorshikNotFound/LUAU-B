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
import string

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


def lexer ():
    keywords = ["if", "end", "then", "while", "self", "function", "break", "continue", "return", "else", "elseif", "for", "do", "in", "local", "and", "or", "not"]

    result = []

    def getline (n):
        linenumber = 0
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
            result.append(["newline", "newline"])
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
                        print(f"\033[1;31mFATAL:\033[0m Invalid scientific notation format\nExample of the correct format: 12e4\n\033[1mLine {getline()}\033[0m")
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
                            print(f"\033[1;31mFATAL:\033[0m Failed to convert {candidate} into Base 2 (Binary)\n\033[1mLine {getline()}\033[0m")
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

        if char in list(string.ascii_letters) + ["_"] and not escaped:
            identifier = ""
            for n in range(len(contents) - x):
                if contents[x+n] in list(string.ascii_letters) + list(string.digits) + ["_"]:
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


        if not char in string.ascii_letters + "01234567890_~*=-+/^#%.(){}[]\n\t:;\"',! ":
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


lexer() # <-- temporary
