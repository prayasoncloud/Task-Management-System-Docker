#!bin/bash

mkdir docker-task-management
cd docker-task-management

git init 
git pull https://github.com/prayasoncloud/Task-Management-System-Docker.git
cd backend
docker build -t py-image .
docker run -d -p 5000:5000 py-image:latest

