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

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from service.firestore import firestore_service  # Adjust the import based on your project structure
from starlette.responses import JSONResponse

class UserValidationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
    ):
        super().__init__(app)
        self.user_cache = {}

    async def dispatch(self, request: Request, call_next):
        # Skip user validation for the /v1/login and /v1/evaluate-post endpoints
        # TODO(dagadeepansh): updated if condition
        if request.url.path in ["/v1/login", "/v1/evaluate-post", "/v1/create-user"]:
            response = await call_next(request)
            return response
        
        if request.method == "POST":
            body = await request.json()
            user_id = body.get("userId")
            try:
                if not user_id:
                    raise HTTPException(status_code=401, detail="Unauthorized: userId is required")
                
                if user_id not in self.user_cache:
                    user = await firestore_service.get_user(user_id)
                    if not user:
                        raise HTTPException(status_code=401, detail="Unauthorized: userId is invalid")
                    self.user_cache[user_id] = user
                
            except HTTPException as http_exc:
                return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
        
        response = await call_next(request)
        return response

    def get_user_from_cache(self, user_id: str):
        return self.user_cache.get(user_id)