""" FastApi Main module """

import sys
import time
import traceback
import logging
import logging.handlers
import uvicorn
# from settings import settings
import json_logging
from utils.settings import settings
#from api.debug.router import router as debug
from api.user.router import router as user
from api.otp.router import router as otp
from api.bss.router import router as bss

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Galleon Middleware API",
    description="API microservice for Galleon middleware project",
    version="0.0.1",
    redoc_url=None
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.handlers.RotatingFileHandler(filename=settings.log_path + '/x-ljson.log', maxBytes=5000000, backupCount=10)
logger.addHandler(log_handler)
json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)

@app.on_event("startup")
async def app_startup():
    logger.info("Starting")
    Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def middle(request: Request, call_next):
    """ Wrapper function to manage errors and logging """
    start_time = time.time()
    # The api_key is enforced only if it set to none-empty value
    if not settings.api_key or ("key" in request.query_params and settings.api_key == request.query_params['key']):
        try:
            response = await call_next(request)
        except:
            stack = []
            ex = sys.exc_info()[1]
            if ex:
                for frame, lineno in traceback.walk_tb(ex.__traceback__):
                    # Exclude log entries inside python libraries
                    if "site-packages" not in frame.f_code.co_filename:
                        stack.append({'file': frame.f_code.co_filename, 'function': frame.f_code.co_name, 'line': lineno})
                logger.error(str(ex), extra={'props': {'stack': stack}})
                #print(str(ex))
                #print(stack)
            response = JSONResponse(status_code=500, content={"status": "error", "code": 99, "message": "Internal error"})
    else:
        response = JSONResponse(status_code=400, content={'status': 'error', 'code': 100, 'message': 'Invalid request'})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    logger.info("Processed", extra={'props': {
                "duration": 1000 * (time.time() - start_time),
                'verb': request.method,
                'path': str(request.url.path),
                'http_status': response.status_code}})
    return response


# app.include_router(debug, prefix='/debug')
app.include_router(user, prefix='/api/user')
app.include_router(otp,  prefix='/api/otp')
app.include_router(bss,  prefix='/api/bss')


if __name__ == "__main__":
    # uvicorn.run("main:app", reload=True)
    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port) # type: ignore 
