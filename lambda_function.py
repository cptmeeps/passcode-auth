import json
import boto3

dynamodb = boto3.client('dynamodb')
table_name = 'auth'

def scan_dynamodb(payload, lookup_keys):
  filtered_payload = {k: v for k, v in payload.items() if k in lookup_keys}
  filter_expression = ' and '.join([f"{k} = :{k}" for k in filtered_payload.keys()])
  expression_attribute_values = {f":{k}": {'S': v} for k, v in filtered_payload.items()}
  print(f"Expression attribute values: {expression_attribute_values}")

  scan = dynamodb.scan(
    TableName=table_name,
    FilterExpression=filter_expression,
    ExpressionAttributeValues=expression_attribute_values
  )
  print(f"Scan result: {json.dumps(scan, indent=2)}")

  if scan['Items']:
    print("Items found")
    return scan['Items']
  else:
    print("No items found")
    return False


def lambda_handler(event, context):
  print(f" received: {json.dumps(event, indent=2)}")
  data = json.loads(event['body'])
  action = data['action']
  payload = data['payload']
  print(f" received: {event}")
  response = {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }

  if action == 'passcode_lookup':
    lookup_keys = ['passcode', 'site']
    items = scan_dynamodb(payload, lookup_keys)
    if items:
      response['body'] = json.dumps(
      {
        'action_result': 'true', 
        'payload': {
          'lookup_message': 'matching_passcode_found'
        }
      }
    )

    else:
      response['body'] = json.dumps(
      {
        'action_result': 'false', 
        'payload': {
          'lookup_message': 'no_matching_passcode'
        }
      }
    )
    
  print(f"Final response: {json.dumps(response, indent=2)}")
  return response
