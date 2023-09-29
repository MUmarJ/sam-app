from pymilvus import (
    connections,
    utility,
    Collection,
    # db
)
import pymilvus
import logging
from retry import retry
from utils.MilvusSchema import schema
from utils.Embeddings import get_embeddings
import time
import os
from utils.text_encryption import encrypt, decrypt
import traceback

class MilvusHelper():
    """ This is helper class to create, insert and search within collections
    """

    def __init__(self, connection_alias) -> None:

        logging.info(f'Class MilvusHelper(): {connection_alias}')
        self.connection_alias = connection_alias

    @retry(exceptions=(pymilvus.exceptions.MilvusException, Exception), tries=10, delay=0, logger=logging)
    def connect(self):

        try:
            print('Connecting to Milvus..', os.getenv('MILVUS_HOST'))

            # TODO : get the credentials from azure
            connections.connect(
                alias=self.connection_alias,
                host=os.getenv('MILVUS_HOST'),
                port=os.getenv('MILVUS_PORT'),
                user=os.getenv('MILVUS_USER', ''),
                password=os.getenv('MILVUS_PASSWORD', ''),
                db_name=os.getenv('MILVUS_DB', '')
            )
        except pymilvus.exceptions.MilvusException as e:
            logging.error("Error connecting to Milvus : " + str(e))
            raise pymilvus.exceptions.MilvusException
        except Exception as e:
            logging.error("Error connecting to Milvus : " + str(e))
            raise Exception

    # TODO : 2nd method to create question chaining
    def get_collection(self, collection_name: str):
        """Function to get collection given name
        If an existing collection found return.
        Else create a new collection from defined schema


        Args:
            collection_name (str): _description_
        """
        try:
            logging.info('MILVUS:  get_collection')
            if not utility.has_collection(collection_name, using=self.connection_alias):
                collection = Collection(name=collection_name, schema=schema, using=self.connection_alias)
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                collection.create_index(
                    field_name="conv_vector",
                    index_params=index_params
                )
            else:
                collection = Collection(name=collection_name, schema=schema, using=self.connection_alias)
            return collection
        except Exception as e:
            logging.error('Error in get_collection Milvus:  ' + str(e))
            return None

    # TODO : Method used by the upload_chat to save the data into the milvus
    def insert_data(self, collection_name: str, key : bytes,  question: str, response: str):

        try:
            logging.info('MILVUS:  insert_data')
            collection = self.get_collection(collection_name)
            if collection:
                timestamp = int(time.time())
                response_tokens = 0
                conv_text = f"User: {question} \nAI: {response}"
                conv_vector = get_embeddings(conv_text)


                conv_text_enc = encrypt( key, conv_text)
                question_enc = encrypt(key, question)
                response_enc = encrypt(key, response)

                data = [[conv_text_enc], [conv_vector], [question_enc], [response_enc], [timestamp], [response_tokens]]

                insert_result = collection.insert(data)
                collection.flush()

                return insert_result
        except Exception as e:
            logging.error('Error in insert_data Milvus: ' + str(e))
            logging.error(traceback.format_exc())

        return None

    # TODO : 3rd method to create question chaining
    def build_message(self,key, search_resp, prev_conv):

        try:
            logging.info('MILVUS:  build_message')
            # collating all results both from search and query
            result_list = []

            # parsing out results from the similarity search
            if search_resp and search_resp[0].ids:

                for hit in search_resp[0]:


                    result_list.append(dict(
                        ai_msg=decrypt( key, hit.entity.ai_msg),
                        human_msg=decrypt(key, hit.entity.human_msg)
                    ))

            if prev_conv and prev_conv['ai_msg'] and prev_conv['human_msg']:
                

                # Retaining only using conversations
                # in case the sim search also contains prev conversation, then we need to remove duplicate
                if prev_conv in result_list:
                    result_list.remove(prev_conv)

                result_list.append(prev_conv)
                # result_list = [dict(s) for s in set(frozenset(d.items()) for d in result_list)]


            msg_list = []
            for result in result_list:
                msg_list.append({"role": "user", "content": result['human_msg']})
                msg_list.append({"role": "assistant", "content": result['ai_msg']})

            return msg_list

        except Exception as e:
            logging.error('Error in build_message Milvus:  ' + str(e))
            logging.error(traceback.format_exc())
        # parsing query results for the
        return []

    # TODO : First method to create question chaining
    def get_context(self, key: bytes, collection_name: str, question: str, topK: int, prev_conv: dict):

        try:
            search_results = None
            logging.info('app logger : MILVUS:  get_context %s', collection_name)
            logging.info('MILVUS:  get_context')
            # * * * this is where it appears to be failing * * *
            collection = self.get_collection(collection_name)

            # app.logger.info('MILVUS:  get_context %s', collection)
            if collection:
                collection.load()
                logging.info('MILVUS:  get_context - collection.load()')
                context_msg = [
                    {"role": "system", "content": "You're an AI assistant at Regeneron responding to users."}]

                logging.info('MILVUS:  get_context -context_msg %s', context_msg)
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 0}

                logging.info('MILVUS:  get_context -search_params %s -- entering get_enbeddings()', search_params)
                connections.remove_connection(self.connection_alias)
                logging.info('MILVUS:  get_context -question %s ', question)
                q_embeddings = get_embeddings(question)
                logging.info('MILVUS:  get_context -leaving get_embeddings()', search_params)
                self.connect()
                if q_embeddings:
                    params = dict(data=[q_embeddings],
                                anns_field="conv_vector",
                                param=search_params,
                                limit=topK,
                                output_fields=['human_msg', 'ai_msg'],
                                consistency_level="Strong")

                    # app.logger.info('MILVUS:  get_context - params() %s', params)
                    search_results = collection.search(**params)  # type: ignore

                collection.release()

                context_msg.extend(self.build_message(key, search_results, prev_conv))

                return context_msg
        except Exception as e:
            logging.error('Error in get_context Milvus:  ' + str(e))

        # print(context_msg)

        return []

    # TODO : Method used to get the complete chat from the meta daa collection name
    def get_collection_data(self, collection_name: str,key : bytes, chat_count: int, limit: int):

        try:
            logging.info('MILVUS:  get_collection_data')
            collection = self.get_collection(collection_name)
            if collection:
                collection.load()
                offset = 0
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 0}

                params = dict(
                    expr="conv_id > 0",
                    offset=offset,
                    limit=limit,
                    output_fields=['conv_id', 'human_msg', 'ai_msg', 'timestamp'],
                    consistency_level="Strong")

                search_results = collection.query(**params)  # type: ignore

                for result in search_results:
                    result['human_msg'] = decrypt(key, result['human_msg'])
                    result['ai_msg'] = decrypt(key, result['ai_msg'])

                return search_results

        except Exception as e:
            logging.error('Error in get_collection_data Milvus:  ' + str(e))

        return []
