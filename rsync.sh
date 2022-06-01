#!/bin/sh -x

for server in galleon_app_uat_1 galleon_app_uat_2; do 
  echo $server
  ssh $server podman stop galleon-middleware
  rsync -av --exclude 'secrets.env' --exclude "logs" --exclude "__pycache__" --exclude ".pytest_cache" backend ${server}:/home/auser/containers/middleware/
  #ssh $server sed -i 's/@127.0.0.1\\/galleon/@10.90.51.194\\/galleon/g' /home/auser/containers/middleware/backend/secrets.env
  #ssh $server sed -i 's/^ZEND_API=.*$/ZEND_API=$(ifconfig ens192 | grep inet  | awk "{print \$2}")\//g' /home/auser/containers/middleware/backend/secrets.env
  #ssh $server sed -i 's/^MOCK_ZAIN_API=.*$/MOCK_ZAIN_API=false/g' /home/auser/containers/middleware/backend/secrets.env
  #ssh $server sed -i 's/@127.0.0.1\\/galleon/@10.90.51.194\\/galleon/g' /home/auser/containers/middleware/backend/secrets.env
  #ssh $server sed -i 's/^MOCK_ZAIN_API=.*$/MOCK_ZAIN_API=false/g' /home/auser/containers/middleware/backend/secrets.env
  ssh $server podman start galleon-middleware

done
