# TeleFile

A personal project with a simple premise.

TeleFile is an app designed to allow users to upload a file and receive a code that can later be used on another machine to download that file.

TeleFile is **NOT a cloud service**. It is not intended to hold files for long periods of time it is simply a tool for moving files between machines.

The server receives requests from clients wishing to either upload or download a file. When uploading the file's bytes are read and sent through HTTP, where the server temporarily stores the file, generates a code, and returns it to the client through a WebSocket. The same code can then be used by another client to request and download the file.

Also like maybe dont use this for real important stuff for now lol.



