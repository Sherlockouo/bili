from .model import USER

from .db import get_write_db

def query_by_user_id(user_id): 
    where_str = f'{USER.USER_ID}={user_id}'
    return get_write_db().select_table(USER, "*", where=where_str)

def create_user(user_id, name):
    get_write_db().insert_table(USER, {USER.USER_ID: user_id, USER.NAME: name})