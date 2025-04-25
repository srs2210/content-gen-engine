"""
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

from http import HTTPStatus
from time import perf_counter
from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import traceback


class TrackerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Middleware to show incoming request and track time taken to process the request"""
        request_uuid = str(uuid4())
        logger.info(f"[{request_uuid}] Incoming request to {request.url.path}")
        start_time = perf_counter()
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            """This will handle all errors not raised in the code (all the errors not raised using HTTPException)"""
            trace = traceback.format_exc()
            logger.error(f"[{request_uuid}] [STACK TRACE]: {trace}")
            response = JSONResponse(
                content={"message": str(e)},
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        finally:
            end_time = perf_counter()
            logger.info(f"[{request_uuid}] Elapsed time: {end_time- start_time}")
            return response
