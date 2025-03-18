#!/usr/bin/bash

# start darkhttpd webserver
./darkhttpd web/ --no-listing --log access.log --index index.html --port 8000 --addr <address>