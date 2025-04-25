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

from datetime import datetime

# Simulate the Event object
class MockDocumentSnapshot:
    def __init__(self, data, doc_id):
        self._data = data
        self._id = doc_id

    def to_dict(self):
        return self._data

    @property
    def id(self):
        return self._id

class MockEvent:
    def __init__(self, document_snapshot):
        self.data = document_snapshot

class MockContext:
    def __init__(self, resource):
        self.resource = resource

def handle_request(data, context):
    from evaluate_post_final import process_new_document
    process_new_document(data, context)
    return 'Function executed successfully', 200

def main():
    postId = 'TwBcO6o1hikiPD6oDMC3'
    
    # Create a mock document snapshot for evaluation
    event_data = {
        'userId': '8uXa7nV8GofheHlamv7J',
        'generatedImageUrl': 'gs://1003801603843_marketing_content_generation_inputs/Artefacts/Generated_Images/reqId_0509_3.png',
        'postCreationTime': datetime(2024, 11, 21, 15, 2, 0),
        'requestId': 'reqId_0509',
        'postStatus': 'original',
        'postVote': 0,
        'evaluationStatus': 'pending',
        'finalImageUrl': 'gs://1003801603843_marketing_content_generation_inputs/Artefacts/Final_Posts/final_reqId_0509_3.png'
    }

    # Create a mock document snapshot
    document_snapshot = MockDocumentSnapshot(data=event_data, doc_id=postId)
    event = MockEvent(document_snapshot=document_snapshot)

    mock_context = MockContext(resource=f"projects/project-id/databases/(default)/documents/posts/{postId}")
    
    # Call the evaluate_post function directly
    handle_request(event, mock_context)
    print(f"Evaluation for postId {postId} completed.")

# Run the test
if __name__ == "__main__":
    main()