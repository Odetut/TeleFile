import socket,requests,os,threading
from dotenv import load_dotenv

load_dotenv()



# Recieve the file along with where to write it to.
def Receive(Code,Destination):
    URL = f"http://{os.getenv('ServerAddress')}:{os.getenv('Port')}/{Code}"
    # We use stream so the entire files contents wont be loaded into RAM at once.
    Response = requests.get(URL,stream=True)

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
def Send(Data):
    requests.post(os.getenv("ServerAddress"),Data)
    

"""
So loading the file isnt fully loaded
into RAM we read it in smaller portions.
To use it combine it with Send E.g. Send(Upload(Filepath))
"""

def Upload(FilePath):
    with open(FilePath,"rb") as File:
        while True:
            Chunk = File.read(1024*1024)

            if not Chunk: # Python treats an empty byte as True
                break

            yield Chunk




    

        
            


