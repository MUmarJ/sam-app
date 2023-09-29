import json
from utils.text_encryption import encrypt, decrypt, get_md5
from sql_helper import SqlHelper # TODO : Replace the module and the class name of the sql lambda layer
import RedisHelper # TODO : Replace the module with the redis helper lambda layer
from MilvusHelper import MilvusHelper # TODO : Replace the module and the class name of the milvus helper

# Initialize SQL helper
sql_helper = SqlHelper()

def lambda_handler(event, context):
    try:
        # Get parameters
        question = event['question']
        response = event['response']
        email = event['email']
        collection_name = event['collection']

        if not question or not response or not email or not collection_name:
            return {
                'statusCode': 400,
                'body': dict(error='Missing required parameters')
            }

        try:
            milvus_conn = os.getenv('MILVUS_CONN') # TODO : get the milvus details from aws
            milvus = MilvusHelper(milvus_conn)
            milvus.connect()
        except pymilvus.exceptions.ConnectError as e:
            print('Milvus connection failed %s', str(e))
        except Exception as e:
            print('Milvus connection failed %s', str(e))


        redis_client = get_redis_client() # TODO : either create a object oriented code / call the method directly

        if redis_client:
            key = redis_client.get(email)

        if collection_name and key:
            redis_client.set(collection_name, encrypt(key, json.dumps(dict(human_msg=question, ai_msg=response))), ex=86400)
            milvus.insert_data(collection_name, key, question, response)

            meta_update_status = sql_helper.update_collection_data(collection_name, response[:100])

            if meta_update_status:
                return {
                'statusCode': 200,
                'body': dict(info='Upload Successful')
                }

        else:
            return {
            'statusCode': 400,
            'body': dict(info='Upload Failed')
            }


    except ValueError as e:
        return {
            'statusCode': 500,
            'body': dict(error='We are sorry, uploading chat failed. Please try again later.')
            }

