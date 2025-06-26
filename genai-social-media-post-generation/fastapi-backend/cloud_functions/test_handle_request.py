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

import asyncio
from main import handle_request
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

def main():
    # requestId = f'reqId_{datetime.now().strftime("%H%M")}'
    requestId = "HJuMlGxtNV93cpxffc9q"

    # Create a mock document snapshot
    event_data = {
        'userId': 'oiNBejsW4vDDHLHdcWk2',
        'requestConfig': {
            'postDescription': 'Create a post to promote an ice cream giveaway. To participate, customers simply need to fill out a survey at privy.sg/icecream',
            'subject': 'Asian man holding an ice cream',
            'artStyle': 'Photorealistic',
            'signOff': 'XYZ Associates',
            'postCount': 4,
            'aspectRatio': 'square',
            'backgroundColor': None,
            'isRecruitmentRelated': False,
            'isCharityRelated': False,
            'requestTitle': 'Ice Cream Giveaway'
        },
        'status': 'pending',
        'requestDate': datetime.now(),
    }

    # Create a mock document snapshot
    document_snapshot = MockDocumentSnapshot(data=event_data, doc_id=requestId)
    event = MockEvent(document_snapshot=document_snapshot)

    mock_context = MockContext(resource=f"projects/project-id/databases/(default)/documents/requests/{requestId}")

    # Call the function with mock data and context
    data = event_data
    
    # Call the handle_request function directly
    response = handle_request(data, mock_context)
    print(response)

# Run the test
if __name__ == "__main__":
    main()