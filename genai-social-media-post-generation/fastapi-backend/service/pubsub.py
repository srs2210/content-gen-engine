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

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.publisher.futures import Future
from concurrent.futures import TimeoutError
from utils.constants import PROJECT_ID
from typing import Dict, Any, Optional
from loguru import logger
import json
import asyncio

class PubSubService:
    def __init__(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.project_path = f"projects/{PROJECT_ID}"

    def get_topic_path(self, topic_name: str) -> str:
        return self.publisher.topic_path(PROJECT_ID, topic_name)

    def get_subscription_path(self, subscription_name: str) -> str:
        return self.subscriber.subscription_path(PROJECT_ID, subscription_name)

    async def publish_message(
        self, 
        topic_name: str, 
        message_data: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publishes a message to a Pub/Sub topic
        Returns: The message ID
        """
        try:
            topic_path = self.get_topic_path(topic_name)
            message_json = json.dumps(message_data)
            message_bytes = message_json.encode('utf-8')
            
            # Create a Future to handle the async publish
            future: Future = self.publisher.publish(
                topic_path,
                data=message_bytes,
                **attributes if attributes else {}
            )
            
            # Wait for the publish to complete
            message_id = await asyncio.wrap_future(future)
            logger.info(f"Published message with ID: {message_id} to {topic_name}")
            return message_id

        except Exception as e:
            logger.error(f"Error publishing message to {topic_name}: {e}")
            raise

    async def create_subscription(
        self,
        topic_name: str,
        subscription_name: str,
        ack_deadline_seconds: int = 60
    ) -> None:
        """Creates a new subscription to a topic"""
        try:
            topic_path = self.get_topic_path(topic_name)
            subscription_path = self.get_subscription_path(subscription_name)
            
            subscription = await asyncio.to_thread(
                self.subscriber.create_subscription,
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                    "ack_deadline_seconds": ack_deadline_seconds,
                }
            )
            logger.info(f"Created subscription: {subscription.name}")
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    async def delete_subscription(self, subscription_name: str) -> None:
        """Deletes a subscription"""
        try:
            subscription_path = self.get_subscription_path(subscription_name)
            await asyncio.to_thread(
                self.subscriber.delete_subscription,
                request={"subscription": subscription_path}
            )
            logger.info(f"Deleted subscription: {subscription_path}")
            
        except Exception as e:
            logger.error(f"Error deleting subscription: {e}")
            raise

    async def subscribe_to_messages(
        self,
        subscription_name: str,
        callback,
        timeout: Optional[float] = None
    ) -> None:
        """
        Subscribes to messages from a subscription
        callback: async function that processes the message
        """
        subscription_path = self.get_subscription_path(subscription_name)

        async def process_message(message):
            try:
                # Decode message data
                message_json = message.data.decode('utf-8')
                message_data = json.loads(message_json)
                
                # Process message with callback
                await callback(message_data, message.attributes)
                
                # Acknowledge the message
                message.ack()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                message.nack()

        def callback_wrapper(message):
            asyncio.create_task(process_message(message))

        try:
            streaming_pull_future = self.subscriber.subscribe(
                subscription_path,
                callback=callback_wrapper
            )
            logger.info(f"Listening for messages on {subscription_path}")
            
            # Wait for specified timeout or indefinitely
            with self.subscriber:
                try:
                    streaming_pull_future.result(timeout=timeout)
                except TimeoutError:
                    streaming_pull_future.cancel()
                    logger.info("Streaming pull future cancelled")
                    
        except Exception as e:
            logger.error(f"Error in subscription: {e}")
            raise

pubsub_service = PubSubService()
