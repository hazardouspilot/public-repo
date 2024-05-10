import boto3
def lambda_handler(event, context):
    #get event type    
    type = event['type']
    #connect to dynamodb
    client = boto3.resource('dynamodb', region_name='us-east-1')

    if type=="options":
        resp = {
         'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': {
                'message': 'All is good'
            }
        }
    else:
        #get login table and API request contents
        table = client.Table('login')
        email = event['email']
        username = event['username']
        password = event['password']
        #retrieve row from table with matching email, if it exists
        response = table.get_item(
            Key={
                'email': email
            }
        )
        #if the email does not exist in login table
        if 'Item' not in response:
            #upload new user details to login table
            table.put_item(
                Item={
                    'email': email,
                    'user_name': username,
                    'password': password
                }
            )
            #successful response
            resp = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': {
                'email': email,
                'user_name': username,
                'password': password,
                'message' : 'user details added to login table'
            }
            }
        #if email was in the login table
        else:
            #unsuccessful response
            resp = {
            'statusCode': 409,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': {
                'message': 'Email already exists'
            }
        }
    return resp