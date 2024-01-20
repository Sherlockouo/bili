from datetime import date

from dal.reply_dal import get_max_seq_no,create_max_seq_no,update_max_seq_no

def get(): 
    max_seq_no_list = get_max_seq_no()
    print('max seq list ',max_seq_no_list)
    if max_seq_no_list[0][0] == None :
        return None
    else:
        return max_seq_no_list[0]

def create(max_seq_no):
    create_max_seq_no(max_seq_no,date.today())
    
def update(max_seq_no,id):
    update_max_seq_no(max_seq_no,date.today(),id)