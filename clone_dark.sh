#!/bin/bash

# clone the darkhttpd repo
git clone https://github.com/emikulic/darkhttpd.git temp

# go into temp directory and compile
cd temp && make

# mv darkhttpd up a directory
mv darkhttpd ..

# move up directory and remove temp
cd .. && rm -rf temp