from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
import sys, pathlib, Networking


Window = (pathlib.Path(__file__).parent.parent / "UI" / "Main.ui").resolve()

AppIcon = QIcon(str((pathlib.Path(__file__).parent.parent / "Images" / "Logo.ico").resolve()))



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(Window), self)
        self.setWindowIcon(AppIcon)
        self.show()

        
        self.DownloadButton = self.findChild(QtWidgets.QPushButton,"ToDownload")
        self.UploadButton = self.findChild(QtWidgets.QPushButton,"ToUpload")
        
        self.UploadPage = self.findChild(QtWidgets.QWidget,"UploadPage")
        self.UploadPage.findChild(QtWidgets.QPushButton,"UploadButton").clicked.connect(lambda: self.PromptFileSelect())
        
        self.UploadPage.findChild(QtWidgets.QPushButton,"CancelButton").clicked.connect(lambda: self.SwitchWindow("Home"))

        self.DownloadButton.clicked.connect(lambda: self.SwitchWindow("DownloadScreen"))
        self.UploadButton.clicked.connect(lambda: self.SwitchWindow("UploadPage"))

    def PromptFileSelect(self):
        FilePath, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Select a file to upload",
        "",
        "All Files (*.*)")
        self.UpdateUpload(FilePath)

       


    def SwitchWindow(self,NewWindow):
        self.PageStack = self.findChild(QStackedWidget,"stackedWidget",)
        if not self.PageStack: return

        NewWindow = self.findChild(QtWidgets.QWidget,NewWindow)
        if not NewWindow: return
        self.PageStack.setCurrentWidget(NewWindow)


    def UpdateUpload(self,FilePath):
        self.UploadPage.findChild(QtWidgets.QLabel,"FileName").setText(f"File Name: {FilePath.split("/")[-1]}")
        self.UploadPage.findChild(QtWidgets.QLabel,"FileType").setText(f"File Type: {pathlib.Path(FilePath).suffix}")
        self.UploadPage.findChild(QtWidgets.QLabel,"FileSize").setText(f"File Size: {round(pathlib.Path(FilePath).stat().st_size / 1024,2)} KB")


        




        


if __name__ == "__main__":
    App = QApplication(sys.argv)
    WindowInstance = MainWindow()







   

















sys.exit(App.exec_())