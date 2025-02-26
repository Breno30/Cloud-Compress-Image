import json
from PIL import Image

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world1"
        }),
    }
