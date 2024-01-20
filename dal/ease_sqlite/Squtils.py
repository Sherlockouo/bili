
class UPDATE_METHOD:
    CHANGE_MERGE = 0  # 当表结构更改后，在原表的基础上修改表
    CHANGE_CLEAR = 1  # 当表结构更改后，删除原表重新建表
    CHANGE_RENAME = 2  # 属性不变，只改变名称


class AUTOINCREMENT_Sqlite:
    """自增约束"""
    VALUE = 'AUTOINCREMENT'


NOW_TIME = "datetime('now','localtime')"


class DEFAULT:
    def __init__(self, value) -> None:
        self.VALUE = f"DEFAULT ({value})"


class TYPE_Sqlite:
    TYPE = 'INT'

    def __str__(self) -> str:
        return getattr(self, 'sql_name', None)

    def __copy(self):
        ret_cls = self.__class__()
        ret_cls.TYPE = self.TYPE
        ret_cls.name = getattr(self, 'name', None)
        ret_cls.table = getattr(self, 'table', None)
        ret_cls.sql_name = getattr(self, 'sql_name', None)
        return ret_cls

    @property
    def SUM(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'SUM({ret_cls.sql_name})'
        return ret_cls

    @property
    def COUNT(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'COUNT({ret_cls.sql_name})'
        return ret_cls

    @property
    def MAX(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'MAX({ret_cls.sql_name})'
        return ret_cls

    @property
    def MIN(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'MIN({ret_cls.sql_name})'
        return ret_cls

    @property
    def AVG(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'AVG({ret_cls.sql_name})'
        return ret_cls

    @property
    def ASC_ORDER(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'{ret_cls.sql_name} ASC'
        return ret_cls

    @property
    def DESC_ORDER(self):
        ret_cls = self.__copy()
        ret_cls.sql_name = f'{ret_cls.sql_name} DESC'
        return ret_cls


class INT_Sqlite(TYPE_Sqlite):
    """整数"""
    TYPE = 'INT'


class TEXT_Sqlite(TYPE_Sqlite):
    """文本"""
    TYPE = 'TEXT'


class DATE_Sqlite(TYPE_Sqlite):
    """"""
    TYPE = 'DATE'


class REAL_Sqlite(TYPE_Sqlite):
    """实数"""
    TYPE = 'REAL'


class TableMeta(type):
    """表的元类，主要负责获取表中的属性等信息"""
    def __new__(cls, name, bases, attrs):
        # attrs中包含了类全局变量信息

        lines = []  # sql中的行
        for key, value in attrs.items():
            if key.startswith('__'):
                continue

            if key in ['Constraint', 'UPDATE_METHOD']:
                continue

            others = []
            if isinstance(value, (tuple, list)):
                # 对于元组或列表，第一元素为属性的类型，之后为其他修饰
                others = value[1:]
                value = value[0]

            attrs[key] = value()  # 实例化，这样方便设置变量名，为之后设置主键之类的提供帮助
            attrs[key].name = key
            attrs[key].table = name  # 记录属性的表名，方便外键
            attrs[key].sql_name = f'{name}.{key}'

            line = {
                'line_name': key,
                'type': attrs[key].TYPE,
                'NotNULL': False,
                'check': ''  # 约束
            }
            for it in others:  # 对于其他属性
                if isinstance(it, bool) or it is None:  # 这里是处理是否为空
                    line['NotNULL'] = bool(it)
                elif isinstance(it, DEFAULT):
                    line['check'] += it.VALUE + ' '
                else:
                    line['check'] += it.VALUE + ' '  # 处理其他约束

            lines.append(line)
        attrs['Lines'] = lines

        new_cls = type.__new__(cls, name, bases, attrs)  # 生成类

        new_cls.Constraint()  # 生成约束
        new_cls.__build__()  # 该函数主要是处理约束信息
        return new_cls


class SqTable:
    """所有表的基类"""
    # 写出这三个是为了在子类里面有代码提示
    PRIMARY = []
    UNIQUE = []
    FOREIGN = []
    UPDATE_METHOD = UPDATE_METHOD.CHANGE_MERGE

    @classmethod
    def Constraint(cls): pass

    @classmethod
    def __build__(cls):
        if hasattr(cls, 'PRIMARY') and len(cls.PRIMARY) > 0:
            cls.PRIMARY = [it.name if not isinstance(it, tuple) else it for it in cls.PRIMARY]

        for line in cls.Lines:
            if line['line_name'] in cls.PRIMARY:
                line['NotNULL'] = False
                if AUTOINCREMENT_Sqlite.VALUE in line['check'] and line['type'] == 'INT':
                    line['type'] = 'INTEGER'

    def getCreateSQL(self):
        """最主要的方法，获取类对应的sql建表语句"""
        ret_sql = f'CREATE TABLE {self.__class__.__name__} (\n'

        for line in self.Lines:
            ret_sql += f"\t{line['line_name']} {line['type']} "

            if line['line_name'] in self.PRIMARY:
                ret_sql += 'PRIMARY KEY '
            elif line['NotNULL']:
                ret_sql += 'NOT NULL '

            ret_sql += line['check'] + ',\n'

        # primary key(aegernum,medid)
        if hasattr(self, 'PRIMARY') and len(self.PRIMARY) > 0:
            for it in self.PRIMARY:
                if isinstance(it, tuple):
                    lst = [xx.name for xx in it]
                    ret_sql += '\tPRIMARY KEY(' + ', '.join(lst) + '),\n'

        if hasattr(self, 'FOREIGN') and len(self.FOREIGN) > 0:
            for a, b in self.FOREIGN:
                if b.table == a.table:
                    raise ValueError(
                        f'外键设置：属性{b.name}与属性{a.name}同处于表{a.table}内')
                ret_sql += f'\tFOREIGN KEY({a.name}) REFERENCES {b.table}({b.name}),\n'

        if hasattr(self, 'UNIQUE') and len(self.UNIQUE) > 0:
            self.UNIQUE = [it.name for it in self.UNIQUE]
            ret_sql += '\tUNIQUE(' + ', '.join(self.UNIQUE) + '),\n'

        ret_sql = ret_sql[:-2] + '\n);'
        return ret_sql
