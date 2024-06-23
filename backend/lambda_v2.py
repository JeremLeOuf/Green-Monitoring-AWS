import boto3
import json
import pandas as pd

# Load the CSV file once
instance_data = pd.read_csv('https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log the event object
    
    try:
        # Extract instance_type, region, period, and vcpu_utilization from the event payload
        instance_type = event['instance_type']
        region = event['region']
        period = event.get('period', 86400)  # Default period to 86400 if not provided
        vcpu_utilization = event.get('vcpu_utilization', 10)  # Default vCPU utilization to 10% if not provided

        # Fetch power consumption data for the given instance type
        instance_row = instance_data[instance_data['InstanceType'] == instance_type].iloc[0]
        min_watts = instance_row['PkgWatt @ Idle']
        max_watts = instance_row['PkgWatt @ 100%']

        # Calculate the average watts
        avg_watts = min_watts + (vcpu_utilization / 100.0) * (max_watts - min_watts)

        results = {
            'instance_type': instance_type,
            'region': region,
            'period': period,
            'min_watts': min_watts,
            'max_watts': max_watts,
            'vcpu_utilization': vcpu_utilization,
            'avg_watts': avg_watts
        }

        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }

    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameter: {}'.format(str(e))})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
