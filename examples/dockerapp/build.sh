#! /bin/bash
docker stop testai
docker rm testai
docker build  -t testai .
docker run -d --name testai -v `pwd`/../dyvideo1:/app/dyvideo -p 5000:5000 -p 9191:9191  testai
docker image prune -f
docker volume prune -f
