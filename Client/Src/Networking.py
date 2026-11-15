import socket,requests,os,threading,sys,websockets
from dotenv import load_dotenv
from pathlib import Path
from websockets.sync.client import connect

load_dotenv()


SessionId = None


# Recieve the file along with where to write it to.
def Receive(Code):
    try:
        URL = f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/{SessionId}/Download/{Code}"
        # We use stream so the entire files contents wont be loaded into RAM at once.
        Response = requests.get(URL,stream=True)

        if Response.headers.get("FileName") is None:
            Filename = f"{Code}.bin"
        else:
            Filename = Response.headers.get("FileName")

        Destination = Path.home() /"Downloads"/f"{Filename}"

        if Response.status_code == 200:
            with open(Destination,"wb") as File:
                for Chunk in Response.iter_content(chunk_size=1024): # Accept 1024 bytes per chunk
                    File.write(Chunk) #Writes the bytes to the file

            return True,None

        #File was not found return to the client as a failure.
        elif Response.status_code == 404:
            return False, "FileNotFound"
    except Exception as e:
        return False,e    



# Function to send data to the server through HTTP
def Send(Data,Metadata):
    try:
    
        Response = requests.post(f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/{SessionId}/Upload",
                        data=Data,
                        headers={
                            "FileName": Metadata.get("FileName"),
                            "FileSize": str(Metadata.get("FileSize")) # Change to size
                        })
        
    except Exception:
        return False, "SendError"

    if Response.text == "IllegalClient":
        return False,"Server cant recognise Client"
    else:
        return True, Socket.recv(12)
    
    

"""
So loading the file isnt fully loaded
into RAM we read it in smaller portions.
To use it combine it with Send E.g. Send(ReadFile(Filepath), Metadata)
"""

def ReadFile(FilePath): #Replicated on Server
    with open(FilePath,"rb") as File:
        while True:
            Chunk = File.read(1024*1024)

            if not Chunk: # Python treats an empty byte as False
                break

            yield Chunk


def GetMetadata(FilePath):
    if not os.path.isfile(FilePath):
        return None
    return {
        "FileName": os.path.basename(FilePath),
        "FileSize": os.path.getsize(FilePath) 
    }

def UpdateSessionId(ID):
    global SessionId
    SessionId = ID



def LaunchSocket():
    global Socket
    try:
        Socket = connect(f"ws://{os.getenv('ServerAddress')}:{os.getenv('WebPort')}")
    except Exception:
        return False,"Failed to connect Websocket"
    try:
        SessionId = Socket.recv(30)
    except Exception:
        print("Couldnt get a SessionId within reasonable time")
        return False,"Exceeded reasonable waiting time for Websocket to connect"

    if SessionId.startswith("SessionID:"):
        SessionId = SessionId.split(":",1)[1]
        UpdateSessionId(SessionId)
        return True,SessionId
    else:
        Socket.close(code=1001,reason="Server provided unexpected input.")
        return False,f"UnexpectedMsg:{SessionId}"

def Listen(WantedAns):
    try:
        Result = Socket.recv(10)
    except Exception:
        return False

    if Result == WantedAns:
        return True
    else:
        return False


def CloseSocket(Reason):
    if not Reason: return False
    Socket.close(code=1000,reason=Reason)

def Start():
    Success,Result = LaunchSocket()

    if not Success:
        return False,Result

    return True,Result
    

def End():
    Socket.close(code=1000,reason="Client shutdown")






def ConnectivityCheck():
    try:
        requests.get(f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/Ping!", timeout=10)  
        return True
    except requests.exceptions.RequestException as e:
        #print(f"Error checking connectivity: {e}")
        return False

# I added this cause I kept pressing the run keybinds lol

if __name__ == "__main__":
    
   
    print("This file is not meant to be run directly. Please run the main client application instead.")
    sys.exit(1)  
            


