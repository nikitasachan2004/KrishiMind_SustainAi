"""
KrishiMind AI - AWS Lambda Handler
Mangum adapter for FastAPI on Lambda
"""

import sys
from pathlib import Path

# Add project paths for Lambda environment
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, '/var/task')

from mangum import Mangum
from cloud.api.app import app

# Create Mangum adapter for AWS Lambda
# This wraps FastAPI for Lambda/API Gateway compatibility
handler = Mangum(
    app,
    lifespan="auto",
    api_gateway_base_path=None
)


# For local testing
if __name__ == "__main__":
    # Simulate Lambda event
    test_event = {
        "httpMethod": "POST",
        "path": "/predict/crop-plan",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": '{"district": "Guntur", "season": "Kharif", "area": 10.0}'
    }
    
    test_context = {}
    
    response = handler(test_event, test_context)
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")
