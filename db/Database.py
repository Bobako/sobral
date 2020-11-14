import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import datetime
import pandas as pd

# возможные значения для action: CREATE/DROP
def create_or_drop_database(host, user, port, password, database, action):
    try:
        connection = psycopg2.connect(host=host, user=user, port=port, password=password)
        cursor = connection.cursor()  
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        query = "{0} DATABASE {1};".format(action, database)
        cursor.execute(query)

        print("PostgreSQL database created/dropped successfully)")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while connection to PostgreSQL", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        

class Database(object):
    def __init__(self, host = "127.0.0.1", database = "test", user = "postgres", port = 5432, password = "fgt6oij12c", archive = "archive"):

        self.host = host
        self.database = database
        self.user = user
        self.port = port
        self.password = password
        self.connection = None
        self.cursor = None
        self.archive = archive

    # подсоединяемся к базе данных
    # cur = True / создавать курсор или нет (по умолчанию - да)
    def connect(self, cur = True):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                port=self.port,
                password=self.password)
            if (cur):
                self.cursor = self.connection.cursor()

            print("Connection to PostgreSQL established successfully")

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

    # отключаемся от базы данных
    def disconnect(self):
        self.cursor.close()
        self.connection.close()
        print("PostgreSQL connection is closed")

    # my_query указывать без скобок
    def create_table(self, name_of_table, columns, data_type_and_constraints, my_query = ""):
        try:
            query_create_table = "CREATE TABLE {} (\n".format(name_of_table)

            if (my_query == ""):
                if (type(columns) != tuple):
                    columns = tuple(columns)
                if (type(data_type_and_constraints) != tuple):
                    columns = tuple(data_type_and_constraints)

                query_tail = ""
                for column, dataTS in zip(columns, data_type_and_constraints):
                    query_tail += column + " " + dataTS + ",\n"
                query_create_table += query_tail[:-2] + "\n);"
            else:
                query_create_table += (my_query + "\n);")

            self.cursor.execute(query_create_table)
            self.connection.commit()

            print("PostgreSQL table {0} in database {1} created successfully)".format(name_of_table, self.database))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)       

    # def update(self, table, rows, value_of_row, columns, values):
    #     try: 
    #         if (type(values) != tuple):
    #             values = tuple(values)
    #         if (type(value_of_row) != tuple):
    #             value_of_row = tuple(value_of_row)

    #         records = list()

    #         for record, row in zip(values, value_of_row):
    #             tmp = [record, row]
    #             records.append(tuple(tmp))

    #         self.cursor.executemany(query, records)
    #         self.connection.commit()

    #         print("Records Updated")

    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print("Error while connection to PostgreSQL", error)

    def select_n_first_rows(self, table, number_of_rows):
        result = list()
        try:
            select_query = "SELECT * FROM {}".format(table)

            self.cursor.execute(select_query)

            for i in range(number_of_rows):
                result.append(self.cursor.fetchone())
            
            print("Selectring rows from table {} finished successfully".format(table))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

        return result

    def insert(self, table, columns, values):
        try:
            query = "INSERT INTO {0} {1} VALUES (".format(table, columns).replace("'","")
            query += ("%s,"*len(columns))[:-1]+")"
            values = tuple(values)
            
            if (type(values) == list):
                self.cursor.executemany(query, values)
            else:
                self.cursor.execute(query, values)
            self.connection.commit()
            print(self.cursor.rowcount, "Record inserted successfully into {} table".format(table))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

    # выбор по стобцам
    def select(self, table, column, condition = False):
        result = None
        try:
            query = "select {0} from {1}".format(column, table)
            if (condition):
                query += (" where " + condition)
            
            self.cursor.execute(query)
            result =  self.cursor.fetchall()            
            
            print("Selectring columns from table {} finished successfully".format(table))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)
        finally:
            return result

    # обновляет одно значение
    def update_one(self, table, column, another_column, id, value):
        try: 
            # для архивации !!!!
            # пока что предполложим что столбцы в архиве будут такие:
            # id | datetime | value | row | column

            # проверим существует ли архив

            self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (self.archive,))

            if (not self.cursor.fetchone()[0]):
                self.create_table( self.archive, ("id", "datetime", "value", "row", "col"), ("SERIAL PRIMARY KEY", "TIMESTAMP", "VARCHAR (100)", "VARCHAR (100)", "VARCHAR (100)"))
            time = datetime.datetime.now()
            print(time)
            changed_val = self.select(table, column, "{0} = {1}".format(another_column, id))
            self.insert(self.archive, ("datetime", "value", "row", "col"), (time, str(changed_val), another_column, column) )

            query = "update {0} set {1} = {2} where {3} = {4}".format(table, column, value, another_column, id)

            self.cursor.execute(query)
            self.connection.commit()

            print("Records Updated")

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

    def select_many_columns(self, table, number_of_rows, columns, where = ""):
        result = dict()
        try:
            if type(columns) == str:
                tmp = list()
                tmp.append(columns)
                columns = tmp

            for column in columns:
                select_query = "SELECT {0} FROM {1}".format(column,table)
                if (where != ""):
                    select_query += (" " + where)
                self.cursor.execute(select_query)
                if number_of_rows == "ALL":
                    fatched = self.cursor.fetchall()
                    result[column] = fatched
                else:
                    fatched = self.cursor.fetchmany(number_of_rows)
                    result[column] = fatched
            
            print("Selectring columns from table {} finished successfully".format(table))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

        return result

    # получаем имена колонок
    def get_columns_names(self, table):
        try:
            col_names = []
            for elt in self.cursor.description:
                col_names.append(elt[0])

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connection to PostgreSQL", error)

        return col_names      
            
# сначала устанавливаем соединение (a.connect())
# потом делаем то нам нужно
# затем закрываем соединение (a.disconnect())

if __name__ == "__main__":
    df = pd.read_excel('Сигналы.xlsx', sheet_name='МПК')
    # list_of_column_names = list()
    # list_of_column_names.append("id")
    # for col_name in df.columns:
    #     if (col_name == "Xmin"):
    #         col_name = "X_min"
    #     if (col_name == "Xmax"):
    #         col_name = "X_max"         
    #     list_of_column_names.append(col_name)
    # list_of_column_names = tuple(list_of_column_names)

    # types = ("SERIAL PRIMARY KEY", "INT", "VARCHAR (50)", "VARCHAR (50)", "VARCHAR (50)", "INT", "INT", "VARCHAR (100)", "REAL", "REAL", "VARCHAR (20)", "REAL", "REAL", "REAL", "REAL", "REAL", "REAL", "VARCHAR (10)")

    # print(list_of_column_names)

    database = "main"
    table_npk = "МПК"
    main = Database(database=database)
    main.connect()

    # # main.create_table(table_npk, list_of_column_names, types)

    df = df.to_dict(orient = 'records')
    keys = []
    for key in df[0].keys():
        if (key == "Xmin"):
            keys.append("X_min")
        elif (key == "Xmax"):
            keys.append("X_max")
        else:
            keys.append(key)
    keys = tuple(keys)

    for record in df:
        values = record.values()
        values = tuple(values)
        main.insert(table_npk, keys, values)
    
    main.disconnect()