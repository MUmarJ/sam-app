from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL
import json
import os

# TODO : Method to get the user details from LDAP
def get_name_photo_from_AD(mail_id):
    """Function to fetch name and display pic from the AD

    Args:
        mail_id (_type_): mail_id of the regeneron user

    Returns:
        _type_: dict(display_name, display_photo)
    """
    try:
        username = f"CN={os.getenv('LDAP_USER')},OU=Regeneron System Accounts,DC=regeneron,DC=regn,DC=com" # TODO : Get the username from AWS
        password = os.getenv("LDAP_PASSWORD") # TODO : get the password from AWS

        server = Server('regeneron.regn.com', get_info=ALL)
        conn = Connection(server, username, password, auto_bind=True)
        conn.search('dc=regeneron,dc=regn,dc=com', f'(&(objectClass=*)(mail={mail_id}))', attributes=ALL_ATTRIBUTES)
        resp = json.loads(conn.entries[0].entry_to_json())

        display_name = resp['attributes'].get('displayName', None)
        display_photo = resp['attributes'].get('thumbnailPhoto', None)
        guid = resp['attributes'].get('objectGUID', None) # TODO : Note this is the key used to decrypt the user chats

        return dict(display_name=display_name, display_photo=display_photo), guid
    except:
        return dict(display_name=None, display_photo=None), ''