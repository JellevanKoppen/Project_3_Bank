"""
Author: Jelle van Koppen
Date: 23-2-2018
Version: 0.1
Description: Datbase connection to python
"""

import _mysql

db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")

sql = """SELECT pincode FROM gebruikers WHERE tagID = 'TAGTAGTAG'; """

pincode = "1234"

db.query(sql)

result = db.store_result()

data = result.fetch_row()

data = data[0][0].decode("utf-8")

if data == pincode:
    ingelogt = True

print(data)

