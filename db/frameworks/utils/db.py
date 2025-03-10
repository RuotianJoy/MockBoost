import pymysql
from db.frameworks.cores.Config import *

class DB:
    db = ''
    cursor = ''

    def __init__(self,db="localhost"):

        if db == "localhost":

            conf = Config().getDB()
            print(conf[0])
        else:
            conf = Config().getOcsOnline()
        self.db = pymysql.connect(host=conf[0],user=conf[1],password=conf[2],port=conf[3],database=conf[4],charset='utf8')
        self.cursor = self.db.cursor()

    def executeSql(self,sql=''):
        try:
            # 执行SQL语句
            result = self.cursor.execute(sql)
            # print(result)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            # print(results)
            if not results:
                results = None
        except:
            print("Error: unable to fecth data")
            results = False

        return results

    def executeSqlMap(self,sql='',table=""):
        rs = self.executeSql(sql)
        colrs = self.executeSql("desc " + table)
        field = []
        for cols in colrs:
            field.append(cols[0])
        newrs = []
        for row in rs:
            option = {}
            for i in range(len(row)):
                option[field[i]] = row[i]
            newrs.append(option)
        print("1")
        # print(newrs)
        return newrs

    def add(self,sql):
        try:
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            return self.cursor.lastrowid
        except:
            self.db.rollback()
            print("Error: add error")
            return False

    def update(self,sql):
        try:
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            return True
        except:
            self.db.rollback()
            print("Error: update error")
            return False

    def update_more(self,sql_list):
        try:
            for sql in sql_list:
                self.cursor.execute(sql)
            self.db.commit()
            return True
        except:
            self.db.rollback()
            print("Error: update error")
            return False

    def delete(self,sql):
        try:
            result = self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            result = True
        except:
            self.db.rollback()
            result = False
            print("Error: delete error")
        return result


