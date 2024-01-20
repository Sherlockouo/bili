import os
import sys
from sqlite3 import connect
from threading import Thread, Lock
from . import Squtils
import time
import logging


class JOIN_METHOD:
    '''数据库SELETE时的连接方法'''
    NATURAL = "NATURAL JOIN"
    CROSS = "CROSS JOIN"
    INNER = "INNER JOIN"
    OUTER = "OUTER JOIN"


class DataBase:
    REF = []  # 数据库文件引用，防止出现多个类操作一个文件

    def __init__(self, db_file, table_modules, not_warning=False) -> None:
        self._filename = db_file
        self._thread_list = {}
        self._thread_idx = 0

        self.db_Lock = Lock()

        if os.path.relpath(self._filename) in self.REF:
            raise RuntimeError(f'文件{self._filename}已经被其他类占用')
        self.REF.append(os.path.relpath(self._filename))

        self._conn = connect(db_file, check_same_thread=False)
        self._tables = DataBase._process_tables(table_modules)
        self._not_warning = not_warning

        self._check_table()

    def __del__(self):
        # 析构函数
        while len(self._thread_list) > 0:
            time.sleep(0.5)
        self._conn.commit()
        self._conn.close()
        self.REF.remove(os.path.relpath(self._filename))  # 删除该数据库对应的引用文件

    def warning(func):  # 装饰器
        def wrapper(self, *args, **kw):
            try:
                func(self, *args, **kw)
            except Exception as e:
                if self._not_warning == False:
                    log_text = f'::In Func "{func.__name__}":File "{__file__}", line {sys._getframe().f_lineno}    ERROR    {type(e).__name__}: {e}'
                    logging.warning(log_text)
        return wrapper

    def warning_exec_sql(func):  # 线程函数装饰器
        def wrapper(self, sql, hash):
            try:
                self.db_Lock.acquire()
                func(self, sql, hash)
            except Exception as e:
                if self._not_warning == False:
                    log_text = f'::In Func "{func.__name__}":File "{__file__}", line {sys._getframe().f_lineno}    ERROR    {type(e).__name__}: {e}'
                    logging.warning(log_text)
            finally:
                self._thread_list.pop(hash)
                self.db_Lock.release()
        return wrapper

    def _check_table(self):
        """
        检查数据库中是否已经包含所有的表
        """
        self.db_Lock.acquire()
        sql = "select name from sqlite_master where type='table'"
        curcor = self._conn.cursor()
        rows = curcor.execute(sql)
        sq_tabs = [r[0] for r in rows]  # sqlite库里存在的表
        py_tabs = []  # 通过python定义的库，用于删除应该不存在的表

        for it in self._tables:
            py_tabs.append(it.__name__)

            if it.__name__ in sq_tabs:
                sub_sql = f'PRAGMA table_info({it.__name__})'
                rows = curcor.execute(sub_sql)
                file_tab_attrs = [(attr[1], attr[2], attr[3]) for attr in rows]
                py_tab_attrs = [(attr['line_name'], attr['type'], int(
                    attr['NotNULL'])) for attr in it.Lines]

                if file_tab_attrs == py_tab_attrs:
                    continue

                if it.UPDATE_METHOD == Squtils.UPDATE_METHOD.CHANGE_MERGE:
                    # 在原表的基础上进行合并
                    need_insert = []  # 在重新建表后需要写回的属性

                    for attrs in file_tab_attrs:
                        if attrs not in py_tab_attrs:
                            continue
                        need_insert.append(attrs[0])

                    sub_sql = f'ALTER TABLE {it.__name__} rename to {it.__name__}_old'
                    curcor.execute(sub_sql)
                    curcor.execute(it().getCreateSQL())
                    try:
                        sub_sql = f"INSERT INTO {it.__name__}({', '.join(need_insert)}) " + \
                            f"SELECT {', '.join(need_insert)} " + \
                            f"FROM {it.__name__}_old;"

                        curcor.execute(sub_sql)
                        sub_sql = f'DROP TABLE {it.__name__}_old;'
                        curcor.execute(sub_sql)
                    except Exception as e:
                        curcor.execute(f'DROP TABLE {it.__name__};')
                        curcor.execute(
                            f'ALTER TABLE {it.__name__}_old rename to {it.__name__}')
                        raise e

                elif it.UPDATE_METHOD == Squtils.UPDATE_METHOD.CHANGE_CLEAR:
                    # 删除表，并从sq_tabs删除方便之后重建
                    sub_sql = f'DROP TABLE {it.__name__}'
                    curcor.execute(sub_sql)
                    sq_tabs.remove(it.__name__)
                    try:
                        # 清空该表的ID自增长
                        sql = f"DELETE FROM sqlite_sequence WHERE name='{it.__name__}';"
                        self._conn.execute(sql)
                    finally:
                        pass

                elif it.UPDATE_METHOD == Squtils.UPDATE_METHOD.CHANGE_RENAME:
                    sub_sql = f'ALTER TABLE {it.__name__} rename to {it.__name__}_old'
                    curcor.execute(sub_sql)
                    curcor.execute(it().getCreateSQL())

                    try:
                        attrs = [attr['line_name'] for attr in it.Lines]
                        sub_sql = f"INSERT INTO {it.__name__}({', '.join(attrs)}) " + \
                            f"SELECT * " + \
                            f"FROM {it.__name__}_old;"

                        curcor.execute(sub_sql)
                        sub_sql = f'DROP TABLE {it.__name__}_old;'
                        curcor.execute(sub_sql)
                    except Exception as e:
                        curcor.execute(f'DROP TABLE {it.__name__};')
                        curcor.execute(
                            f'ALTER TABLE {it.__name__}_old rename to {it.__name__}')
                        raise e

            if it.__name__ not in sq_tabs:
                print(it().getCreateSQL())
                curcor.execute(it().getCreateSQL())

        # 删除未定义的表
        for it in sq_tabs:
            if not it.startswith('sqlite') and it not in py_tabs:
                sub_sql = f'DROP TABLE {it};'
                curcor.execute(sub_sql)

        self._conn.commit()
        self.db_Lock.release()

    def _process_tables(table_modules):
        '''处理表模块'''
        tab_list = []
        for module in table_modules:  # 枚举模块
            for it in module.__dict__:  # 模块里所有的变量包含在__dict__中
                if '__' in it:  # 隐藏变量不用管
                    continue
                value = module.__dict__[it]  # 获取某一个类(也可能不是类，所以要判断)
                if type(value).__name__ == 'TableMeta' and issubclass(value, Squtils.SqTable):
                    # 找到Table
                    tab_list.append(value)  # 将这个类放到列表中

        return tab_list

    @warning_exec_sql
    def _exec_sql(self, sql, hash):
        '''这个是个线程函数, hash用于管理thread list, 该函数修改后会立即提交，用于少量插入'''
        self._conn.execute(sql)
        self._conn.commit()

    @warning_exec_sql
    def _exec_sql_no_commit(self, sql, hash):
        '''
            这个是个线程函数, hash用于管理thread list，
            该函数修改后不会立即提交，用于配合上下文管理器提交大量数据
        '''
        self._conn.execute(sql)

    def insert_table(self, table, *data, **kw_data):
        table_attrs = [it['line_name'] for it in table.Lines]
        insert_attrs = []
        insert_data = []

        if len(data) == 1 and isinstance(data[0], dict) and len(kw_data) == 0:
            # 以字典的形式传入参数
            insert_dict = data[0]
            for key in insert_dict:
                value = insert_dict[key]
                value = str(value) if not isinstance(
                    value, str)else f'"{value}"'

                key_str = key
                if isinstance(key, Squtils.TYPE_Sqlite):
                    key_str = key.name

                if key_str in table_attrs:
                    insert_attrs.append(key_str)
                    insert_data.append(value)

        elif len(kw_data) > 0 and len(data) == 0:
            insert_dict = kw_data
            for key in insert_dict:
                value = insert_dict[key]
                value = str(value) if not isinstance(
                    value, str)else f'"{value}"'
                key_str = key

                if key_str in table_attrs:
                    insert_attrs.append(key_str)
                    insert_data.append(value)

        else:
            insert_attrs = [it['line_name'] for it in table.Lines]
            for it in data:
                if it is None:
                    insert_data.append('NULL')
                elif not isinstance(it, str):
                    insert_data.append(str(it))
                else:
                    insert_data.append(f'"{it}"')

        if len(insert_attrs) != len(insert_data):
            raise ValueError('插入数据的长度应与表的属性个数相同')

        sql = f"INSERT INTO {table.__name__}({', '.join(insert_attrs)}) VALUES({', '.join(insert_data)})"
        t = Thread(target=self._exec_sql, args=(sql, self._thread_idx))
        self._thread_list[self._thread_idx] = t
        self._thread_idx += 1
        t.start()

    @property
    def inserter(self):
        '''创建一个上下文管理器，用于插入数据'''
        class _inserter:
            def __init__(this, table, log=False) -> None:
                # 把 self 改成 this 防止名称冲突，因为要访问外面的名称
                this._tab = table
                this._log = log
                this._attrs = [it['line_name'] for it in table.Lines]

            def __enter__(this):
                return this

            def insert_table(this, *data, **kw_data):
                insert_attrs = []
                insert_data = []

                if len(data) == 1 and isinstance(data[0], dict) and len(kw_data) == 0:
                    # 以字典的形式传入参数
                    insert_dict = data[0]
                    for key in insert_dict:
                        value = insert_dict[key]
                        value = str(value) if not isinstance(
                            value, str)else f'"{value}"'

                        key_str = key
                        if isinstance(key, Squtils.TYPE_Sqlite):
                            key_str = key.name

                        if key_str in this._attrs:
                            insert_attrs.append(key_str)
                            insert_data.append(value)

                elif len(kw_data) > 0 and len(data) == 0:
                    insert_dict = kw_data
                    for key in insert_dict:
                        value = insert_dict[key]
                        value = str(value) if not isinstance(
                            value, str)else f'"{value}"'
                        key_str = key

                        if key_str in this._attrs:
                            insert_attrs.append(key_str)
                            insert_data.append(value)

                else:
                    insert_attrs = this._attrs
                    for it in data:
                        if it is None:
                            insert_data.append('NULL')
                        elif not isinstance(it, str):
                            insert_data.append(str(it))
                        else:
                            insert_data.append(f'"{it}"')

                if len(insert_attrs) != len(insert_data):
                    raise ValueError('插入数据的长度应与表的属性个数相同')

                sql = f"INSERT INTO {this._tab.__name__}({', '.join(insert_attrs)}) VALUES({', '.join(insert_data)})"
                if this._log:
                    print(sql)
                t = Thread(target=self._exec_sql_no_commit,
                           args=(sql, self._thread_idx))
                self._thread_list[self._thread_idx] = t
                self._thread_idx += 1
                t.start()

            def __exit__(this, exc_type, exc_val, exc_tb):
                self._conn.commit()
                if exc_type:
                    return False
                return True

        return _inserter

    def update_table(self, tables, value_dict, where: str = ''):
        if not isinstance(value_dict, dict):
            raise ValueError('value_dict需要为dict')
        
        setter_list = []
        for key, val in value_dict.items():
            value = str(val) if not isinstance(val, str)else f'"{val}"'
            if isinstance(key, str):
                setter_list.append(key + ' = ' + value)
            else:
                setter_list.append(key.name + ' = ' + value)
            

        sql = f"UPDATE {tables.__name__} \n"
        sql += f"SET {', '.join(setter_list)} \n"
        sql += f"WHERE {where};"

        self._conn.execute(sql)
        self._conn.commit()


    def select_table(self, tables, attrs, where: str = '', groupby=None, orderby=None, join_method=JOIN_METHOD.NATURAL):
        SELECT_SQL = ''
        FROM_SQL = ''
        WHERE_SQL = where
        GROUPBY_SQL = ''
        ORDERBY_SQL = ''

        # SELECT 处理
        if isinstance(attrs, str) and attrs == '*':
            SELECT_SQL = '*'
        elif not isinstance(attrs, (list, tuple)):
            raise ValueError(
                'attrs或为list或为tuple且元素应当为str或SqTable.ATTR，或者为字符串"*"')
        else:
            selete_attrs = [str(it) if isinstance(
                it, Squtils.TYPE_Sqlite) else it for it in attrs]
            SELECT_SQL = ', '.join(selete_attrs)

        # FROM 处理
        if isinstance(tables, (Squtils.TableMeta, str)):  # 直接传表
            FROM_SQL = tables if isinstance(tables, str) else tables.__name__
        elif isinstance(tables, (list, tuple)):  # 传过来多个表
            tables_name = []
            for it in tables:
                if isinstance(it, Squtils.TableMeta):
                    tables_name.append(it.__name__)
                else:
                    tables_name.append(it)

            FROM_SQL = f" {join_method} ".join(tables_name)

        # GROUPBY 处理
        if isinstance(groupby, (Squtils.TYPE_Sqlite, str)):  # 直接传表
            GROUPBY_SQL = str(groupby)
        elif isinstance(groupby, (list, tuple)):  # 传过来多个表
            groupby_name = [str(it) for it in groupby]
            GROUPBY_SQL = f", ".join(groupby_name)

        # ORDERBY 处理
        if isinstance(orderby, (Squtils.TYPE_Sqlite, str)):  # 直接传表
            ORDERBY_SQL = str(orderby)
        elif isinstance(orderby, (list, tuple)):  # 传过来多个表
            orderby_name = [str(it) for it in orderby]
            ORDERBY_SQL = f", ".join(orderby_name)

        # 拼凑SQL语句
        sql = f"SELECT {SELECT_SQL} \nFROM {FROM_SQL}"
        if WHERE_SQL:
            sql += f" \nWHERE {WHERE_SQL}"
        if GROUPBY_SQL:
            sql += f" \nGROUP BY {GROUPBY_SQL}"
        if ORDERBY_SQL:
            sql += f" \nORDER BY {ORDERBY_SQL}"
        sql += ';'
        cursor = self._conn.cursor()
        rows = cursor.execute(sql)
        return list(rows)

    def delete_item(self, table, where):
        sql = f"DELETE FROM {table.__name__} \n"
        sql += f"WHERE {where};"
        self._conn.execute(sql)
        self._conn.commit()

    def clear_table(self, table):
        self.db_Lock.acquire()
        sql = f'DELETE FROM {table.__name__};'
        self._conn.execute(sql)
        auto_inc = False  # 是否包含自增长
        for attr in table.Lines:
            if Squtils.AUTOINCREMENT_Sqlite.VALUE in attr['check']:
                sql = f"DELETE FROM sqlite_sequence WHERE name='{table.__name__}';"
                auto_inc = True
                break

        if auto_inc:  # 清空该表的ID自增长
            sql = f"DELETE FROM sqlite_sequence WHERE name='{table.__name__}';"
            self._conn.execute(sql)

        self._conn.commit()
        self.db_Lock.release()
