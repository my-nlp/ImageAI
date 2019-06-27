#! /bin/bash

# install latest docker ce 
mkdir /docker-ce
cd /docker-ce
wget https://download.docker.com/linux/static/stable/x86_64/docker-18.09.6.tgz
tar zxvf docker-18.09.6.tgz
cp docker/* /usr/bin/