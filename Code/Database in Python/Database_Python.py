"""
Author: Jelle van Koppen
Date: 23-2-2018
Version: 0.1
Description: Datbase connection to python
"""

import _mysql

db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")

#sql = """SELECT pincode FROM gebruikers WHERE tagID = 'TAGTAG';"""

def fetchData(sql):
    db.query(sql)
    result = db.store_result()
    data = result.fetch_row()
    return data

def selectPincode(tag):
    str(tag)
    sql = "SELECT pincode FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def manageData(data):
    try:
        data = data[0][0].decode("utf-8")
        return data
    except IndexError:
        print("Error geen data gevonden")

tag = "TAGTAG"

data = selectPincode(tag)
resultaat = manageData(data)

print(resultaat)

