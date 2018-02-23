"""
Author: Jelle van Koppen
Date: 23-2-2018
Version: 0.1
Description: Datbase connection to python
"""

import _mysql

db = _mysql.connect(host="localhost", user="", passwd="")
