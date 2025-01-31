import boto3
import os
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from cachetools.func import ttl_cache


load_dotenv()
# create a boto3 client with environment variables if set to use access keys
if os.getenv('use_aws_access_keys') == 'true':
    print("Using AWS access keys from .env file")
    session = boto3.Session(
        region_name="us-east-1",
        aws_access_key_id=os.getenv('aws_access_key_id'),
        aws_secret_access_key=os.getenv('aws_secret_access_key'),
        aws_session_token=os.getenv('aws_session_token')
    )
    
else:
    session = boto3.Session(region_name="us-east-1")

dynamodb = session.resource('dynamodb')

user_table = dynamodb.Table('users')
patient_data_table = dynamodb.Table('patient_data_history')
patient_table = dynamodb.Table('patients')
device_table = dynamodb.Table('iot_device_catalog')

class CacheService(object):

    def __init__(self):
        self.data = {}

    def __setitem__(self, key, item):
        self.data[key] = [item, 0]

    def __getitem__(self, key):
        value = self.data[key]
        value[1] += 1
        return value[0]
    
    def get(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            return None

    def getcount(self, key):
        return self.data[key][1]
    
user_patients = CacheService()

@ttl_cache(maxsize=128, ttl=5)
def get_user_by_telegram_id(telegram_id: int) -> dict:
    
    response = user_table.query(
        IndexName='telegram_id-index',
        KeyConditionExpression=Key('telegram_id').eq(telegram_id),
        Limit=1
    )
    
    return response.get('Items')[0] if response.get('Items') else None

@ttl_cache(maxsize=128, ttl=5)
def get_user_by_uuid(uuid: str) -> dict:
    response = user_table.get_item(Key={'uuid': uuid})
    return response.get('Item')

@ttl_cache(maxsize=128, ttl=5)
def get_user_by_email(email: str) -> dict:
    response = user_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email),
        Limit=1
    )
    return response.get('Items')[0] if response.get('Items') else None

@ttl_cache(maxsize=128, ttl=5)
def get_patient(uuid: str) -> dict:
    response = patient_table.get_item(Key={'uuid': uuid})
    return response.get('Item')

@ttl_cache(maxsize=128, ttl=5)
def get_device(patient_uuid: str) -> dict:
    response = device_table.get_item(Key={'patient_uuid': patient_uuid})
    return response.get('Item')

@ttl_cache(maxsize=128, ttl=5)
def get_patient_status(patient_uuid: str) -> dict:
    response = patient_data_table.query(
        KeyConditionExpression=Key('patient_uuid').eq(patient_uuid),
        ScanIndexForward=False,
        Limit=1
    )
    return response.get('Items')[0] if response.get('Items') else None

@ttl_cache(maxsize=128, ttl=5)
def get_all_patients_by_telegram_id(telegram_id: str) -> list:
    user = get_user_by_telegram_id(telegram_id)
    if user:
        return get_all_patients_by_uuid(user.get('uuid'))

@ttl_cache(maxsize=128, ttl=5)
def get_all_patients_by_uuid(uuid: str) -> list:
    patients = patient_table.query(
        IndexName='caregiver_uuid-index',
        KeyConditionExpression=Key('caregiver_uuid').eq(uuid)
    )
    
    if patients.get('Items'):
        # store user's patients in cache
        user_patients[uuid] = {}
        
        for patient in patients.get('Items'):
            user_patients[uuid][patient.get('uuid')] = patient
        
    return patients.get('Items')

@ttl_cache(maxsize=128, ttl=5)
def unlink_telegram_id(telegram_id: str) -> None:
    user = get_user_by_telegram_id(telegram_id)
    
    if not user:
        return False
    
    user_table.update_item(
        Key={'uuid': user.get('uuid')},
        UpdateExpression='REMOVE telegram_id'
    )
    
    return user
