import boto3
import json
import pandas as pd

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log the event object

    try:
        # Extract data from the event payload with default values
        instance_type = event['instance_type']
        period_label = event.get('period_label', '24 hours')  # Default: '24 hours'
        period = float(event.get('period', 86400))  # Default: 86400 seconds (24 hours)
        vcpu_utilization = float(event.get('vcpu_utilization', 10))  # Default: 10%
        rounded_vcpu_utilization = round(vcpu_utilization)

        # Load CSV data
        instance_data = pd.read_csv('https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv')

        # Fetch power consumption data for the given instance type
        try:
            instance_row = instance_data[instance_data['Instance type'] == instance_type].iloc[0]
            min_watts = float(instance_row['PkgWatt @ Idle'].replace(",", "."))
            max_watts = float(instance_row['PkgWatt @ 100%'].replace(",", "."))
        except (KeyError, IndexError) as e:
            # Handle cases where instance type is not found or data is missing
            raise Exception(f"Instance type '{instance_type}' not found or data missing in CSV") from e

        # Calculate average watts, hours in period, and kilowatt-hours
        avg_watts = min_watts + (vcpu_utilization / 100.0) * (max_watts - min_watts)
        hours_in_period = period / 3600.0
        kWh = avg_watts * hours_in_period / 1000.0  # Convert from Wh to kWh

        # Determine the appropriate period label based on the input period
        if period >= 31536000:  # 1 year in seconds
            period_label = '1 year'
        elif period >= 2592000:  # 30 days in seconds
            period_label = '1 month'
        elif period >= 604800:  # 1 week in seconds
            period_label = f"{int(period // 604800)} week" if int(period // 604800) == 1 else f"{int(period // 604800)} weeks"
        elif period >= 86400:  # 1 day in seconds
            period_label = f"{int(period // 86400)} day" if int(period // 86400) == 1 else f"{int(period // 86400)} days"
        elif period >= 3600:  # 1 hour in seconds
            period_label = f"{int(period // 3600)} hour" if int(period // 3600) == 1 else f"{int(period // 3600)} hours"
        else:
            period_label = f"{int(period // 60)} minute" if int(period // 60) == 1 else f"{int(period // 60)} minutes"


        # Create separate dictionaries for each table's data
        min_max_data = [
            {'Metric': 'Min. Watts (@ 0% utilization):', 'Value': f'{min_watts:.2f} W'},
            {'Metric': 'Max Watts (@ 100% utilization):', 'Value': f'{max_watts:.2f} W'}
        ]
        avg_watt_hours_data = [
            {'Metric': 'Average Watts:', 'Value': f'{avg_watts:.2f} W'},
            {'Metric': f'Instance power consumption (kWh) for {period_label}:', 'Value': f'{kWh:.2f} kWh'}
        ]

        # Create the messages for the response
        messages = [
            f"Your {instance_type} instance with an average {rounded_vcpu_utilization}% CPU Utilization over a period of {period_label} would generate an average of {avg_watts:.2f} Watts, consuming a total of {kWh:.2f} Kilowatt-Hours (kWh) over that period."
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