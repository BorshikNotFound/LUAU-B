# FUN FACT:
# .shik stands for Sorshik Horshik Iorshik Korshik (probably)

from PySide6 import QtWidgets, QtGui, QtCore
import os


scripts = []
current = -1
previewpath = os.path.join(os.path.dirname(os.path.dirname(__file__)),"preview.shik")
if os.path.exists(previewpath):
    scripts.append(previewpath)
    current = 0


QtWidgets.QApplication.setStyle("Fusion")

scriptfont, scriptfontsize = {"8": QtGui.QFont("JetBrainsMono-Regular", 8), "12": QtGui.QFont("JetBrainsMono-Regular", 12), "16": QtGui.QFont("JetBrainsMono-Regular", 16), "32": QtGui.QFont("JetBrainsMono-Regular", 32), "48": QtGui.QFont("JetBrainsMono-Regular", 48), "64": QtGui.QFont("JetBrainsMono-Regular", 64)}, 12
font = {"5": QtGui.QFont("Inconsolata", 8), "15": QtGui.QFont("Inconsolata", 15)}

app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
window.setMinimumSize(800, 600)
holder = QtWidgets.QWidget()
holder.setStyleSheet("background-color: #212122")
window.setCentralWidget(holder)

window.setWindowTitle("shik.writer")
window.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "logo.png")))

holdervlayout = QtWidgets.QVBoxLayout(holder)
topbar = QtWidgets.QWidget()
contentsholder = QtWidgets.QWidget()
topbar.setFixedHeight(30)
holdervlayout.addWidget(topbar)
holdervlayout.addWidget(contentsholder)
topbar.setStyleSheet("border-bottom: 2px solid #404040")
holdervlayout.setSpacing(0)
holdervlayout.setContentsMargins(0, 0, 0, 0)

contentshlayout = QtWidgets.QHBoxLayout(contentsholder)
editor = QtWidgets.QPlainTextEdit()
scriptslist = QtWidgets.QWidget()
editor.setStyleSheet("background-color: #151516; color: #ffffff;")
scriptslist.setStyleSheet(f"border-right: 1px solid #393939")
contentshlayout.addWidget(scriptslist, 1)
contentshlayout.addWidget(editor, 2)
scriptslist.setMaximumWidth(400)
contentshlayout.setContentsMargins(0, 0, 0, 0)
contentshlayout.setSpacing(0)
editor.setFont(scriptfont[str(scriptfontsize)])

class shikhighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, contents):
        super().__init__(contents)

    def highlightBlock(self, text):
        keywords = ["if", "end", "then", "while", "self", "function", "break", "continue", "return", "else", "elseif", "for", "do", "in", "local", "and", "or", "not"]

        functions = ["print", "warn", "error", "pairs", "wait"]

        keywordfmt = QtGui.QTextCharFormat()
        keywordfmt.setForeground(QtGui.QColor("#ff6969"))
        keywordfmt.setFontWeight(QtGui.QFont.Weight.Bold)

        functionfmt = QtGui.QTextCharFormat()
        functionfmt.setForeground(QtGui.QColor("#74a7f2"))
        functionfmt.setFontWeight(QtGui.QFont.Weight.Bold)

        ufunctionfmt = QtGui.QTextCharFormat()
        ufunctionfmt.setForeground(QtGui.QColor("#e6e08c"))
        ufunctionfmt.setFontWeight(QtGui.QFont.Weight.Normal)

        pathfmt = QtGui.QTextCharFormat()
        pathfmt.setForeground(QtGui.QColor("#8cdcfa"))
        pathfmt.setFontWeight(QtGui.QFont.Weight.Normal)

        valuesfmt = QtGui.QTextCharFormat()
        valuesfmt.setForeground(QtGui.QColor("#fcba49"))
        valuesfmt.setFontWeight(QtGui.QFont.Weight.Bold)

        stringfmt = QtGui.QTextCharFormat()
        stringfmt.setForeground(QtGui.QColor("#63db6f"))
        stringfmt.setFontWeight(QtGui.QFont.Weight.Normal)

        commentfmt = QtGui.QTextCharFormat()
        commentfmt.setForeground(QtGui.QColor("#757575"))
        commentfmt.setFontWeight(QtGui.QFont.Weight.Normal)

        # keywords and (built in) functions
        i = 0
        while i < len(text):
            if text[i].isalpha() or text[i] == "_":
                start = i
                while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                    i += 1

                word = text[start:i]
                length = i - start

                if word in keywords:
                    self.setFormat(start, length, keywordfmt)
                elif word in functions:
                    self.setFormat(start, length, functionfmt)
            else:
                i += 1

        # user functions
        i = 0
        while i < len(text):
            if text[i].isalpha() or text[i] == "_":
                start = i

                while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                    i += 1

                word = text[start:i]

                check = i
                while check < len(text) and text[check].isspace():
                    check += 1

                if check < len(text) and text[check] == "(":
                    if word not in keywords and word not in functions:
                        self.setFormat(start, i - start, ufunctionfmt)
            else:
                i += 1

        # paths
        i = 0
        while i < len(text):
            if text[i].isalpha() or text[i] == "_":
                start = i

                while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                    i += 1

                # check for a dotted path
                if i < len(text) and text[i] == ".":
                    end = i

                    while end < len(text) and text[end] == ".":
                        end += 1

                        while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                            end += 1

                    self.setFormat(start, end - start, pathfmt)
            else:
                i += 1

        # values
        i = 0
        while i < len(text):
            if text[i].isdigit():
                start = i

                while i < len(text) and (text[i].isdigit() or text[i] == "."):
                    i += 1

                if i < len(text) and text[i] in "eE":
                    i += 1

                    if i < len(text) and text[i] in "+-":
                        i += 1

                    while i < len(text) and text[i].isdigit():
                        i += 1

                self.setFormat(start, i - start, valuesfmt)

            elif text[i].isalpha():
                start = i

                while i < len(text) and text[i].isalpha():
                    i += 1

                word = text[start:i]

                if word == "true" or word == "false":
                    self.setFormat(start, i - start, valuesfmt)
            else:
                i += 1

        # strings
        i = 0
        while i < len(text):
            if text[i] == '"' or text[i] == "'":
                quote = text[i]
                start = i
                i += 1

                while i < len(text):
                    if text[i] == "\\":
                        i += 2
                        continue
                    if text[i] == quote:
                        i += 1
                        break
                    i += 1

                self.setFormat(start, i - start, stringfmt)
            else:
                i += 1

        # comments
        commentstart = text.find("--")
        if commentstart != -1:
            self.setFormat(commentstart, len(text) - commentstart, commentfmt)
highlighter = shikhighlighter(editor.document())

tblayout = QtWidgets.QHBoxLayout(topbar)
openbutton = QtWidgets.QPushButton("Open (CTRL+O)")
savebutton = QtWidgets.QPushButton("Save (CTRL+S)")
newbutton = QtWidgets.QPushButton("New (CTRL+N)")
tblayout.addWidget(newbutton)
tblayout.addWidget(openbutton)
tblayout.addWidget(savebutton)
tblayout.setContentsMargins(10, 0, 0, 0)
openbutton.setStyleSheet("background: none; border: none; color: #cccccc; text-align: left")
openbutton.setFont(font["15"])
openbutton.setMaximumWidth(len("Open (CTRL+O)")*10)
savebutton.setStyleSheet("background: none; border: none; color: #cccccc; text-align: left")
savebutton.setFont(font["15"])
savebutton.setMaximumWidth(len("Save (CTRL+S)")*10)
newbutton.setStyleSheet("background: none; border: none; color: #cccccc; text-align: left")
newbutton.setFont(font["15"])
newbutton.setMaximumWidth(len("New (CTRL+N)")*10)
spacer1 = QtWidgets.QWidget()
spacer1.setStyleSheet("background: none; border: none")
tblayout.addWidget(spacer1, 1)
tblayout.setSpacing(20)


scriptsvlayoutL = QtWidgets.QVBoxLayout(scriptslist)
scriptsarea = QtWidgets.QScrollArea(scriptslist)
scriptscontents = QtWidgets.QWidget()
scriptsarea.setStyleSheet("background: #212122; border: none")
scriptsarea.setWidget(scriptscontents)
scriptsarea.setWidgetResizable(True)
scriptsarea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
scriptscontents.setStyleSheet("background: none; border: none")
scriptsvlayout = QtWidgets.QVBoxLayout(scriptscontents)
scriptsvlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
scriptsvlayoutL.addWidget(scriptsarea)
scriptsarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scriptsarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

class scriptstemplate (QtWidgets.QWidget):
    closing = QtCore.Signal()

    def __init__ (self, path):
        super().__init__()

        scriptsvlayout.addWidget(self)

        self.parent = QtWidgets.QLabel()
        self.name = QtWidgets.QLabel()
        self.closebutton = QtWidgets.QPushButton()
        self.path = path

        def ihavenoideawhatdoinamethefunctionsoherewegopneumonoultramicroscopicsilicovolcanoconiosis ():
            global current

            where = None
            try:
                where = scripts.index(path)
            except:
                print(f"\033[31mERROR:\033[0m shik.writer failed to remove {path}.")
                return

            scripts.pop(where)

            if where == current:
                editor.setPlainText("-- no script selected")
                current = -1
            elif where < current:
                current -= 1

            scriptsvlayout.removeWidget(self)
            self.deleteLater()
        self.closebutton.clicked.connect(ihavenoideawhatdoinamethefunctionsoherewegopneumonoultramicroscopicsilicovolcanoconiosis)

        self.setStyleSheet("QWidget {background: none; border: none}")
        self.setFixedHeight(75)

        self.selfhlayout = QtWidgets.QHBoxLayout(self)
        self.namecontainer = QtWidgets.QWidget()
        self.namecontainerlayout = QtWidgets.QVBoxLayout(self.namecontainer)
        self.selfhlayout.addWidget(self.namecontainer, 1)
        self.selfhlayout.addWidget(self.closebutton)
        self.namecontainerlayout.addWidget(self.parent)
        self.namecontainerlayout.addWidget(self.name, 1)

        self.name.setFont(font["15"])
        self.name.setStyleSheet("color: white; background: none")
        self.name.setMinimumHeight(20)
        self.parent.setFont(font["5"])
        self.parent.setStyleSheet("color: #999999; background: none")
        self.parent.setMinimumHeight(10)
        self.closebutton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "close.png")))
        self.closebutton.setIconSize(QtCore.QSize(30, 30))
        self.closebutton.setFixedSize(30, 30)
        self.closebutton.setStyleSheet("background: none; border: none")

        self.name.setText(os.path.basename(path))
        self.parent.setText(os.path.dirname(path))

    def mousePressEvent(self, event):
        global current

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            try:
                with open(self.path, "r", encoding="utf-8") as script:
                    contents = script.read()
            except:
                print(f"\033[31mERROR:\033[0m shik.writer failed to load the script")
                return

            current = scripts.index(self.path)
            editor.setPlainText(contents)

templates = []
def updatescripts():
    global templates

    while scriptsvlayout.count():
        item = scriptsvlayout.takeAt(0)
        widget = item.widget()

        if widget: widget.deleteLater()

    templates = []
    for script in scripts:
        if os.path.exists(script):
            template = scriptstemplate(script)
            templates.append(template)
        else:
            print(f"\033[31mERROR:\033[0m failed to load {script}.")
updatescripts()

saveshortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), window)
def savescript():
    if current < 0 or current >= len(scripts):
        print("\033[31mERROR:\033[0m no script selected")
        return False

    try:
        script = scripts[current]
    except IndexError:
        print("\033[31mERROR:\033[0m failed to save the script (script not found)")
        return False

    try:
        with open(script, "w", encoding="utf-8") as file:
            file.write(editor.toPlainText())
    except:
        print(f"\033[31mERROR:\033[0m failed to save the script (os error)")
        return False

    return True

saveshortcut.activated.connect(savescript)
savebutton.clicked.connect(savescript)

newshortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+N"), window)
def newscript ():
    global current

    if current >= 0 and not savescript():
        return

    path, _ = QtWidgets.QFileDialog.getSaveFileName(window,"Create a .shik script","","LUAU:B scripts (*.shik)")
    if not path: return

    if os.path.exists(path):
        return

    try:
        with open(path, "x", encoding="utf-8") as script:
            script.write("print(\"hi world\")")
    except:
        print("\033[31mERROR:\033[0m failed to read the script.")
        return

    scripts.append(path)
    current = len(scripts) - 1

    updatescripts()
    editor.setPlainText('print("hi world")')
newshortcut.activated.connect(newscript)
newbutton.clicked.connect(newscript)

openshortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+O"), window)
def openscript ():
    global current

    if current >= 0 and not savescript():
        return

    path, _ = QtWidgets.QFileDialog.getOpenFileName(window,"Open a .shik script","","LUAU:B scripts (*.shik);;Scripts/Text files (*.shik *.py *.pyw *.js *.java *.lua *.html *.css *.txt *.md *.sh *.bat *.cmd *.json *.xml);;All files (*)")
    if not path: return

    contents = ""

    try:
        with open(path, "r", encoding="utf-8") as script:
            contents = script.read()
    except:
        print("\033[31mERROR:\033[0m failed to read the script.")
        return

    if not path in scripts:
        scripts.append(path)
    current = scripts.index(path)

    editor.setPlainText(contents)

    updatescripts()
openshortcut.activated.connect(openscript)
openbutton.clicked.connect(openscript)

window.show()
app.exec()
