#!/usr/bin/bash

# start darkhttpd webserver
./darkhttpd web/ --no-listing --log access.log --index status.json  --port 8000  --addr <address>