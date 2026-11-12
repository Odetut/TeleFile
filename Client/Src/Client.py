from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
import sys, pathlib, Networking

DebugModeSwitches = {
    "RequiresServer": False,

}

Window = (pathlib.Path(__file__).parent.parent / "UI" / "Main.ui").resolve()

AppIcon = QIcon(str((pathlib.Path(__file__).parent.parent / "Images" / "Logo.ico").resolve()))



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(Window), self)
        self.setWindowIcon(AppIcon)
        self.show()
        self.TargetFile = None
        
           
                    

        # Window defenitions
        self.DownloadButton = self.findChild(QtWidgets.QPushButton,"ToDownload")
        self.UploadButton = self.findChild(QtWidgets.QPushButton,"ToUpload")
        
        self.UploadPage = self.findChild(QtWidgets.QWidget,"UploadPage")
        self.UploadPage.findChild(QtWidgets.QPushButton,"UploadButton").clicked.connect(lambda: self.PromptFileSelect())
        self.UploadPage.findChild(QtWidgets.QPushButton,"SendButton").clicked.connect(lambda: SendButtonPress())
        SendButton = self.UploadPage.findChild(QtWidgets.QPushButton,"SendButton")

        if self.TargetFile is None:
            SendButton.setEnabled(False)

        self.UploadPage.findChild(QtWidgets.QPushButton,"CancelButton").clicked.connect(lambda: self.SwitchWindow("Home"))

        self.DownloadButton.clicked.connect(lambda: self.SwitchWindow("DownloadScreen"))
        self.UploadButton.clicked.connect(lambda: self.SwitchWindow("UploadPage"))

        self.DownloadPage = self.findChild(QtWidgets.QWidget,"DownloadScreen")
        self.DownloadPage.findChild(QtWidgets.QPushButton,"DownloadButton").clicked.connect(lambda:DownloadButtonPress())
        self.CrashPage = self.findChild(QtWidgets.QWidget,"CrashPage")
        self.CrashPage.findChild(QtWidgets.QPushButton,"ExitButton").clicked.connect(lambda: ExitProgram())
        #End of Window defenitions


        #OnPressed funtions
        def DownloadButtonPress():
            Input = self.DownloadPage.findChild(QtWidgets.QPlainTextEdit,"CodeInput").toPlainText()
            if len(Input) < 8: return 
            Success,Err =  Networking.Receive(Input)

            if not Success:
                self.AppCrash(Err) 

        def ExitProgram():
            sys.exit()

        def SendButtonPress():
            Success,Err = Networking.Send(Networking.ReadFile(self.TargetFile),Networking.GetMetadata(self.TargetFile))

            if not Success:
                self.AppCrash(Err)
            








        Success = Networking.ConnectivityCheck()
        if not Success and DebugModeSwitches["RequiresServer"] == True:
            self.SwitchWindow("ServerNotFound")
                


    def PromptFileSelect(self):
        FilePath, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Select a file to upload",
        "",
        "All Files (*.*)")
        self.UpdateUpload(FilePath)
        self.TargetFile = FilePath
        
        
        SendButton = self.UploadPage.findChild(QtWidgets.QPushButton,"SendButton")
        if self.TargetFile is not None:
            SendButton.setEnabled(True)
        

    

    def SwitchWindow(self,NewWindow):
        self.PageStack = self.findChild(QStackedWidget,"stackedWidget",)
        if not self.PageStack: return

        NewWindow = self.findChild(QtWidgets.QWidget,NewWindow)
        if not NewWindow: return
        self.PageStack.setCurrentWidget(NewWindow)

        if NewWindow.objectName() == "UploadPage":
            self.UploadPage.findChild(QtWidgets.QLabel,"FileName").setText("File Name: FileNotFound")
            self.UploadPage.findChild(QtWidgets.QLabel,"FileType").setText("File Type: FileNotFound")
            self.UploadPage.findChild(QtWidgets.QLabel,"FileSize").setText("File Size: FileNotFound")
            SendButton = self.UploadPage.findChild(QtWidgets.QPushButton,"SendButton")
            SendButton.setEnabled(False)

    def UpdateUpload(self,FilePath):
        if not FilePath: return
        self.UploadPage.findChild(QtWidgets.QLabel,"FileName").setText(f"File Name: {FilePath.split("/")[-1]}")
        self.UploadPage.findChild(QtWidgets.QLabel,"FileType").setText(f"File Type: {pathlib.Path(FilePath).suffix}")
        self.UploadPage.findChild(QtWidgets.QLabel,"FileSize").setText(f"File Size: {round(pathlib.Path(FilePath).stat().st_size / 1024)} KB")

    def AppCrash(self,ErrorMessage):
        self.SwitchWindow("CrashPage")
        self.findChild(QtWidgets.QLabel,"ErrorLabel").setText(f"Error Message: {ErrorMessage}")

        


if __name__ == "__main__":
    App = QApplication(sys.argv)
    WindowInstance = MainWindow()
    
    
    








   

















sys.exit(App.exec_())