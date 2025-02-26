import boto3
from PIL import Image
from io import BytesIO
import json

TARGET_BUCKET = 'output-compressor' # Replace with your target S3 bucket name
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(TARGET_BUCKET)

    # Get source bucket and key from the S3 event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    
    response = s3.get_object(Bucket=source_bucket, Key=source_key)
    image_data = response['Body'].read()

    # Resize the image
    with Image.open(BytesIO(image_data)) as img:
        # img = img.resize((200, 200))  # Resize to 800x600
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=35)
        buffer.seek(0)

    target_key = f"resized_{source_key}"
    s3.put_object(
        Bucket=TARGET_BUCKET,
        Key=target_key,
        Body=buffer,
        ContentType="image/jpeg"
    )

    return {
        "statusCode": 200,
        "body": {
            "source_bucket": source_bucket,
            "source_key": source_key
        },
    }
