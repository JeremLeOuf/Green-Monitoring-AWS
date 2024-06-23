import boto3
import json
import pandas as pd


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log the event object

    try:
        # Extract data from the event payload with default values
        instance_type = event['instance_type']
        period = float(event.get('period', 86400))  # Default: 86400 seconds (24 hours)
        vcpu_utilization = float(event.get('vcpu_utilization', 10))  # Default: 10%

        # Load CSV data (assuming the file is accessible by the Lambda function)
        instance_data = pd.read_csv('aws-instances.csv')  # Assuming file exists locally

        # Fetch power consumption data for the given instance type
        try:
            instance_row = instance_data[instance_data['Instance type'] == instance_type].iloc[0]
            min_watts = float(instance_row['PkgWatt @ Idle'].replace(",", "."))
            max_watts = float(instance_row['PkgWatt @ 100%'].replace(",", "."))
        except (KeyError, IndexError):
            # Handle cases where instance type is not found or data is missing
            raise Exception(f"Instance type '{instance_type}' not found or data missing in CSV")

        # Calculate average watts, hours in period, and watt-hours
        avg_watts = min_watts + (vcpu_utilization / 100.0) * (max_watts - min_watts)
        hours_in_period = period / 3600.0
        watt_hours = avg_watts * hours_in_period

        # Create separate dictionaries for each table's data
        min_max_data = {
            'Metric': 'Min. Watts:',
            'Value': f'{min_watts:.2f} W'
        }, {
            'Metric': 'Max Watts:',
            'Value': f'{max_watts:.2f} W'
        }
        avg_watt_hours_data = {
            'Metric': 'Average Watts:',
            'Value': f'{avg_watts:.2f} W'
        }, {
            'Metric': f'Watt-Hour used for running the instance during {hours_in_period:.0f} hours:',
            'Value': f'{watt_hours:.2f} Wh'
        }

        # Create the messages for the response
        messages = [
            f"Your `{instance_type}` instance with an average {vcpu_utilization}% CPU Utilization over a period of {hours_in_period:.0f} hour(s) would generate an average of {avg_watts:.2f} Watts (W), consuming a total of {watt_hours:.2f} Watt-Hours (Wh) over that period."
        ]

        # Combine results into a dictionary
        results = {
            'messages': messages,
            'table_data': {
                'min_max': min_max_data,
                'avg_watt_hours': avg_watt_hours_data
            }
        }

        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
