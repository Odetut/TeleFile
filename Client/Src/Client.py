from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
import sys, pathlib

App = QtWidgets.QApplication(sys.argv)

Window = uic.loadUi((pathlib.Path(__file__).parent.parent / "UI" / "Main.ui").resolve())

AppIcon = QIcon(str((pathlib.Path(__file__).parent.parent / "Images" / "Logo.ico").resolve()))
App.setWindowIcon(AppIcon)# Dont know why this dont work lol
Window.setWindowIcon(AppIcon)

Window.show()

def SwitchWindow(NewWindow):
    pass













sys.exit(App.exec_())