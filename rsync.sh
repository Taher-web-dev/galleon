#!/bin/sh -x

for server in galleon_app_uat_1 galleon_app_uat_2; do 
  echo $server
  ssh $server podman stop galleon-middleware 
  rsync -av --exclude "__pycache__" backend ${server}:/home/auser/containers/galleon/
  ssh $server sed -i 's/@127.0.0.1\\/galleon/@10.90.51.194\\/galleon/g' /home/auser/containers/galleon/backend/secrets.env
  ssh $server podman start galleon-middleware 

done
