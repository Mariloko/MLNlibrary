import mysql.connector
from flask import Flask
import re

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=""
)

ddl_path = "DDL.sql"
dml_path = "DML.sql"
qs_path = "QSH.sql"

def no_comments(text):
    ret = re.sub(r'--.*?\n', '', text)
    return ret

def no_delimiters(text):
    text = text.replace("DELIMITER //", '')
    text = text.replace("DELIMITER ;", '')
    text = text.replace(" //", ';')
    return text

with open(ddl_path, encoding = 'utf-8') as file_ddl:
    ddl = file_ddl.read()

with open(dml_path, encoding = 'utf-8') as file_dml:
    dml = file_dml.read()

with open(qs_path, encoding = 'utf-8') as file_qs:
    qs = file_qs.read()

#--------------------------------------------------------

ddl = no_comments(ddl)
dml = no_comments(dml)
qs = no_comments(qs)

ddl = no_delimiters(ddl)
dml = no_delimiters(dml)
qs = no_delimiters(qs)

allentries = ddl + dml + qs

#--------------------------------------------------------

print('Building Database...')
mycursor = mydb.cursor()

for _ in mycursor.execute(ddl, multi=True):
    pass

print('DDL Done!')

for _ in mycursor.execute(dml, multi=True):
    pass

print('DML Done!')

for _ in mycursor.execute(qs, multi=True):
    pass

print('QS Done!')
print('All Done!')
