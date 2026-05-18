import yfinance as yf
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Initialize SQS client
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.eu-central-1.amazonaws.com/137982683099/WallStreetQueue'
    
    tickers = ["AAPL", "NVDA", "TSLA", "META", "AMZN"]
    results = []

    try:
        # 1. Fetch market data
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                results.append({
                    "symbol": ticker,
                    "price": round(current_price, 2),
                    "timestamp": datetime.now().isoformat()
                })
        
        # 2. Send data to SQS as a single JSON payload
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(results)
        )
        
        print(f"Success! Data sent to SQS. Message ID: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data successfully sent to SQS queue',
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
