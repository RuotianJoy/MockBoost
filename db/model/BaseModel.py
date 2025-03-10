from db.frameworks.utils.db import *

class BaseModel(object):
    db = ''
    table = ''

    def __init__(self,dbname="localhost"):
        self.db = DB(dbname)
