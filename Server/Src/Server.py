import json,secrets,dotenv,flask,socket,string
from pathlib import Path

##--INIT--##
StartOnRun = False
Uploads = (Path(__file__).parent.parent / "Uploads").resolve()



#TODO: Make it check if the code already exists, If true then generate another
#Generates a ture random code and returns it
def CodeGenerator():
    Code = ""
    for _ in range(8):
        Code += secrets.choice(string.digits + string.ascii_uppercase)

    return Code



#--MAIN--#
App = flask.Flask(__name__)

@App.route("/")
def Start():
    #TODO: Check python requirements 
    return "Server Succesfully started"

@App.route("/Ping!")
def Callback():
    return "Pong!"


if StartOnRun: App.run()
