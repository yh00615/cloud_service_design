import boto3
import random
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    # 커스텀 메트릭 전송
    cloudwatch.put_metric_data(
        Namespace='CustomApplication',
        MetricData=[
            {
                'MetricName': 'OrdersProcessed',
                'Value': random.randint(10, 100),
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'ResponseTime',
                'Value': random.uniform(0.1, 2.0),
                'Unit': 'Seconds',
                'Timestamp': datetime.utcnow()
            }
        ]
    )
    
    return {
        'statusCode': 200,
        'body': 'Custom metrics sent successfully'
    }
