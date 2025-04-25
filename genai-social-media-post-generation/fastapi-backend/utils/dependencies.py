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

from fastapi import Depends, HTTPException
from middlewares.user_validation import UserValidationMiddleware
from fastapi import Request

async def get_current_user(request: Request):
    body = await request.json()  # Get the request body
    user_id = body.get("userId")  # Extract userId from the body
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: userId is required")

    middleware = request.app.user_validation_middleware
    user = middleware.get_user_from_cache(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user