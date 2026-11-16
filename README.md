# TeleFile

A personal project with a simple premise.

TeleFile is an "app" designed to allow people to upload a file  receive a code then later use it on another machine to download that file.

TeleFile is **NOT a cloud service**. It is not intended to hold files for long periods of time.

The server receives requests from clients wishing to either upload or download a file. When uploading the file's bytes are read and sent through HTTP, where the server temporarily stores the file, generates a code and returns it to the client through a WebSocket. The same code can then be used by another client to request and download the file to their own computer.

# How to use
1) Download the Server file and set it up the .env.Template to your liking. Then rename it to .env
2) Launch the server and follow the instructions in the output
3) Download the client file and set the .env.Template to match the server. Rename it to .env
4) Then use the Client through the **Client.py** if set up correctly the client should open on the home screen
   

That's it! TeleFile should handle installing its requirements automatically provided you give it permission




# Future Features
TeleFile may receive the following in the future if development continues:
 - Encryption of files during transfer
 - Turning a file code into a QR code allowing a file to be downloaded to a phone
 - Uploading multiple files at once
 - Clients able to change the server thorough a gui rather than the env
 - File expiration


**Warning: TeleFile lacks proper encryption your files are vulnerable during transfers**


TeleFile is licensed under the PolyForm Noncommercial License 1.0.0.



