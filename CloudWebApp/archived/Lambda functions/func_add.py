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
        #get subs table and API request contents
        table = client.Table('subs')
        title = event['title']
        email = event['email']
        #put contents in table
        table.put_item(
                Item={
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


