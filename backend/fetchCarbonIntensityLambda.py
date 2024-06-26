import requests


def lambda_handler(event, context):
    region = event['region']
    region_mapping = {
        'eu-central-1': 'DE',
        'eu-west-1': 'IE',
        'eu-west-2': 'GB',
        'eu-west-3': 'FR',
        'eu-north-1': 'SE-SE3'
    }

    if region not in region_mapping:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid region'})
        }

    api_url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={
        region_mapping[region]}"
    headers = {
        'auth-token': 'mH1ux820u6aJMbHz3svz1AD3'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Adjust according to the API response
        carbon_intensity = data['carbonIntensity']

        return {
            'statusCode': 200,
            'body': json.dumps({'carbon_intensity': carbon_intensity})
        }
    except requests.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
