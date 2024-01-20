from .model import MaxSeqNo

from .db import get_write_db

def get_max_seq_no(): 
    return get_write_db().select_table(MaxSeqNo, ["max(MAX_SEQ_NO)"])

def create_max_seq_no(max_seq_no, date):
    get_write_db().insert_table(MaxSeqNo, {MaxSeqNo.MAX_SEQ_NO: max_seq_no,MaxSeqNo.UPDATE_TIME: date})
    
def update_max_seq_no(max_seq_no, date,old_id):
    get_write_db().update_table(MaxSeqNo, {MaxSeqNo.MAX_SEQ_NO: max_seq_no,MaxSeqNo.UPDATE_TIME: date},where=f'id = {old_id}')    