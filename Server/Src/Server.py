import json,secrets,dotenv,string,os,sys,subprocess,asyncio,websockets,threading
import logging,datetime,atexit
from flask import Flask,Response,request
from pathlib import Path
from websockets.asyncio.server import serve

##--INIT--##
StartOnRun = True
LoggingDir = (Path(__file__).parent.parent/ "Logs").resolve()
Uploads = (Path(__file__).parent.parent / "Uploads").resolve()
dotenv.load_dotenv((Path(__file__).parent.parent / ".env").resolve())
WebSocketLoop = None
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
    Target = Uploads/ f"{Code}.bin"
    with open(Target,"rb") as File:
        while True:
            Chunk = File.read(1024*1024)
            if not Chunk:
                break

            yield Chunk



def DeleteFile(Code):
    FileCache.pop(Code, None)

    try:
        os.remove(Uploads /f"{Code}.bin")

    except Exception:
        logging.exception(f"Failed to delete {Code}.bin.")


def Start():
    
    try:
        subprocess.run([
        sys.executable, "-m", "pip", "install", "-r",
        str((Path(__file__).parent.parent / "Requirements.txt").resolve())
        ],check=True)

    except subprocess.CalledProcessError:
        logging.exception("Error installing requirements")
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
def End(FileCache): #TODO: Path loads too late predefine
    if not FileCache is None:
        with open(Path(__file__).parent / "Metadata.json","w") as File:
            logging.info("Saving Metadata.json...")
            File.write(json.dumps(FileCache,indent=4)) 

    
        
   
    

    

    



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

    logging.info(f"Connection from {ClientSocket.remote_address[0]} has been established.")
    Clients[SessionID] = ClientSocket
    
    # In the future this would dispatch messages to appropiate services
    try:
        await ClientSocket.send(f"SessionID:{SessionID}")
        async for Message in ClientSocket:
            pass

    finally:
        logging.info(f"Dead client removing: {SessionID}")
        Clients.pop(SessionID, None)


async def CloseConnections():
    for _,Socket in list(Clients.items()):
        await Socket.close(code=1001,reason="Shutting down")



async def Disconnect(SessionId,Reason):
    if SessionId in Clients:
        await Clients[SessionId].close(code=1000,reason=Reason)
        

        logging.info(f"Client {SessionId} has been disconnected.")
    else:
        logging.warning(f"No client with SessionID {SessionId} found.")


async def SendToClient(SessionId,Data):
    if SessionId in Clients:
        await Clients[SessionId].send(Data)
        logging.info(f"Sent data to client {SessionId}.")

    else:
        logging.warning(f"No client with SessionID {SessionId} found.")


def ReadMetadata(Code):
    FileData = FileCache.get(Code)
    if not FileData:
        return None,None
    
    FileName = FileData.get("FileName")
    FileSize = FileData.get("FileSize")

    return FileName,FileSize
    



    

#--MAIN--#
App = Flask(__name__)

@App.route("/Ping!")
def Callback():
    return "Pong!"


@App.route("/<SessionID>/Download/<Code>")
def Download(Code,SessionID):
    if SessionID is None or SessionID not in Clients:
        return Response("IllegalClient",status=400)

    FileName,FileSize = ReadMetadata(Code)

    DownloadResponse = Response(
        ReadFile(Code),
        mimetype="application/octet-stream",
        headers= {
            "FileName" : FileName,
            "FileSize" : str(FileSize)
            }
        )
    

    DownloadResponse.call_on_close(lambda: DeleteFile(Code))

    asyncio.run_coroutine_threadsafe(
        SendToClient(SessionID, "Done"),WebSocketLoop)
    return DownloadResponse
    


@App.route("/<SessionID>/Upload",methods = ["POST"])
def Upload(SessionID):
    if SessionID is None or SessionID not in Clients:
        return Response("IllegalClient",status=400)
    
    FileCode = CodeGenerator() 
    Check = DuplicateCheck(FileCode)
    while Check: 
        FileCode = CodeGenerator()
        Check = DuplicateCheck(FileCode)

    asyncio.run_coroutine_threadsafe(
    SendToClient(SessionID, f"FileCode:{FileCode}"),
    WebSocketLoop
    )

    with open(Uploads/f"{FileCode}.bin","wb") as File: #Save file as a binary 
        while True: 
            Chunk = request.stream.read(1024*1024)

            if not Chunk:
                break

            File.write(Chunk)

    
    FileCache[FileCode] = {
        "FileName":request.headers.get("FileName"),
        "FileSize":request.headers.get("FileSize")   # Change  
    }
    asyncio.run_coroutine_threadsafe(
    SendToClient(SessionID, "Done"),WebSocketLoop)
    
    return "Recieving"


@App.route("/favicon.ico")
def Favicon():
    return Response(status=204) 

@App.route("/DoAFlip")
def DoAFlip():
    return Response("¯\_(ツ)_/¯",status=418)

atexit.register(lambda: End(FileCache))




# Isnt funny the main program is all the way down here, Just a funny thought

# Conditional present for debugging purposes
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
    global WebSocketLoop
    
        
    WebSocketLoop = asyncio.get_running_loop()
    ServerWebsocket = await serve(
        AcceptConnections,
        os.getenv("ServerAddress"),
        int(os.getenv("WebPort"))
    )
    
    try:
        logging.info("Server Successfully started")
        await ServerWebsocket.serve_forever()
        


    finally:
        await CloseConnections()
        ServerWebsocket.close()
        await ServerWebsocket.wait_closed()


    

asyncio.run(WebSocketMain())

    
