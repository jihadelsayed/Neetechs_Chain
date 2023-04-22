# neetechs_chain


## docker configuration
### create virtual envorment 
python3 -m venv virtual_environment

### activate on linux
source virtual_environment/bin/activate 

### activate on windows
virtual_environment/Scripts/activate

### git library
python3 -m pip freeze > requirements.txt

### to build it
docker build -t neetechs_chain .

### to run the application
docker run --publish 8888:8888 neetechs_chain

### to go into the shell of the docker
docker run neetechs_chain /bin/bash


### to chick running container
docker container ls

### to chick images
docker images 