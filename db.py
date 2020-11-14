from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase
import datetime
import pandas as pd

# замените на ваши значения
database_name = "main"
user = "postgres"
password = "123"
host = "localhost"
port = 5432

pg_db = PostgresqlExtDatabase(database_name, user=user, password=password, host=host, port=port)

class BaseModel(Model):
    # возвращает столбец
    @classmethod
    def select_column(cls, column: str, where: str, condition: str, limit: int): # для where condition limit принимается значение False
        if (limit):
            selected = cls.select().limit(limit).dicts().execute()
        else:
            selected = cls.select().dicts().execute()
        res = list()
        for record in selected:
            if (where):
                if (record[where] == condition):
                    res.append(record[column])
            else:
                res.append(record[column])
        return res

    class Meta:
        database = pg_db

# след. три таблицы для листов из Сигналы.xlsx 
# важная ремарочка: в PostgreSQL имена колонок xmin, xmax
# являются зарезервированными и их нельзя использователь в таблице
class MPK(BaseModel):
    id = AutoField(primary_key = True)
    id_kks = IntegerField(null = True)
    KKS = CharField(null = True)
    Суффикс = CharField(null = True)
    Модуль = CharField(null = True)
    Слот = IntegerField(null = True)
    Канал = IntegerField(null = True)
    NAME = CharField(null = True)
    Xmin_ = FloatField(null = True)
    Xmax_ = FloatField(null = True)
    unit = CharField(null = True)
    LA = FloatField(null = True)
    LW = FloatField(null = True)
    HW = FloatField(null = True)
    HA = FloatField(null = True)
    Точность_лог = FloatField(null = True)
    Точность_вк = FloatField(null = True)
    Type = CharField(null = True)

    class Meta:
        table_name = "МПК"
    
    # меняет значение поля, возвращает значение которое было в поле до изменения
    @classmethod
    def insert_one(cls, id, column, value):
        record = cls.select().where(cls.id == id).get() # cls.id_kks / cls.id
        previous_value = None
        if (column == 'KKS'):
            previous_value = record.KKS
            record.KKS = value           
            record.save()
        elif (column == 'Суффикс'):
            previous_value = record.Суффикс
            record.Суффикс = value
            record.save()
        elif (column == 'Модуль'):
            previous_value = record.Модуль
            record.Модуль = value
            record.save()
        elif (column == 'Слот'):
            previous_value = record.Слот
            record.Слот = value
            record.save()
        elif (column == 'Канал'):
            previous_value = record.Канал
            record.Канал = value
            record.save()
        elif (column == 'NAME'):
            previous_value = record.NAME
            record.NAME = value
            record.save()
        elif (column == 'Xmin_'):
            previous_value = record.Xmin_
            record.Xmin_ = value
            record.save()
        elif (column == 'Xmax_'):
            previous_value = record.Xmax_
            record.Xmax_ = value
            record.save()
        elif (column == 'unit'):
            previous_value = record.unit
            record.unit = value
            record.save()
        elif (column == 'LA'):
            previous_value = record.LA
            record.LA = value
            record.save()
        elif (column == 'LW'):
            previous_value = record.LW
            record.LW = value
            record.save()
        elif (column == 'HW'):
            previous_value = record.HW
            record.HW = value
            record.save()
        elif (column == 'HA'):
            previous_value = record.HA
            record.HA = value
            record.save()
        elif (column == 'Точность_лог'):
            previous_value = record.Точность_лог
            record.Точность_лог = value
            record.save()
        elif (column == 'Точность_вк'):
            previous_value = record.Точность_вк
            record.Точность_вк = value
            record.save()
        elif (column == 'Type'):
            previous_value = record.Type
            record.Type = value
            record.save()
        else:
            print('table MPK has no column named {}'.format(column))
        return previous_value

class RS485(BaseModel):
    id = AutoField(primary_key = True)
    KKS = CharField(null = True)
    Суффикс = CharField(null = True)
    Модуль = CharField(null = True)
    Слот = IntegerField(null = True)
    Канал = IntegerField(null = True)
    NAME = CharField(null = True)
    Xmin_ = FloatField(null = True)
    Xmax_ = FloatField(null = True)
    unit = CharField(null = True)
    LA = FloatField(null = True)
    LW = FloatField(null = True)
    HW = FloatField(null = True)
    HA = FloatField(null = True)
    Точность_лог = FloatField(null = True)
    Точность_вк = FloatField(null = True)
    Type = CharField(null = True)

    class Meta:
        table_name = "RS458"

class Calculated(BaseModel):
    id = AutoField(primary_key = True)
    KKS = CharField(null = True)
    Суффикс = CharField(null = True)
    Модуль = CharField(null = True)
    Слот = IntegerField(null = True)
    Канал = IntegerField(null = True)
    name = CharField(null = True)
    Xmin_ = FloatField(null = True)
    Xmax_ = FloatField(null = True)
    unit = CharField(null = True)
    Type = CharField(null = True)
    Formula = FloatField(null = True)
    LA = FloatField(null = True)
    LW = FloatField(null = True)
    HW = FloatField(null = True)
    HA = FloatField(null = True)
    Точность_лог = FloatField(null = True)
    Точность_вк = FloatField(null = True)

    class Meta:
        table_name = "Calculated"

# класс для таблицы архива
class Archive(BaseModel):
    id = AutoField(primary_key = True)
    id_kks = IntegerField(null = True)
    value = FloatField(null = True)
    session_date = DateTimeField()
    session_id = IntegerField(null = True)
    cycle_id = IntegerField(null = True)
    tm_update = FloatField(null = True)

    class Meta:
        table_name = "Archive"

class DatabaseManipulation(object):
    def __init__(self, db, current_table, archive):
        self.db = db
        self.current_table = current_table
        self.archive = archive
    
    def create_tables(self, list_of_tables):
        with self.db:
            self.db.create_tables(list_of_tables)
        print('Tables created successfully')
    
    def drop_tables(self, list_of_tables):
        with self.db:
            self.db.drop_tables(list_of_tables)
        print('Tables dropped successfully')

    def insert_many(self, data):
        with self.db.atomic():
            self.current_table.insert_many(data).execute()
        print("{} filled successfully".format(self.current_table))

    def insert_one(self, id, column, value): # работает пока только с MPK
        previous = self.current_table.insert_one(id=id, column=column, value=value)

        archive_dict = dict()
        archive_dict['id_kks'] = id
        archive_dict['value'] = previous # у этого столбца тип данны real так что если вставлять строку то будет ошибка
        archive_dict['session_date'] = datetime.datetime.now()

        self.archive.insert_many(archive_dict).execute()
        print("{} filled successfully".format(self.archive))

    def delete_row(self, row):
        to_del = self.current_table.get(self.current_table.id_kks == row)
        to_del.delete_instance()

    def select_column(self, column, where=False, condition=False): 
        selected = self.current_table.select().dicts().execute()
        res = list()
        for record in selected:
            if (where):
                if (record[where] == condition):
                    res.append(record[column])
            else:
                res.append(record[column])
        return res

    def start(self): # создание таблиц и их инициализация, файлы Сигналы.xlsx и arhive.csv должны лежать в той же папке что и скрипт
        self.create_tables([self.current_table, self.archive])

        df = pd.read_excel('Сигналы.xlsx', sheet_name='МПК') # извлекаем информацию из xlsx
        data = df.to_dict(orient = 'records')
        with pg_db.atomic():
            self.current_table.insert_many(data).execute() # заполняем таблцу
        print("{} filled successfully".format(self.current_table))

        df = pd.read_csv('arhive.csv') # извлекаем иформацию из arhive.csv
        data = df.to_dict(orient = 'records')
    
        # кто-то придумал хранить дату как строки, поэтому сделаем эти строки обратно датой
        for index in range(len(data)):
            data[index]['session_date'] = pd.to_datetime(data[index]['session_date'])
        with pg_db.atomic():
            self.archive.insert_many(data).execute() # заполняем таблицу Archive
        print("{} filled successfully".format(self.archive))        

if __name__ == '__main__':
    my_tables = DatabaseManipulation(pg_db, MPK, Archive)
    my_tables.start()
    # for i in range(8):
    #     my_tables.insert_one(3+i,'Xmin_', 3000 + i*100)
    # print(Archive.select_column('value', 'id_kks', 20))
    # to_insert = {'id_kks': 128, 'KKS': 'DFJFDJKDF', 'Суффикс': '123'}
    # my_tables.insert_many([to_insert])
    # my_tables.delete_row(128)