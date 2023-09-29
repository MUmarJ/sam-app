'''External Libraries'''
from flask import jsonify

# Custom Libraries

class ResponseHelper:
    '''
    This is a helper class to help in json structuring
    '''

    # Method to return info
    @staticmethod
    def return_info(message):
        '''
        Arguments : 
            message : message to convert into json
        Return type : JSON String
        '''
        return jsonify({'info' : message})
    
    
    # Method to return error with type
    @staticmethod
    def return_error(message, type_message):
        '''
        Arguments : 
            message : message to convert into json
        Return type : JSON String
        '''
        return jsonify({'error' : message, 'type': type_message })
    
    # Method to return data
    @staticmethod
    def return_data(message):
        '''
        Arguments : 
            message : message to convert into json array
        Return type : JSON Array Data
        '''
        return jsonify(dict(data = message))
