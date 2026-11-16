ImportSuccess = True
try:
    from PyQt5 import QtWidgets, uic
    from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
    from PyQt5.QtGui import QIcon
    import sys, pathlib, Networking,subprocess,logging,datetime
except Exception:
    ImportSuccess = False
LoggingDir = (pathlib.Path(__file__).parent.parent/ "Logs").resolve()

# Debug # 
DebugModeSwitches = {
    "RequiresServer": True,

}

FileHandler = logging.FileHandler(LoggingDir / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
ConsoleHandler = logging.StreamHandler()

LogFormat = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")

FileHandler.setFormatter(LogFormat)
ConsoleHandler.setFormatter(LogFormat)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[FileHandler, ConsoleHandler]
)

Window = (pathlib.Path(__file__).parent.parent / "UI" / "Main.ui").resolve()

AppIcon = QIcon(str((pathlib.Path(__file__).parent.parent / "Images" / "Logo.ico").resolve()))

if ImportSuccess is False:
    try:
        subprocess.run([
        sys.executable, "-m", "pip", "install", "-r",
        str((pathlib.Path(__file__).parent.parent / "Requirements.txt").resolve())
        ],check=True)
        logging.log("Succesdsfully installed requirements. Please restart")

        
        sys.exit()
        
    except subprocess.CalledProcessError:
        logging.critical("Failed to install Dependencies")
        sys.exit()
        
        

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
        self.DownloadSuccess = self.findChild(QtWidgets.QWidget,"DownloadSuccess")
        self.DownloadSuccess.findChild(QtWidgets.QPushButton,"CloseButton").clicked.connect(lambda: ExitProgram())

        self.DownloadSuccess = self.findChild(QtWidgets.QWidget,"UploadSuccess")
        self.DownloadSuccess.findChild(QtWidgets.QPushButton,"CloseButton_2").clicked.connect(lambda: ExitProgram())

        self.UploadSuccess = self.findChild(QtWidgets.QWidget,"UploadSuccess")
        self.FileCodeLabel = self.UploadSuccess.findChild(QtWidgets.QLabel,"CodeBox")
        #End of Window defenitions


        #OnPressed funtions
        def DownloadButtonPress():
            Input = self.DownloadPage.findChild(QtWidgets.QPlainTextEdit,"CodeInput").toPlainText()
            if len(Input) < 8: return 
            Success,Err =  Networking.Receive(Input)

            if not Success:
                self.AppCrash(Err)
            else:
                self.SwitchWindow("TransferPage")
                self.findChild(QtWidgets.QLabel,"ActionText").setText("Downloading")
                Success = Networking.Listen("Done")
                if Success:
                    Networking.CloseSocket("Client Shutdown")
                    self.SwitchWindow("DownloadSuccess")


        def ExitProgram():
            sys.exit()

        def SendButtonPress():
            Success,Result = Networking.Send(Networking.ReadFile(self.TargetFile),Networking.GetMetadata(self.TargetFile))

            if not Success:
                self.AppCrash(Result)
            else:
                self.SwitchWindow("TransferPage")
                self.findChild(QtWidgets.QLabel,"ActionText").setText("Uploading")
                Success = Networking.Listen("Done")
                if Success:
                    Networking.CloseSocket("Client Shutdown")
                    self.SwitchWindow("UploadSuccess")
                    self.FileCodeLabel.setText(Result)
                    
                    
        

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
    App.setStyle("Fusion")
    WindowInstance = MainWindow()

    Success,Result = Networking.LaunchSocket()
    if not Success and DebugModeSwitches["RequiresServer"] is True:
        WindowInstance.SwitchWindow("ServerNotFound")
        

    
    
    


sys.exit(App.exec_())