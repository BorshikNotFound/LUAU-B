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
    pass
