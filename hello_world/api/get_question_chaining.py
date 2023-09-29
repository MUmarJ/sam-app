import json
from sql_helper import SqlHelper # TODO : Replace the module and the class name of the sql lambda layer
import RedisHelper # TODO : Replace the module with the redis helper lambda layer
from utils.text_encryption import encrypt, decrypt, get_md5
from MilvusHelper import MilvusHelper # TODO : Replace the module and the class name of the milvus helper


# Initialize SQL helper
sql_helper = SqlHelper()

def lambda_handler(event, context):
    # Get mail_id from event
    question = event['question']
    email = event['email']
    collection_name = event['collection']

    if not question or not email or not collection_name:
        return {
            'statusCode': 400,
            'body': dict(error='Missing required parameters')
        }

    if collection_name:
        redis_client = get_redis_client() # TODO : either create a object oriented code / call the method directly

        if redis_client:
            key = redis_client.get(email)
            prev_conv = redis_client.get(collection_name)

            prev_conv = json.loads(decrypt(key, prev_conv.decode('utf-8'))) if prev_conv else {}
            
            if key:
                try:
                    milvus_conn = os.getenv('MILVUS_CONN') # TODO : get the milvus details from aws
                    milvus = MilvusHelper(milvus_conn)
                    milvus.connect()
                except pymilvus.exceptions.ConnectError as e:
                    print('Milvus connection failed %s', str(e))
                except Exception as e:
                    print('Milvus connection failed %s', str(e))
        
                messages = milvus.get_context(key, collection_name, question, topK=2, prev_conv=prev_conv)
            else:
                raise Exception("Unable to fetch context!")

    messages.append({"role": "user", "content": question})
       
    # Return data to user
    return {
    'statusCode': 200,
    'body': messages
    }