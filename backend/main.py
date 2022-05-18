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

from api.user.router import router as user
from api.otp.router import router as otp
from api.number.router import router as number

from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from utils.db import engine, Base
from starlette.concurrency import iterate_in_threadpool
import json
from utils.api_responses import ApiResponse, Error, Status, ApiException
from fastapi.encoders import jsonable_encoder

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Galleon Middleware API",
    description="API microservice for Galleon middleware project",
    version="0.0.1",
    redoc_url=None,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.handlers.RotatingFileHandler(
    filename=f"{settings.log_path}/x-ljson.log", maxBytes=5000000, backupCount=10
)
logger.addHandler(log_handler)
json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)


@app.on_event("startup")
async def app_startup():
    logger.info("Starting")
    Base.metadata.create_all(bind=engine)
    openapi_schema = app.openapi()
    paths = openapi_schema["paths"]
    for path in paths:
        for method in paths[path]:
            responses = paths[path][method]["responses"]
            if responses.get("422"):
                responses.pop("422")
    app.openapi_schema = openapi_schema


@app.on_event("shutdown")
async def app_shutdown():
    logger.info("Application shutdown")


async def capture_body(request: Request):
    request.state.request_body = {}
    if (
        request.method == "POST"
        and request.headers.get("content-type") == "application/json"
    ):
        request.state.request_body = await request.json()


@app.exception_handler(HTTPException)
async def my_exception_handler(_, exception):
    return JSONResponse(content=exception.detail, status_code=exception.status_code)


@app.middleware("http")
async def middle(request: Request, call_next):
    """Wrapper function to manage errors and logging"""
    if request.url._url.endswith("/docs") or request.url._url.endswith("/openapi.json"):
        return await call_next(request)

    start_time = time.time()
    response_body: str = ""
    # The api_key is enforced only if it set to none-empty value
    if not settings.api_key or (
        "key" in request.query_params
        and settings.api_key == request.query_params["key"]
    ):
        try:
            response = await call_next(request)
            raw_response = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(raw_response))
            response_body = json.loads(b"".join(raw_response))

        except ApiException as ex:
            response = JSONResponse(
                status_code=ex.status_code,
                content=jsonable_encoder(
                    ApiResponse(status=Status.failed, errors=[ex.error])
                ),
            )
        except:
            ex = sys.exc_info()[1]
            if ex:
                stack = [
                    {
                        "file": frame.f_code.co_filename,
                        "function": frame.f_code.co_name,
                        "line": lineno,
                    }
                    for frame, lineno in traceback.walk_tb(ex.__traceback__)
                    if "site-packages" not in frame.f_code.co_filename
                ]
                logger.error(str(ex), extra={"props": {"stack": stack}})
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(
                    ApiResponse(
                        status=Status.failed,
                        errors=[Error(type="internal", code=99, message=str(ex))],
                    )
                ),
            )

    else:
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ApiResponse(
                    status=Status.failed,
                    errors=[
                        Error(type="bad request", code=100, message="invalid request")
                    ],
                )
            ),
        )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    logger.info(
        "Processed",
        extra={
            "props": {
                "duration": 1000 * (time.time() - start_time),
                "verb": request.method,
                "path": str(request.url.path),
                "response": {
                    "headers": dict(response.headers.items()),
                    "body": response_body,
                },
                "request": {
                    "headers": dict(request.headers.items()),
                    "query_params": dict(request.query_params.items()),
                    "body": request.state.request_body,
                },
                "http_status": response.status_code,
            }
        },
    )
    return response


app.include_router(user, prefix="/api/user", dependencies=[Depends(capture_body)])
app.include_router(otp, prefix="/api/otp", dependencies=[Depends(capture_body)])
app.include_router(number, prefix="/api/number", dependencies=[Depends(capture_body)])


if __name__ == "__main__":
    # uvicorn.run("main:app", reload=True)
    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port)  # type: ignore
