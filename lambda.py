import boto3
import json
import datetime
import pandas as pd

s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')

# Load the CSV file from GitHub
csv_url = 'https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv'
instance_data = pd.read_csv(csv_url)

def get_instance_power(instance_type, utilization):
    instance_row = instance_data[instance_data['InstanceType'] == instance_type].iloc[0]
    idle_power = instance_row['PkgWatt @ Idle']
    max_power = instance_row['PkgWatt @ 100%']
    return idle_power + (max_power - idle_power) * (utilization / 100.0)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    instance_type = body['instance_type']
    region = body['region']
    period = body.get('period', 86400)  #TODO: Should be an input from index.html

    # Initialize AWS client for the specified region
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(seconds=period)

    results = {}

    for metric_name in ['CPUUtilization', 'MemoryUtilization']:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2' if metric_name == 'CPUUtilization' else 'CWAgent',
                MetricName=metric_name,
                Dimensions=[{'Name': 'InstanceType', 'Value': instance_type}],
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=['Average'],
                Unit='Percent'
            )
            datapoints = response['Datapoints']
            if datapoints:
                average_utilization = sum(d['Average'] for d in datapoints) / len(datapoints)
            else:
                average_utilization = 0
            results[metric_name] = average_utilization
        except Exception as e:
            results[metric_name] = {'Error': str(e)}

    try:
        results['InstanceType'] = instance_type
        results['Power'] = {
            'CPU': get_instance_power(instance_type, results['CPUUtilization']),
            'Memory': results['MemoryUtilization']  # Add appropriate logic to calculate memory power usage if available; TODO
            
            # TODO: ADD NETWORKING?
            
            # TODO: ADD GPU?
            
            # TODO: ADD ElectricityMaps API to lookup for the region
        }
    except Exception as e:
        results['InstanceType'] = {'Error': str(e)}

    return {
        'statusCode': 200,
        'body': json.dumps(results),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Allow all origins for CORS
        }
    }
