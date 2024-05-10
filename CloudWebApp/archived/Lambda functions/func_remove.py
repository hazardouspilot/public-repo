import boto3
def lambda_handler(event, context):
    #get event type 
    type = event['type']
    client = boto3.resource('dynamodb', region_name='us-east-1')
    #connect to dynamodb
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
        #get subs table and API request contents
        title = event['title']
        email = event['email']
        table = client.Table('subs')
        #remove contents from table
        table.delete_item(
                Key={
                    'song_title': title,
                    'user_email': email
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
                'song_title': title,
                'user_email': email
            }
            }
    return resp
    


