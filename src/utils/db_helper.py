import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
user_table = dynamodb.Table('users')
patient_data_table = dynamodb.Table('patient_data_history')
patient_table = dynamodb.Table('patients')
device_table = dynamodb.Table('iot_device_catalog')

def get_user_by_telegram_id(telegram_id: str) -> dict:
    response = user_table.get_item(Key={'telegram_id': telegram_id})
    return response.get('Item')

def get_user_by_uuid(uuid: str) -> dict:
    response = user_table.get_item(Key={'uuid': uuid})
    return response.get('Item')

def get_patient(uuid: str) -> dict:
    response = patient_table.get_item(Key={'uuid': uuid})
    return response.get('Item')

def get_device(patient_uuid: str) -> dict:
    response = device_table.get_item(Key={'patient_uuid': patient_uuid})
    return response.get('Item')

def get_patient_status(patient_uuid: str) -> dict:
    response = patient_data_table.query(
        KeyConditionExpression='patient_uuid = :uuid',
        ExpressionAttributeValues={':uuid': patient_uuid},
        ScanIndexForward=False,
        Limit=1
    )
    return response.get('Items')[0] if response.get('Items') else None

def get_all_patients_by_telegram_id(telegram_id: str) -> list:
    user = get_user_by_telegram_id(telegram_id)
    return get_all_patients_by_uuid(user.get('uuid'))

def get_all_patients_by_uuid(uuid: str) -> list:
    patients = patient_table.query(
        KeyConditionExpression='caregiver_uuid = :uuid',
        ExpressionAttributeValues={':uuid': uuid}
    )
    
    return patients.get('Items')

def unlink_telegram_id(telegram_id: str) -> None:
    user = get_user_by_telegram_id(telegram_id)
    user_table.update_item(
        Key={'uuid': user.get('uuid')},
        UpdateExpression='REMOVE telegram_id'
    )
