# Galleon Middleware

A thin-wrapper that implements basic business logic and invokes respective zain-backend api endpoints.

## Install / usage

### Requirements

- git
- python >= 3.9
- pip
- jq
- postgresql

Optional:

- podman
- gzip

### Local / Direct Setup

#### Go inside the project folder

`cd backend`

#### Install required modules

`pip install --user -r requirements.txt`

#### Create logs folder (path can be configured in sample.env)

`mkdir ./logs`

#### Install pytest

`pip install --user -r requirements-dev.txt`

#### Environment setup

`cp sample.env secrets.env`

create your DB (we're using postgresql)
Add your DB credentials in secrets.env at "DATABASE_URL"

`source env.sh`

Note: You will need to repeat this command every time you change the environment variables or every new terminal session.

#### To run and migrate the DB tables

`python main.py`

#### or

`./run.sh`

#### Unit test

`python tests.py`

#### pytest

`pytest -v`

#### Invoke sample apis using curl

`./curl.sh`

#### Using Podman/Container

```plain
# Build
podman rmi galleon-middleware
podman build -t galleon-middleware .

# Run
 podman run --name galleon-middleware --rm \
  -e DATABASE_URL="postgresql://db-user:db-pass@server-ip/db-name" \
  -p 127.0.0.1:8080:8080/tcp \
  -it galleon-middleware \
  /home/backend/run.sh

# Command line access inside the container
podman exec -it galleon-middleware ash

# The image can be saved to a file for off-line deployment
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


#### Git pre-commit hook

```
echo '#!/usr/bin/env bash
black .
flake8
export BACKEND_ENV=backend/secrets.env
export LOG_PATH=backend/logs
pytest -v' > .git/hooks/pre-commit
chmod a+x .git/hooks/pre-commit
```
