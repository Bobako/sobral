from Database import *

columns = ["id", "model", "price"]
descr = ["INTEGER", "VARCHAR (50)", "REAL"]

create_or_drop_database("127.0.0.1", "postgres", 5432, "fgt6oij12c", "lol", "CREATE")

a = Database(database="to_delete")
a.connect()
a.insert("table_with_phones", ("id", "model"), [(3, "Xiaomi"), (6, "Mezu")])
    
# a.create_or_drop_database("to_delete", "CREATE")
# a.create_table(name_of_database="to_delete", name_of_table="table_with_phones", columns=columns, data_type_and_constraints=descr)
# a.insert("table_with_phones", ["id", "model"], [(1, "Pixel"), (2, "iPhone")], "to_delete")

# lupa = a.select_n_first_rows("table_with_phones", "to_delete", 3)
    
# pupa = a.select_columns("table_with_phones", 2, ["id", "price"], "id = 4")
# print(pupa)

a.update("table_with_phones", "id", (1,2), "price", (30, 40))
a.disconnect()