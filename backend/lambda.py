import boto3
import json
import pandas as pd

# Load the CSV file once
instance_data = pd.read_csv('https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log the event object

    try:
        # Extract instance_type, period, and vcpu_utilization from the event payload
        instance_type = event['instance_type']
        period = event.get('period', 86400)  # Default period to 86400 if not provided
        vcpu_utilization = event.get('vcpu_utilization', 10)  # Default vCPU utilization to 10% if not provided

        # Fetch power consumption data for the given instance type
        instance_row = instance_data[instance_data['Instance type'] == instance_type].iloc[0]
        min_watts = instance_row['PkgWatt @ Idle']
        max_watts = instance_row['PkgWatt @ 100%']

        # Convert the watts values pulled from the CSV to actual floats
        min_watts = float(min_watts.replace(",", "."))
        max_watts = float(max_watts.replace(",", "."))

        # Calculate the average watts
        avg_watts = min_watts + (vcpu_utilization / 100.0) * (max_watts - min_watts)

        # Calculate the number of hours in the period
        hours_in_period = period / 3600.0

        # Compute watt-hours
        watt_hours = avg_watts * hours_in_period

        # Create the table using string formatting
        table_data = [
            {'Metric': 'Average Min Watts', 'Value': f'{min_watts:.2f}'},
            {'Metric': 'Average Max Watts', 'Value': f'{max_watts:.2f}'},
            {'Metric': 'Average Watts', 'Value': f'{avg_watts:.2f}'},
            {'Metric': 'Watt Hours', 'Value': f'{watt_hours:.2f}'},
        ]

        # Create the message string
        message = f"Your {instance_type} instance with an average {vcpu_utilization}% utilization over {hours_in_period:.2f} hours generated an average of {avg_watts:.2f} watts, consuming a total of {watt_hours:.2f} watt-hours."

        # Combine table and message after both are defined
        results = {
            'message': message,
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
