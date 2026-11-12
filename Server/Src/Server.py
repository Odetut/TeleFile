import json,secrets,dotenv,string,os,sys,subprocess,asyncio,websockets,threading
import logging,datetime
from flask import Flask,Response,request
from pathlib import Path
from websockets.asyncio.server import serve

##--INIT--##
StartOnRun = False
LoggingDir = (Path(__file__).parent.parent/ "Logs").resolve()
Uploads = (Path(__file__).parent.parent / "Uploads").resolve()
dotenv.load_dotenv((Path(__file__).parent.parent / ".env").resolve())
Clients = {}


FileHandler = logging.FileHandler(LoggingDir / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
ConsoleHandler = logging.StreamHandler()

LogFormat = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")

FileHandler.setFormatter(LogFormat)
ConsoleHandler.setFormatter(LogFormat)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[FileHandler, ConsoleHandler]
)


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
        logging.exception(f"Error installing requirements")
        return False,None
    logging.info("Succesfully installed requirements continuing Start()")


    try:
        with open( Path(__file__).parent / "Metadata.json","r") as File:
            try:
                FileCache = json.loads(File.read())
            except json.decoder.JSONDecodeError:
                FileCache = {}
                logging.warning("Metadata.json was Empty/Invalid, Will Create new one on exit.")
            except Exception as e:
                FileCache = {}
                logging.warning(f"An unexpected error occurred while reading Metadata.json: {e} || Will Create new one on exit.")
                
    except FileNotFoundError:
        FileCache = {}
        logging.warning("Metadata.json not found, Will Create new one on exit.")

    except PermissionError:
        FileCache = {}
        logging.error("Permission denied while trying to read Metadata.json.Session will continue, but changes will not be saved on exit.")        


   
    logging.info("Start() was successful")
    return True, FileCache




    

# All things that Start() must End()
def End(FileCache):
    with open(Path(__file__).parent / "Metadata.json","w") as File:
        logging.info("Saving Metadata.json...")
        File.write(json.dumps(FileCache,indent=4)) 
    CloseConnections()

    

    



def DuplicateCheck(Code):
    return Code in FileCache

#Init WebSocket
async def AcceptConnections(ClientSocket):
    SessionID = secrets.token_hex(32) 
    
    while True: 
        if SessionID in Clients:
            SessionID = secrets.token_hex(32)  
        else:
            break

    logging.info(f"Connection from {ClientSocket.remote_address[1]} has been established.")
    Clients[SessionID] = ClientSocket
    await ClientSocket.send(f"SessionID:{SessionID}")


    # In the future this would dispatch messages to appropiate services
    try:
        async for Message in ClientSocket:
            pass
    finally:
        logging.info(f"Dead client removing: {SessionID}")
        Clients.pop(SessionID, None)


async def CloseConnections():
    for _,Socket in Clients.items():
        await Socket.close(code=1001,reason="Shutting down")



    
   
# def DisconnectLEGACY(SessionID):
#     if SessionID in Clients:
#         Clients[SessionID].close()
#         del Clients[SessionID]
#         print(f"Client {SessionID} has been disconnected.")
#     else:
#         print(f"No client with SessionID {SessionID} found.")


def Disconnect(SessionId,Reason):
    if SessionId in Clients:
        Clients[SessionId].close(code=1000,reason=Reason)
        del Clients[SessionId]

        logging.info(f"Client {SessionId} has been disconnected.")
    else:
        logging.warning(f"No client with SessionID {SessionId} found.")


# def SendToClientLEGACY(SessionID,Data):
#     if SessionID in Clients:
#         Clients[SessionID].sendall(Data.encode())
#         print(f"Sent data to client {SessionID}.")
#     else:
#         print(f"No client with SessionID {SessionID} found.")

async def SendToClient(SessionId,Data):
    if SessionId in Clients:
        await Clients[SessionId].send(Data)
        logging.info(f"Sent data to client {SessionId}.")

    else:
        logging.warning(f"No client with SessionID {SessionId} found.")






    

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

    with open(Uploads/f"{FileCode}.bin","wb") as File: #Save file as a binary 
        while True: 
            Chunk = request.stream.read(1024*1024)

            if not Chunk:
                break

            File.write(Chunk)

    
    FileCache[FileCode] = {
        "Filename":request.headers.get("Filename"),
        "FileType":request.headers.get("FileType")   
    }


@App.route("/favicon.ico")
def Favicon():
    return Response(status=204) 

@App.route("/DoAFlip")
def DoAFlip():
    return Response("¯\_(ツ)_/¯",status=418)


# Isnt funny the main program is all the way down here, Just a funny thought

# Conditional present for debugging purposes
logging.debug("Test")
Started,FileCache = Start()
if not Started:
    logging.critical("Server failed to start due to an error")
    logging.warning("Tough luck, Loser!")
    sys.exit(1)

def HttpMain():
        App.run(
        host=os.getenv("ServerAddress"),
        port=int(os.getenv("HttpPort")),
        use_reloader=False
    )


if StartOnRun: 
    HttpThread = threading.Thread(target=HttpMain,daemon=True)
    HttpThread.start()

        
async def WebSocketMain():
    ServerWebsocket = await serve(
        AcceptConnections,
        os.getenv("ServerAddress"),
        int(os.getenv("WebPort"))
    )
    
    logging.info("Server Successfully started") 
    await ServerWebsocket.serve_forever()


asyncio.run(WebSocketMain())
    
