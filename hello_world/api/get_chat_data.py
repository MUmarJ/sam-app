import RedisHelper # TODO : Replace the module with the redis helper lambda layer
from MilvusHelper import MilvusHelper # TODO : Replace the module and the class name of the milvus helper

def lambda_handler(event, context):
    try:
        # Get mail_id from event
        collection_name = event['collection_name']
        email = event['email']

        if not collection_name or not email:
            return {
                'statusCode': 400,
                'body': dict(error='Required parameters missing')
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
            chat_data = milvus.get_collection_data(collection_name,key, 16384, 100)

            if chat_data:
                # Return data to user
                return {
                'statusCode': 200,
                'body': chat_data
                }
            
            # Return error to the user
            return {
            'statusCode': 100,
            'body': dict(info='No chat data found')
            }
                    

    except Exception as e:
         return {
            'statusCode': 500,
            'body': dict(error='We are sorry, retrieving chat data failed. Please try again later.')
            }