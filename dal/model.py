from .ease_sqlite import Squtils, Sqdb

class USER(Squtils.SqTable, metaclass=Squtils.TableMeta):
    '''
    用户类
    '''

    # 一个自动增加的INT型数据，稍后会设置其为主键
    ID = (Squtils.INT_Sqlite, Squtils.AUTOINCREMENT_Sqlite)

    # 用户ID，是bilibili用户的UID
    USER_ID = (Squtils.TEXT_Sqlite, not None)

    # 用户名
    NAME = (Squtils.TEXT_Sqlite, not None)

    @classmethod
    def Constraint(cls):
        cls.PRIMARY = [cls.ID]
        cls.UNIQUE = [cls.USER_ID]

class MaxSeqNo(Squtils.SqTable, metaclass=Squtils.TableMeta):
    '''
    用户类
    '''

    # 一个自动增加的INT型数据，稍后会设置其为主键
    ID = (Squtils.INT_Sqlite, Squtils.AUTOINCREMENT_Sqlite)

    # 最大回复序列号
    MAX_SEQ_NO = (Squtils.INT_Sqlite, not None)

    # time
    UPDATE_TIME = (Squtils.DATE_Sqlite, not None)

    @classmethod
    def Constraint(cls):
        cls.PRIMARY = [cls.ID]
        