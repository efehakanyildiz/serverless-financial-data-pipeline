import json
import boto3
from decimal import Decimal
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')

DYNAMO_TABLE = 'WallStreetPrices'
S3_BUCKET = 'wall-street-bronze-efe'
SNS_TOPIC_ARN = 'arn:aws:sns:eu-central-1:137982683099:WallStreetAlerts'

def lambda_handler(event, context):
    table = dynamodb.Table(DYNAMO_TABLE)
    
    try:
        for record in event['Records']:
            payload_str = record['body']
            message_body = json.loads(payload_str, parse_float=Decimal)
            
            # 1. DynamoDB Write & Smart Alert Logic
            for stock in message_body:
                symbol = stock['symbol']
                new_price = stock['price']
                
                try:
                    response = table.get_item(Key={'symbol': symbol})
                    if 'Item' in response:
                        old_price = response['Item']['price']
                        change_percent = abs((new_price - old_price) / old_price) * 100
                        
                        # Alert if volatility > 15%
                        if change_percent > 15:
                            alert_msg = f"ALERT! {symbol} stock showed high volatility. Price changed by {change_percent:.2f}%. Old Price: ${old_price}, New Price: ${new_price}"
                            sns.publish(
                                TopicArn=SNS_TOPIC_ARN,
                                Message=alert_msg,
                                Subject=f"Wall Street Alert: {symbol} Volatility (>15%)"
                            )
                except Exception as e:
                    print(f"Could not fetch historical data for {symbol}: {str(e)}")
                
                # Write latest price to DynamoDB
                table.put_item(
                    Item={
                        'symbol': symbol,
                        'timestamp': stock['timestamp'],
                        'price': new_price
                    }
                )
            
            # 2. Save Raw Data to S3 (Bronze Layer) in NDJSON format
            raw_list = json.loads(payload_str)
            ndjson_content = "\n".join([json.dumps(item) for item in raw_list])
            file_name = f"raw_stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=file_name,
                Body=ndjson_content
            )

        return {
            'statusCode': 200,
            'body': json.dumps('Processing and storage completed successfully')
        }
        
    except Exception as e:
        print(f"System Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
