import socket,requests,os,threading,sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

#PLACEHOLDERS#
SessionId = None


# Recieve the file along with where to write it to.
def Receive(Code):
    URL = f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/{Code}"
    # We use stream so the entire files contents wont be loaded into RAM at once.
    Response = requests.get(URL,stream=True)

    if Response.headers.get("Filename") is None:
        Filename = Code
    else:
        Filename = Response.headers.get("Filename")

    Destination = Path.home() /"Downloads"/f"{Filename}"

    if Response.status_code == 200:
        with open(Destination,"wb") as File:
            for Chunk in Response.iter_content(chunk_size=1024): # Accept 1024 bytes per chunk
                File.write(Chunk) #Writes the bytes to the file

        return True,None

    #File was not found return to the client as a failure.
    elif Response.status_code == 404:
        return False, "FileNotFound"


HeartbeatEventObj = threading.Event() 
#TODO: This will run on its own thread (As it yeilds)
def Heartbeat():
    # TODO: Make it so the client pings the server

    while True:
        HeartbeatEventObj.clear()
        # Send ping here then run .set() if response

        if not HeartbeatEventObj.wait(15): # After 15 seconds runs out return false.
            #Run Cleanup function Here
            break

# Function to send data to the server through HTTP
def Send(Data,Metadata):
    
    requests.post(f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/{SessionId}/Upload",
                      data=Data,
                      headers={
                          "Filename": Metadata.get("Filename"),
                          "FileType": Metadata.get("FileType")
                      })

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
    return {
        "Filename": os.path.basename(FilePath),
        "FileType": os.path.splitext(FilePath)[1]
    }

# Temporary # 
"""
The following may be changed/Moved in the future.
"""


def LaunchSocket(): #TODO: Timeouts for http and websocket
    global Socket
    Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    Socket.connect((os.getenv("ServerAddress"),int(os.getenv("WebPort"))))
    SessionId = Socket.recv(1024).decode() # Recieve the session ID from the server
    if SessionId.startswith("SessionID:"):
        SessionId = SessionId.split(":")[1]

    else:
        print("Failed to receive a valid SessionID from the server.")
        return False, "InvalidSessionID"


    print(f"Connected to server with SessionID: {SessionId}")



def End():
    Socket.close()




def Ping(): # We dont instantly return true if the Http responds as we also need the WebSocket to respond. If either fails we return false.
    # Http Check
    try:
        Response = requests.get(f"http://{os.getenv('ServerAddress')}:{os.getenv('Port')}/Ping!")
        if Response.text == "Pong!":
            print("Server is reachable via HTTP.")
        else:
            print("Server is reachable via HTTP, but got an unexpected response.") 
            
    except requests.exceptions.RequestException as e:
        print(f"Error pinging server: {e}")
        return False, "HTTPError"
    
    # WebSocket Check
    try:
        Socket.sendall(b"Ping")
        # Wait for a response from the server
        Response = Socket.recv(1024)

        if Response == b"Pong": 
            # We dont check if its an unexpected response because the message could be intended for another system
            print("Server is reachable via WebSocket.")
        return True
    
    except socket.error as e:
        print(f"Error connecting to WebSocket server: {e}")
        return False, "WebSocketError"

# End of Temporary #


def ConnectivityCheck():
    try:
        requests.get(f"http://{os.getenv('ServerAddress')}:{os.getenv('HttpPort')}/Ping!", timeout=10)  
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error checking connectivity: {e}")
        return False

# I added this cause I kept pressing the run keybinds lol

if __name__ == "__main__":
    print("This file is not meant to be run directly. Please run the main client application instead.")
    sys.exit(1)  
            


