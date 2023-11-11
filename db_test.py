import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ankush@2003",
    database="onlinebookstore",
    port=3306
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

mydb.close()