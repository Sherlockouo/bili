from .ease_sqlite import Sqdb

from . import model, db_config

db = Sqdb.DataBase(db_config.DB_FILE_NAME, [model])

def get_write_db():
    return db