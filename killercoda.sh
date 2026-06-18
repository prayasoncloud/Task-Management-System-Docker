mkdir docker-task-management
cd docker-task-management

sudo apt update
sudo apt install docker-compose-v2 -y


git init 
git pull https://github.com/prayasoncloud/Task-Management-System-Docker.git
docker compose up --build


