"""
Author: Jelle van Koppen
Date: 23-2-2018
Version: 0.1
Description: Datbase connection to python
"""

import _mysql

db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")


"""
All the sql scripts:

Pull data:

pincode = SELECT pincode FROM gebruikers WHERE tagID = '%s' % tag

klantid = SELECT klantid FROM gebruikers WHERE pincode = '%s' AND tagID = '%s' % pincode, tag

naam = SELECT naam FROM gebruikers WHERE klantid = '%s' % klantid

geblokkeerd = SELECT geblokkeerd FROM gebruikers WHERE klantid = '%s' % klantid

saldo = SELECT saldo FROM rekeningen WHERE rekeningnr = '%s' AND klantid = '%s' % rekeningnr, klantid

=====================================================================================================

Write data:
neem saldo op:

UPDATE rekeningen SET saldo = '%s' WHERE rekeningnr = '%s' % (saldo, rekeningnr)

verander pincode:

UPDATE gebruikers SET pincode = '%s' WHERE klantid = '%s' % (pincode, klantid)

Get poging:
"""

global rows
rows = 0

def fetchData(sql):
    data = []
    global rows
    db.query(sql)
    result = db.store_result()
    rows = result.num_rows()
    for x in range(0,rows):
        data.append(result.fetch_row())
    return data

def pushData(sql):
    db.query(sql)

def selectPincode(tag):
    tag = str(tag)
    sql = "SELECT pincode FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def getKlantid(pincode,tag):
    pincode = str(pincode)
    tag = str(tag)
    sql = "SELECT klantid FROM gebruikers WHERE pincode = '%s' AND tagID = '%s'" % (pincode, tag)
    data = fetchData(sql)
    return data

def getGegevens(klantid):
    klantid = str(klantid)
    sql = "SELECT naam FROM gebruikers WHERE klantid = '%s'" % klantid
    naam = fetchData(sql)
    sql = "geblokkeerd = SELECT geblokkeerd FROM gebruikers WHERE klantid = '%s'" % klantid
    geblokkeerd = fetchData(sql)
    data = (naam,geblokkeerd)
    return data

def getRekening(klantid):
    klantid = str(klantid)
    sql = "SELECT rekeningnr FROM rekeningen WHERE klantid = '%s'" % klantid
    data = fetchData(sql)
    return data

def opnemen(rekeningnr, saldo):
    rekeningnr = str(rekeningnr)
    sql = "UPDATE rekeningen SET saldo = '%s' WHERE rekeningnr = '%s'" % (saldo, rekeningnr)
    data = pushData(sql)
    sql = "SELECT saldo FROM rekeningen WHERE rekeningnr = '%s'" % rekeningnr
    data = fetchData(sql)
    return data
    

def getSaldo(rekeningnr, klantid):
    rekeningnr = str(rekeningnr)
    klantid = str(klantid)
    sql = "SELECT saldo FROM rekeningen WHERE rekeningnr = '%s' AND klantid = '%s'" % (rekeningnr, klantid)
    saldo = fetchData(sql)
    return saldo
    
def manageData(data):
    result = []
    global rows
    try:
        for x in range(0,rows):
            result.append(data[x][0][0])
        return result
    except IndexError:
        print("Error geen data gevonden")

tag = "TAGTAG"
pincode = "5689"
klantid = getKlantid(pincode,tag)
klantid = manageData(klantid)
klantid = klantid[0]
#print (klantid)
rekening = getRekening(klantid)
rekening = manageData(rekening)
#for x in range(0, len(rekening)):
#    print("Rekeningnummers: " + rekening[x])

saldo = getSaldo(rekening[0],klantid)
saldo = manageData(saldo)
saldo = saldo[0]
saldo = int(saldo)
print (saldo)
saldo *= 2
saldo = str(saldo)
geld = opnemen(rekening[0], saldo)
geld = geld[0][0][0]
print (int(geld))

