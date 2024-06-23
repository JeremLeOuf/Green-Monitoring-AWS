from flask import Flask, request, jsonify
import boto3
import datetime
import pandas as pd

app = Flask(__name__)

# Load the CSV file
instance_data = pd.read_csv('https://raw.githubusercontent.com/cloud-carbon-footprint/cloud-carbon-coefficients/main/data/aws-instances.csv')

def get_instance_power(instance_type, utilization):
    instance_row = instance_data[instance_data['InstanceType'] == instance_type].iloc[0]
    idle_power = instance_row['PkgWatt @ Idle']
    max_power = instance_row['PkgWatt @ 100%']
    return idle_power + (max_power - idle_power) * (utilization / 100.0)

def get_memory_power(instance_type):
    instance_row = instance_data[instance_data['InstanceType'] == instance_type].iloc[0]
    mem_idle_power = instance_row['RAMWatt @ Idle']
    mem_10_power = instance_row['RAMWatt @ 10%']
    mem_50_power = instance_row['RAMWatt @ 50%']
    mem_max_power = instance_row['RAMWatt @ 100%'] 

def get_gpu_power():
    pass #TODO

# Useful? Let's see

def get_network_usage():
    # not sure if possible...
    pass

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    instance_type = data['instance_type']
    region = data['region']
    period = data.get('period', 86400)  # Default to 24 hours 
    # TODO: Change that to input of the webform
    
    '''

    Need a conversion function here from user input to seconds
    Also to add in the UI: a dropdown to choose the period (daily/weekly/yearly)

    '''  

    # Initialize AWS clients for the specified region
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
            'Memory': results['MemoryUtilization']  #TODO: Add appropriate logic to calculate memory power usage if available, else use 
        }
    except Exception as e:
        results['InstanceType'] = {'Error': str(e)}

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
