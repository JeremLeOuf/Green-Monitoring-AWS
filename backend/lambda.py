import boto3
import json
import pandas as pd
import datetime

# Load the CSV file once
instance_data = pd.read_csv(
    'https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log the event object

    try:
        # Extract instance_type, region, period, and vcpu_utilization from the event payload
        instance_type = event['instance_type']
        
        # Default period to 86400 if not provided
        period = float(event.get('period', 86400))
        
        # Default vCPU utilization to 10% if not provided
        vcpu_utilization = float(event.get('vcpu_utilization', 10))

        # Fetch power consumption data for the given instance type
        instance_row = instance_data[instance_data['Instance type']
                                     == instance_type].iloc[0]
        min_watts = instance_row['PkgWatt @ Idle']
        max_watts = instance_row['PkgWatt @ 100%']

        # Convert the watts values pulled from the CSV to actual floats
        min_watts = float(min_watts.replace(",", "."))
        max_watts = float(max_watts.replace(",", "."))

        # Calculate the average watts
        avg_watts = min_watts + \
            (vcpu_utilization / 100.0) * (max_watts - min_watts)

        # Calculate the number of hours in the period
        hours_in_period = period / 3600.0

        # Compute watt-hours
        watt_hours = avg_watts * hours_in_period

        # Create the table data
        table_data = [
            {'Metric': 'Min. Watts:', 'Value': f'{min_watts:.2f} W'},
            {'Metric': 'Max Watts:', 'Value': f'{max_watts:.2f} W'},
            {'Metric': 'Average Watts:', 'Value': f'{avg_watts:.2f} W'},
            {'Metric': f'Watt-Hour used for running the instance during {hours_in_period:.0f} hours:', 'Value': f'{watt_hours:.2f} Wh'},
        ]

        # Create the messages array
        messages = [
            f"Your `{instance_type}` instance with an average {vcpu_utilization}% CPU Utilization over a period of {hours_in_period:.0f} hour(s) would generate an average of {avg_watts:.2f} Watts (W), consuming a total of {watt_hours:.2f} Watt-Hours (Wh) over that period.",
        ]

        results = {
            'messages': messages,
            'table_data': table_data,
        }

        return {
            'statusCode': 200,
            'body': json.dumps(results),
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
