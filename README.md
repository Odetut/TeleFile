# TeleFile

A personal project with a simple premise.

TeleFile is an "app" designed to allow people to upload a file  receive a code then later use it on another machine to download that file.

TeleFile is **NOT a cloud service**. It is not intended to hold files for long periods of time.

The server receives requests from clients wishing to either upload or download a file. When uploading the file's bytes are read and sent through HTTP, where the server temporarily stores the file, generates a code and returns it to the client through a WebSocket. The same code can then be used by another client to request and download the file.

Also like maybe dont use this for real important stuff for now lol.

TeleFile is licensed under the PolyForm Noncommercial License 1.0.0.



