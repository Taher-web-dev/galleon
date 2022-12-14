""" FastApi Main module """

import time
import traceback
from typing import Any

# import uvicorn

# from settings import settings
import json_logging
from utils.settings import settings
from api.user.router import router as user
from api.otp.router import router as otp
from api.number.router import router as number
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, Depends, status
from utils.logger import logger
from fastapi.responses import JSONResponse
from starlette.concurrency import iterate_in_threadpool
import json
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from api.models.response import ApiResponse, ApiException
from api.models.data import Error, Status
from api.models import examples as api_examples


json_logging.init_fastapi(enable_json=True)

app = FastAPI(
    title="Galleon Middleware API",
    description="""### API microservice for Galleon middleware project
#### Notes:

* APIs with the 🔒 'lock' icon, require the http header `Authorization: Bearer ABC`.
* Invoke the login api and use the returned access token in the Authorization form button in the upper right section of this documentation.
* All the api responses are in application/json format.
* All apis also return X-Server-Time as  http header response, the value of which is iso-formatted server timestamp.
    """,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=[
        {
            "name": "otp",
            "description": "One-Time-Password operations (currently SMS-only)",
        },
        {
            "name": "user",
            "description": "User, registration and profile management operations",
        },
        {"name": "number", "description": "Zain backend `number` (msisdn) operations"},
    ],
    version="0.0.1",
    redoc_url=None,
)

json_logging.init_request_instrument(app)


@app.on_event("startup")
async def app_startup():
    logger.info("Starting")
    openapi_schema = app.openapi()
    paths = openapi_schema["paths"]
    for path in paths:
        if path == "/api/number/status":
            for method in paths[path]:
                responses = paths[path][method]["responses"]
                if responses.get("403"):
                    responses.pop("403")
                if responses.get("401"):
                    responses.pop("401")
        if path in ["/api/user/logout", "/api/user/delete"]:
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


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(_, exception):
    return JSONResponse(content=exception.detail, status_code=exception.status_code)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_, exception: SQLAlchemyError):
    raise ApiException(
        status_code=(
            status.HTTP_409_CONFLICT
            if "UniqueViolation" not in str(exception)
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        error=Error(type="SQLAlchemyError", code=543, message=str(exception)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    err = jsonable_encoder({"detail": exc.errors()})["detail"]
    raise ApiException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=Error(code=422, type="validation", message=err),
    )


@app.get("/", include_in_schema=False, dependencies=[Depends(capture_body)])
async def root():
    """Micro-service card identifier"""
    return {
        "name": "GMW",
        "type": "microservice",
        "decription": "Galleon Middleware for Self-service",
        "status": "Up and running",
        "date": datetime.now(),
    }


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
        exception_data: dict[str, Any] | None = None
        try:
            response = await call_next(request)
            raw_response = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(raw_response))
            response_body = json.loads(b"".join(raw_response))
        except ApiException as ex:
            response = JSONResponse(
                status_code=ex.status_code,
                content=jsonable_encoder(
                    ApiResponse(status=Status.failed, error=ex.error)
                ),
            )
            stack = [
                {
                    "file": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line": lineno,
                }
                for frame, lineno in traceback.walk_tb(ex.__traceback__)
                if "site-packages" not in frame.f_code.co_filename
            ]
            exception_data = {"props": {"exception": str(ex), "stack": stack}}
            response_body = json.loads(response.body.decode())

        except Exception as ex:
            # ex = sys.exc_info()[1]
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
                exception_data = {"props": {"exception": str(ex), "stack": stack}}
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(
                    ApiResponse(
                        status=Status.failed,
                        error=Error(type="internal", code=99, message=str(ex)),
                    )
                ),
            )
            response_body = json.loads(response.body.decode())
    else:
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ApiResponse(
                    status=Status.failed,
                    error=Error(
                        type="bad request", code=100, message="Invalid request."
                    ),
                )
            ),
        )
        response_body = json.loads(response.body.decode())

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Server-Time"] = datetime.now().isoformat()

    extra = {
        "props": {
            "duration": 1000 * (time.time() - start_time),
            "request": {
                "verb": request.method,
                "path": str(request.url.path),
                "headers": dict(request.headers.items()),
                "query_params": dict(request.query_params.items()),
                "body": request.state.request_body
                if hasattr(request.state, "request_body")
                else {},
            },
            "response": {
                "headers": dict(response.headers.items()),
                "body": response_body,
            },
            "http_status": response.status_code,
        }
    }

    if exception_data:
        extra["props"]["exception"] = exception_data
    if hasattr(request.state, "request_body"):
        extra["props"]["request"]["body"] = request.state.request_body
    if response_body:
        extra["props"]["response"]["body"] = response_body

    logger.info("Processed", extra=extra)

    return response


app.include_router(
    user,
    prefix="/api/user",
    dependencies=[Depends(capture_body)],
    tags=["user"],
    responses=api_examples.general_response([api_examples.validation]),
)
app.include_router(
    otp,
    prefix="/api/otp",
    dependencies=[Depends(capture_body)],
    tags=["otp"],
    responses=api_examples.general_response([api_examples.validation]),
)
app.include_router(
    number,
    prefix="/api/number",
    dependencies=[Depends(capture_body)],
    tags=["number"],
    responses=api_examples.general_response(
        [api_examples.validation, api_examples.not_authenticated]
    ),
)


@app.get("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.post("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.put("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.patch("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.delete("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
async def catchall():
    raise ApiException(
        status_code=status.HTTP_404_NOT_FOUND,
        error=Error(
            type="catchall", code=501, message="Requested method or path is invalid"
        ),
    )


# if __name__ == "__main__":
# uvicorn.run("main:app", reload=True)
#    uvicorn.run(app, host=settings.listening_host, port=settings.listening_port)  # type: ignore
