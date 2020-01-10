from .item import BaseItem, Field
import sqlite3
import pymysql


class OriginSqlItem(BaseItem):
    """
        稍微封装一下sql语句，避免每次爬虫都要写SQL语句
    """
    table = None

    @classmethod
    def create_item(cls, sql, table=None,  sqltype='sqlite'):
        table = table if table else cls.table
        create_list = []
        for k, f in cls.fields.items():
            create_list.append(f'{k} {f}')
        if cls.relation:
            create_list.append(cls.relation)
        if sqltype.lower() == 'sqlite':
            cmd = 'create table if not exists {table}\
            ({creation})'.format(table=table, creation=','.join(create_list))
        elif sqltype.lower() == 'sqlserver':
            cmd = "if not exists (select * from sysobjects where id=object_id('{table}') \
            and OBJECTPROPERTY(id, 'IsUserTable')=1) \
            create table {table}\
            ({creation})".format(table=table, creation=','.join(create_list))
        else:
            raise AttributeError
        sql.cursor.execute(cmd)

    @classmethod
    def rollback(cls, sql):
        sql.conn.rollback()


    @classmethod
    def get_items(cls, sql, table=None, select_list=['*'], order_str='', filter_str=''):
        """
            select_list = [*],
            order_str = ''
        """
        table = table if table else cls.table
        selects = ','.join(select_list)
        cmd = f'select {selects} from {table} {filter_str} {order_str}'
        # print(cmd)
        sql.cursor.execute(cmd)
        return sql.cursor.fetchall()

    @classmethod
    def clear_all(cls, sql, table):
        try:
            sql.cursor.execute(f'delete from {table}')
            sql.conn.commit()
            return (True, 1)
        except Exception as e:
            return (False, str(e))

    @classmethod
    def delete_item(cls, sql, table):
        ''' 删除表 '''
        try:
            sql.cursor.execute(f'drop table {table}')
            sql.conn.commit()
            return (True, 1)
        except Exception as e:
            return (False, str(e))

    @classmethod
    def remove_item(self, sql, table, name, value):
        """
            sql, table, name, value
        """
        try:
            sql.cursor.execute(f"delete from {table} where {name}='{value}'")
            sql.conn.commit()
            return (True, 1)
        except Exception as e:
            return (False, str(e))


    @classmethod
    def inserts(cls, sql, table, items):
        if not items:
            return (True, 0)
        insert_str = ','.join([x for x in items[0].keys()])
        for item in items:
            values = [f"'{value}'" for value in items.values()]
            value_str = ','.join(values)
            cmd = f"insert into {table}({insert_str}) values({value_str})"
            try:
                sql.cursor.execute(cmd)
            except Exception as e:
                print(str(e))
                cls.rollback(sql)
                pass
        sql.conn.commit()
        return (True, 1)

    @classmethod
    def save_list(cls, sql, table, name_list, value_list):
        insert_str = ','.join(name_list)
        value_str = tuple(value_list)
        cmd = f"insert into {table}({insert_str}) values{value_str}"
        # print(cmd)
        try:
            sql.cursor.execute(cmd)
            sql.conn.commit()
            return (True, cmd)
        except Exception as e:
            return (False, str(e))

    # @classmethod
    # def get_one(cls, sql, table, select_list=['*'], order_str='', filter_str=''):
    #     selects = ','.join(select_list)
    #     cmd = f'select {selects} from {table} {filter_str} {order_str}'
    #     sql.cursor.execute(cmd)
    #     return sql.cursor.fetchone()

    @classmethod
    def raw_query(cls, sql, cmd):
        sql.cursor.execute(cmd)
        return sql.cursor.fetchall()

    @classmethod
    def raw_update(cls, sql, cmd):
        try:
            sql.cursor.execute(cmd)
            return True
        except:
            return False

    @classmethod
    def save(cls, sql, table, item):
        inserts = []
        values = []
        for key, value in item.items():
            inserts.append(key)
            values.append("'{}'".format(value))
        insert_str = ','.join(inserts)
        value_str = ','.join(values)
        cmd = 'insert into {}({}) values({})'.format(
            table, insert_str, value_str
        )
        try:
            sql.cursor.execute(cmd)
            msg = (True, cmd)
        except pymysql.IntegrityError:
            msg = (True, cmd)
        except sqlite3.IntegrityError:
            msg = (True, cmd)
        except Exception as e:
            # cls.rollback(sql)
            msg = (False, str(e) + cmd)
        try:
            sql.conn.commit()
        except:
            sql.conn.ping()
        return msg

    @classmethod
    def get_save_cmd(cls, table, item):
        inserts = []
        values = []
        for key, value in item.items():
            inserts.append(key)
            values.append("'{}'".format(value))
        insert_str = ','.join(inserts)
        value_str = ','.join(values)
        return 'insert into {}({}) values({})'.format(
            table, insert_str, value_str
        )

    @classmethod
    def update_item(cls, sql, table, value_dict={}, limit_dict={}, quotation="'"):
        value_str = ','.join([f"{k}={quotation}{v}{quotation}" for k, v in value_dict.items()])
        if limit_dict:
            limit_str = 'where ' + ' and '.join([f"{k}='{v}'" for k, v in limit_dict.items()])
        else:
            limit_str = ''
        cmd = 'update {} set {} {}'.format(
            table, value_str, limit_str
        )
        try:
            sql.cursor.execute(cmd)
            msg = (True, cmd)
        except Exception as e:
            # cls.rollback(sql)
            msg = (False, str(e))
        sql.conn.commit()
        return msg


class SqlItem(BaseItem):
    table = None

    @classmethod
    def create_item(cls, sql):
        create_list = []
        for k, f in cls.fields.items():
            create_list.append(f'{k} {f}')
        if cls.relation:
            create_list.append(cls.relation)
        cmd = "if not exists (select * from sysobjects where id=object_id('{table}') \
            and OBJECTPROPERTY(id, 'IsUserTable')=1) \
            create table {table}\
            ({creation})".format(table=cls.table, creation=','.join(create_list))
        sql.cursor.execute(cmd)


class MongoItem(BaseItem):
    
    @classmethod
    def save(cls, mongo, document):
        """
            mongo: mongo,
            collection:
            document:
        """
        try:
            mongo.collection.insert_one(document)
            return (True, document)
        except Exception as e:
            return (False, str(e))

    @classmethod
    def get_items(cls, collection, document):
        return collection.find(document)

    @classmethod
    def delete_item(cls, mongo):
        return mongo.collection.drop()
