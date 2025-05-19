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

from google.cloud.firestore import CollectionReference, AsyncClient, AsyncCollectionReference
from utils.constants import *
from typing import List, Optional
from utils.types import *
from loguru import logger
from datetime import datetime
import pytz

class FirestoreService:
    def __init__(self) -> None:
        self.db = AsyncClient(project=PROJECT_ID, database=FIRESTORE_ID)

    @property
    async def client(self):
        return self.db

    @property
    async def batch(self):
        return await self.db.batch()

    @property
    async def task_table(self) -> CollectionReference:
        return await self.db.collection("task")

    @property
    async def users_collection(self) -> AsyncCollectionReference:
        return self.db.collection("users")

    @property
    async def requests_collection(self) -> AsyncCollectionReference:
        return self.db.collection("requests")

    @property
    async def posts_collection(self) -> AsyncCollectionReference:
        return self.db.collection("posts")

    @property
    async def templates_collection(self) -> AsyncCollectionReference:
        return self.db.collection("templates")

    # CRUD operations for Users
    async def create_user(self, user: User):
        users_collection = await self.users_collection
        await users_collection.add(user.model_dump())

    async def get_user(self, user_id: str) -> Optional[User]:
        user_collection = await self.users_collection
        doc = await user_collection.document(user_id).get()
        if not doc.exists:
            return None
        user_object = doc.to_dict()
        user_object["userId"] = doc.id  
        return User(**user_object)
    
    async def get_user_by_email_and_pin(self, email: str, pin: str) -> Optional[User]:
        user_collection = await self.users_collection
        query = user_collection.where("email", "==", email).where("pin", "==", pin)
        docs = await query.get()
        if not docs:
            return None
        user_object = docs[0].to_dict()
        user_object["userId"] = docs[0].id
        return User(**user_object)

    async def update_user(self, user_id: str, user: User):
        await self.users_collection.document(user_id).set(user.model_dump(), merge=True)

    async def update_user_sign_off(self, user_id: str, sign_off: str, is_sign_off_remembered: bool):
        users_collection = await self.users_collection
        try:
            if is_sign_off_remembered:
                await users_collection.document(user_id).update({"signOff": sign_off})
            else:
                await users_collection.document(user_id).update({"signOff": ""})
            return True
        except Exception as e:
            logger.error(f"Error updating user sign-off: {e}")
            return False

    async def delete_user(self, user_id: str):
        await self.users_collection.document(user_id).delete()

    # CRUD operations for Requests
    async def create_request(self, user_id: str, request_config: RequestConfig):
        requests_collection = await self.requests_collection
        singapore_tz = pytz.timezone('Asia/Singapore')
        request_date = datetime.now(singapore_tz)
        _, new_request_ref = await requests_collection.add({
            "userId": user_id,
            "requestConfig": request_config.model_dump(),
            "requestDate": request_date,
            "status": RequestStatus.pending
        })
        return new_request_ref.id

    async def get_request(self, request_id: str) -> Optional[Request]:
        requests_collection = await self.requests_collection
        doc = await requests_collection.document(request_id).get()
        request_object = doc.to_dict()
        request_object["requestId"] = doc.id
        return Request(**request_object) if doc.exists else None
    
    def add_id_to_request(self, request: dict):
        output = request.to_dict()
        output["requestId"] = request.id
        return output
    
    async def get_requests_by_user_id(self, user_id: str) -> List[Request]:
        requests_collection = await self.requests_collection
        query = requests_collection.where("userId", "==", user_id)
        docs = await query.get()
        if not docs:
            return []
        requests = [Request(**self.add_id_to_request(doc)) for doc in docs]
        return sorted(requests, key=lambda x: x.requestDate, reverse=True)

    async def update_request(self, request_id: str, request: Request):
        request_collection = await self.requests_collection
        await request_collection.document(request_id).set(request.model_dump(), merge=True)

    async def delete_request(self, request_id: str):
        request_collection = await self.requests_collection
        await request_collection.document(request_id).delete()

    async def update_request_status(self, request_id: str, status: RequestStatus):
        try:
            request_collection = await self.requests_collection
            await request_collection.document(request_id).update({"status": status})
            return True
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
            return False
        
    # CRUD operations for Posts
    async def create_post(self, post: Post):
        posts_collection = await self.posts_collection
        await posts_collection.add(post.model_dump())

    async def get_post(self, post_id: str) -> Optional[Post]:
        posts_collection = await self.posts_collection
        doc = await posts_collection.document(post_id).get()
        post_object = doc.to_dict()
        post_object["postId"] = doc.id
        return Post(**post_object) if doc.exists else None
    
    def add_id_to_post(self, post: dict):
        output = post.to_dict()
        output["postId"] = post.id
        return output
    
    async def get_posts_by_request_id(self, request_id: str) -> List[Post]:
        posts_collection = await self.posts_collection
        query = posts_collection.where("requestId", "==", request_id)
        docs = await query.get()
        posts = [Post(**self.add_id_to_post(doc)) for doc in docs if doc.to_dict()["evaluationStatus"] != "error"]
        error_count = len(docs) - len(posts)
        return posts, error_count

    async def update_post(self, post_id: str, post: Post):
        posts_collection = await self.posts_collection
        await posts_collection.document(post_id).set(post.model_dump(), merge=True)

    async def delete_post(self, post_id: str):
        posts_collection = await self.posts_collection
        await posts_collection.document(post_id).delete()

    async def update_post_vote(self, post_id: str, vote: PostVote):
        try:
            posts_collection = await self.posts_collection
            await posts_collection.document(post_id).update({"postVote": vote})
            return True
        except Exception as e:
            logger.error(f"Error updating post vote: {e}")
            return False

firestore_service = FirestoreService()
