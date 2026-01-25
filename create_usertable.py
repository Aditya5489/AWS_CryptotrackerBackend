import boto3


dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:8000'
)


table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {'AttributeName': 'email', 'KeyType': 'HASH'}  
    ],
    AttributeDefinitions=[
        {'AttributeName': 'email', 'AttributeType': 'S'}  
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)


table.meta.client.get_waiter('table_exists').wait(TableName='Users')
print("Users table created successfully!")
