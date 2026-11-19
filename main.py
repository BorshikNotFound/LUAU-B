# LUAU:B
# LUAU: BORSHIKIFIED
# BY BorshikNotFound
# https://borshik.is-a.dev/luaub

from PySide6 import QtWidgets, QtGui, QtCore
import random
import os
import sys

version = "shik/dev-0.0"

if len(sys.argv) < 2:
    print("No script specified. Use --help for usage.")
    sys.exit(1)

script = os.path.abspath(sys.argv[1])

# terminal bs
if sys.argv[1] == "--help" or sys.argv[1] == "/?":
    print(f"""\033[1;31mLuau: Borshikified\033[0m
{__file__}

\033[1mluaub\033[0m <script> <-- Runs <script>

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

    instring, incomment, escaped, lastescaped = False, False, False, False
    rstring, stringtype, last = "", "", ""
    x = 0
    while x < len(contents):
        char = contents[x]

        if incomment:
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

        if char == "-" and last == "-" and not (escaped or lastescaped) and not instring:
            incomment = True
            x += 1
            continue
        if not (instring and stringtype == "[[") and char == "\n":
            if instring:
                print(f"\033[1;31mFATAL:\033[0m Unterminated string")
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
                rstring = rstring.replace("\\n", "\n").replace("\\t", "\t")
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
                    continue
        for check in ["=", "<", ">", "+", "-", "/", "*"]:
            if char == check and not escaped:
                if x + 1 < len(contents):
                    if contents[x+1] == "=":
                        result.append(["operator", f"{check}="])
                        x += 2
                        tcontinue = True
                        continue
                    else:
                        result.append(["operator", check])
                        x += 1
                        tcontinue = True
                        continue
                else:
                    result.append(["operator", check])
                    x += 1
                    tcontinue = True
                    continue
        if tcontinue == True: continue
        if char == "~" and not escaped:
            if x + 1 < len(contents):
                if contents[x+1] == "=":
                    result.append(["operator", "~="])
                    x += 2
                    continue
        if char == "." and not escaped:
            if x + 2 < len(contents):
                if contents[x+2] == contents[x+1] and contents[x+1] == ".":
                    result.append(["operator", "..."])
                    x += 3
                    continue
                elif contents[x+2] == "=" and contents[x+1] == ".":
                    result.append(["operator", "..="])
                    x += 3
                    continue
                else:
                    if contents[x+1] == ".":
                        result.append(["operator", ".."])
                        x += 2
                        continue
                    else:
                        result.append(["symbol", "."])
                        x += 1
                        continue
            else:
                if x + 1 < len(contents):
                    if contents[x+1] == ".":
                        result.append(["operator", ".."])
                        x += 2
                        continue
                    else:
                        result.append(["symbol", "."])
                        x += 1
                        continue
                else:
                    result.append(["symbol", "."])
                    x += 1
                    continue
        tcontinue = False
        for check in ["^", "%"]:
            if char == check and not escaped:
                result.append(["operator", check])
                x += 1
                tcontinue = True
                continue
        if tcontinue == True: continue
        tcontinue = False
        for check in ["(", ")", "{", "}", "[", "]", ",", ":", ";"]:
            if char == check and not escaped:
                result.append(["symbol", check])
                last = check
                x += 1
                tcontinue = True
                continue
        if tcontinue == True: continue

        last, lastescaped = char, escaped
        escaped = False
        x += 1

    if instring:
        print("\033[1;31mFATAL:\033[0m Unterminated string")
        sys.exit(1)
    if result == []:
        print("\033[33mWARN:\033[0m Empty script")
        return
    return result
print(lexer())
