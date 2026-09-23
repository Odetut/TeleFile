import json,secrets,dotenv,socket,string,os
from flask import Flask,Response,request
from pathlib import Path

##--INIT--##
StartOnRun = False
Uploads = (Path(__file__).parent.parent / "Uploads").resolve()
dotenv.load_dotenv((Path(__file__).parent.parent / ".env").resolve())

#TODO: Make it check if the code already exists, If true then generate another
#Generates a ture random code and returns it
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
    #TODO: Check python requirements 
    return "Server Successfully started" #TODO:Change to a log


#--MAIN--#
App = Flask(__name__)

#@App.route("/")

@App.route("/Ping!")
def Callback():
    return "Pong!"


@App.route("/<Code>")
def Download(Code):
    return Response(ReadFile(Code),mimetype = "application/octet-stream")


@App.route("/Upload",methods = ["POST"])
def Upload():
    FileCode = CodeGenerator() #TODO: Send to client via Websocket

    with open(Uploads/f"{FileCode}.bin","wb") as File: #Save file as a binary till JSON is implemented
        while True: 
            Chunk = request.stream.read(1024*1024)

            if not Chunk:
                break

            File.write(Chunk)


# Conditional present for debugging purposes
if StartOnRun: App.run(host=os.getenv("ServerAddress"),port=int(os.getenv("Port")))
