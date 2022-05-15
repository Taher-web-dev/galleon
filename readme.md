## Galleon Middleware

A thin-wrapper that implements basic business logic and invokes respective zain backend api end points.

### Install / usage

#### Requirements

- git
- python >= 3.9
- pip
- jq
- postgresql

Optional:

- podman
- gzip


#### Local / Direct Setup

```
# Go inside the project folder
cd backend 

# Install required modules
pip install -r requirements.txt

# Create logs folder (path can be configured in sample.env)
mkdir ./logs

# Install pytest
pip install -r requirements-dev.txt 

# Environment setup
cp sameple.env secrets.env
create your DB
Add your DB credentials in secrets.env at "DATABASE_URL"
source env.sh

# To run and migrate the DB tables:
python main.py
# or
./run.sh

# Unit test
python tests.py

# pytest
pytest -v


# Invoke sample apis using curl
./curl.sh
```

#### Using Podman/Container

```
# Build
podman rmi galleon-middleware
podman build -t galleon-middleware .

# Run 
podman run --name galleon-middleware --rm \
  -p 0.0.0.0:8080:8080/tcp \
  -it galleon-middleware \
  /home/backend/run.sh
  
# Command line access inside the container
podman exec -it galleon-middleware ash

# The image can be saved to a file for off-line deployement
podman save --quiet galleon-middleware | gzip > galleon-middleware.tar.gz

# Then loaded at the target system
podman load -i galleon-middleware.tar.gz

# Stop/start container
podman stop galleon-middleware
podman start galleon-middleware

# Watch podman logs
podman logs --follow --tail 0 galleon-middleware | jq

# Watch app logs
tail -n 0 -f ./logs/x-ljson.log | jq
```


