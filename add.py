import boto3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:8000'
)
table = dynamodb.Table("Users")

password = "Admin@123"  # temp password

table.put_item(
    Item={
        "email": "admin3@example.com",
        "username": "admin3",
        "password": generate_password_hash(password),
        "role": "admin",
        "status": "active",
        "createdAt": datetime.now(timezone.utc).isoformat()
    },
    ConditionExpression="attribute_not_exists(email)"
)

print("✅ Admin created")
print("🔑 Login password:", password)
