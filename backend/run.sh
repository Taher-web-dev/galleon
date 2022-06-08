#!/bin/sh -x

# Python: use ipdb instead of pdb
export PYTHONBREAKPOINT=ipdb.set_trace

BASE=$(dirname ${0})
export BACKEND_ENV="${BACKEND_ENV:-${BASE}/secrets.env}"
export LOG_PATH=${BASE}/logs
LISTENING_PORT=$(grep -i '^LISTENING_PORT' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"')
LISTENING_HOST=$(grep -i '^LISTENING_HOST' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"')
mkdir -p $LOG_PATH
# uvicorn --env-file $BACKEND_ENV --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app
# gunicorn main:app -w $(nproc --all) -k uvicorn.workers.UvicornWorker -b $LISTENING_HOST':'$LISTENING_PORT
cd $(dirname "$(realpath $0)")
# hypercorn main:app -w 1 -k uvicorn.workers.UvicornWorker -b $LISTENING_HOST':'$LISTENING_PORT
# hypercorn main:app -w $(nproc --all) -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio'
hypercorn --log-config json_log.ini -w 1 --backlog 200 --debug --reload -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio' main:app 
