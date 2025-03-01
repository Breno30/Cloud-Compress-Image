import boto3
from PIL import Image
from io import BytesIO
import json
import base64
import re

TARGET_BUCKET = 'output-compressor' # Replace with your target S3 bucket name
s3 = boto3.client('s3')

def lambda_handler(event, context):
    if 'Records' in event and event['Records'][0]['eventSource'] == 'aws:s3':
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        image_data = response['Body'].read()
    if 'queryStringParameters' in event and 'image_s3_key' in event['queryStringParameters']:
        image_s3_key = event['queryStringParameters']['image_s3_key']
        image_s3_bucket = event['queryStringParameters']['image_s3_bucket'] = event['queryStringParameters']['image_s3_key']
        response = s3.get_object(Bucket=image_s3_bucket, Key=image_s3_key)
        image_data = response['Body'].read()
    else:
        try:
            body = event['body']
            image_data = base64.b64decode(body)
            match = re.search(rb'\r?\n\r?\n(.*)----------------------------', image_data, re.DOTALL)
            image_data = match.group(1).strip()

        except:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid image data in request'})
            }

    # Resize the image
    with Image.open(BytesIO(image_data)) as img:
        # img = img.resize((200, 200))  # Resize to 800x600
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=35)
        buffer.seek(0)

    target_key = f"resized_image_{context.aws_request_id}.jpg"
    s3.put_object(
        Bucket=TARGET_BUCKET,
        Key=target_key,
        Body=buffer,
        ContentType="image/jpeg"
    )

    # Generate presigned URL for the uploaded image
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': TARGET_BUCKET, 'Key': target_key},
        ExpiresIn=3600  # URL expires in 1 hour
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Image processed successfully",
            "target_bucket": TARGET_BUCKET,
            "target_key": target_key,
            "image_url": url
        })
    }
