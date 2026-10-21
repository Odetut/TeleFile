import json,secrets,dotenv,socket,string,os,sys,subprocess
from flask import Flask,Response,request
from pathlib import Path

##--INIT--##
StartOnRun = False
ProtoLock = False #TODO: Make it so only one user can use the prototype at a time
Uploads = (Path(__file__).parent.parent / "Uploads").resolve()
dotenv.load_dotenv((Path(__file__).parent.parent / ".env").resolve())
Clients = {}

#TODO: Make it check if the code already exists, If true then generate another
#Generates a true random code and returns it
def CodeGenerator():
    Code = ""
    for _ in range(8):
        Code += secrets.choice(string.digits + string.ascii_uppercase)

    return Code

def ReadFile(Code): #Replicated on client
    Target = Uploads/ Code
    with open(Target,"rb") as File:
        while True:
            Chunk = File.read(1024*1024)
            if not Chunk:
                break

            yield Chunk

def Start():
    
    try:
        subprocess.run([
        sys.executable, "-m", "pip", "install", "-r",
        str((Path(__file__).parent.parent / "Requirements.txt").resolve())
        ],check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False,None

    

    try:
        with open( Path(__file__).parent / "Metadata.json","r") as File:
            try:
                FileCache = json.loads(File.read())
            except json.decoder.JSONDecodeError:
                FileCache = {}
                print("Metadata.json was Empty/Invalid, Will Create new one on exit.")
            except Exception as e:
                FileCache = {}
                print(f"An unexpected error occurred while reading Metadata.json: {e}")
                print("Will Create new one on exit.")
    except FileNotFoundError:
        FileCache = {}
        print("Metadata.json not found, Will Create new one on exit.")

    except PermissionError:
        FileCache = {}
        print("Permission denied while trying to read Metadata.json.Session will continue, but changes will not be saved on exit.")        
       

        return True, FileCache




    print("Server Successfully started") #TODO:Change to a log

# All things that Start() must End()
def End(FileCache):
    with open(Path(__file__).parent / "Metadata.json","w") as File:
        print("Saving Metadata.json")
        File.write(json.dumps(FileCache,indent=4)) 

    



def DuplicateCheck(Code):
    return Code in FileCache

ServerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ServerSocket.bind((os.getenv("ServerAddress"),int(os.getenv("Port"))))
ServerSocket.listen(3) # Prototype supports 1 user at a time

def AcceptConnections(): 
    ClientSocket,Address = ServerSocket.accept()
    SessionID = secrets.token_hex(32) 
    if SessionID in Clients: # When the stars align this will run 💀
        SessionID = secrets.token_hex(64)
    print(f"Connection from {Address} has been established.")
    Clients[SessionID] = ClientSocket
    ClientSocket.sendall(f"SessionID:{SessionID}".encode()) # Send the session ID to the client

    
   
def Disconnect(SessionID):
    if SessionID in Clients:
        Clients[SessionID].close()
        del Clients[SessionID]
        print(f"Client {SessionID} has been disconnected.")
    else:
        print(f"No client with SessionID {SessionID} found.")


def SendToClient(SessionID,Data):
    if SessionID in Clients:
        Clients[SessionID].sendall(Data.encode())
        print(f"Sent data to client {SessionID}.")
    else:
        print(f"No client with SessionID {SessionID} found.")





    

#--MAIN--#
App = Flask(__name__)

@App.route("/Ping!")
def Callback():
    return "Pong!"


@App.route("/<Code>")
def Download(Code):#TODO: Make it so server adds Filename and ext to client
    return Response(ReadFile(Code),mimetype = "application/octet-stream")


@App.route("/<SessionID>/Upload",methods = ["POST"])
def Upload(SessionID):
    FileCode = CodeGenerator() 
    Check = DuplicateCheck(FileCode)
    while Check: 
        FileCode = CodeGenerator()
        Check = DuplicateCheck(FileCode)
    SendToClient(SessionID,f"FileCode:{FileCode}") 

    with open(Uploads/f"{FileCode}.bin","wb") as File: #Save file as a binary till JSON is implemented
        while True: 
            Chunk = request.stream.read(1024*1024)

            if not Chunk:
                break

            File.write(Chunk)

    
    FileCache[FileCode] = {
        "Filename":request.headers.get("Filename"),
        "FileType":request.headers.get("FileType")   
    }




# Isnt funny the main program is all the way down here, Just a funny thought

# Conditional present for debugging purposes
Started,FileCache = Start()
if not Started:
    print("Server failed to start due to an error in the requirements installation.")
    print("Tough luck, Loser!")
    sys.exit(1)

if StartOnRun: App.run(host=os.getenv("ServerAddress"),port=int(os.getenv("Port")))
