from db.model.BaseModel import *
import datetime
import json
import json

class CommonDb(BaseModel):
    def __init__(self,tablename,dbname=""):
        if dbname == "":
            BaseModel.__init__(self)
        else:
            BaseModel.__init__(self,dbname)
        self.table = tablename

    def add(self,info,isctime=False,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:]+ ") ON DUPLICATE KEY UPDATE " + sUpdateSql[:-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)


    def add_comment(self,info,isctime=False,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:]+ ") ON DUPLICATE KEY UPDATE " + sUpdateSql[:-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)

    def select(self,page,num,field,desc):
        if page <= 1:
            start = 0;
        else:
            start = (page-1) * num;
        sql = "select * from " + self.table + " order by " + field + " " + desc + " limit " + str(start) + "," + str(num) +  ";"
        print(sql)
        return self.db.executeSql(sql)

    def select_sid(self,sname):
        print(sname)
        sql = "select stu_no from " + self.table + " where username = "+sname+";"
        print(sql)
        return self.db.executeSql(sql)

    def selectAll(self,wheresql,optionstr="*",map=False):
        print(wheresql)
        sql = "select " + optionstr + " from " + self.table + " where 1 and " + wheresql + ";"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql,self.table)
        else:
            return self.db.executeSql(sql)

    def select_recommend(self,  map=False):

        sql = "select c_name,t_name,href from "+ self.table + " where 1  " + ";"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql, self.table)
        else:
            return self.db.executeSql(sql)

    def select_sinfo(self,wheresql,map=False):
        print(wheresql)
        sql = "select username,stu_no,grade from " + self.table + " where 1 and major = " + "'"+wheresql + "'"+" group by username,stu_no,grade;"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql,self.table)
        else:
            return self.db.executeSql(sql)

    def select_recommend(self,map=False):

        sql = "select cname,tname,href from " + self.table + " where 1 ;"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql,self.table)
        else:
            return self.db.executeSql(sql)

    def select_recommend_iframe(self,wheresql,map=False):

        sql = "select href from " + self.table + " where 1 and "+ wheresql     +";"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql,self.table)
        else:
            return self.db.executeSql(sql)

    def selectAll_Direct(self, wheresql, optionstr, map=False):
        print(wheresql)
        sql = "select " + optionstr + " from " + self.table + " where 1 and " + wheresql + ";"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql, self.table)
        else:
            return self.db.executeSql(sql)

    def selectAllPost_Direct(self, wheresql, optionstr="*", map=False):
        print(wheresql)
        sql = "select " + optionstr + " from " + self.table + " where 1 " + wheresql + ";"
        print(sql)
        if map:
            return self.db.executeSqlMap(sql, self.table)
        else:
            return self.db.executeSql(sql)

    def selectByWhere(self,wheresql,page,num,field,desc):
        if page <= 1:
            start = 0;
        else:
            start = (page-1) * num;
        sql = "select * from " + self.table + " where 1 and " + wheresql + " order by " + field + " " + desc + " limit " + str(start) + "," + str(num) +  ";"
        print(sql)
        return self.db.executeSql(sql)

    def update(self,info,wheresql):
        sUpdateSql = ""
        for key in info.keys():
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        sql = "update " + self.table + " set " + sUpdateSql[0:-1] + " where 1 and " + wheresql;
        print(sql)
        return self.db.update(sql)

    def add_grade(self,data):
        sql = "update " + self.table + " set c_grade= " +"'"+ str(data['c_grade']) +"'"+ " where 1 and " + ' username= '+"'"+ str(data['username']) +"'"+ " and course=" +"'"+ str(data['course']+"'");
        print(sql)
        return self.db.update(sql)

    def delete_where(self,wheresql):
        sql = "delete from " + self.table + " where 1 and " + wheresql + ";"
        print(sql)
        return self.db.update(sql)

    def delete_chatman(self,data):
        sql = "delete from " + self.table + " where username = " + "'"+str(data['username'])+"'" + ";"
        print(sql)
        return self.db.update(sql)

    def executeMap(self,sql):
        print(sql)
        return self.db.executeSqlMap(sql,self.table)

    def execute(self,sql):
        return self.db.executeSql(sql)

    def update_delete(self,info,wheresql):
        sql_test = info + " = " + "null"

        sql = "update " + self.table + " set " + sql_test + " where 1 and " + wheresql + ";"
        print(sql)
        return self.db.update(sql)

    def addcourse(self,info):


        sql = "insert into " + self.table + "(course) values(" + info[1] + ");"
        print(sql)
        return self.db.add(sql)

    def select_blob(self, data):

        sql = "select photo from " + self.table + " where username = " +"'"+ str(data['username']) +"'"+ " and phone = " + "'"+str(data['phone'])+ "'"+" and password = " + "'"+ str(data['password']) + "'"+ ";"
        print(sql)
        return self.db.executeSql(sql)

    def select_blob2(self):

        sql = "select photo from " + self.table + " where username = 'ljy'"+";"
        print(sql)
        return self.db.executeSql(sql)

    def insert_blob(self, name, data):
        sql = "update " + self.table + " set photo= " + "'" + json.dumps(data) + "'" + " where 1 and " + ' username= ' + "'" + str(name) + "'" + ";"
        print(sql)
        return self.db.update(sql)

    def insert_info(self,name,info):
        print(type(json.dumps(info)))
        sql = "update " + self.table + " set info= " + "'"+ json.dumps(info,ensure_ascii=False) +"'"+ " where 1 and " + ' username= ' + "'" + str(name) + "'" + ";"
        print(sql)
        return self.db.update(sql)

    def get_info(self,name):
        sql = "select info from " + self.table + " where 1 and " + ' username= ' + "'" + str(name) + "'" + ";"
        print(sql)
        return self.db.executeSql(sql)

    def get_table_commit(self,name,data):
        sql = "update " + self.table + " set htable= " + "'" + json.dumps(data,ensure_ascii=False) + "'" + " where 1 and " + ' username= ' + "'" + str(name) + "'" + ";"
        print(sql)
        return self.db.update(sql)

    def get_table_get(self,name):
        sql = "select htable from " + self.table + " where 1 and " + ' username= ' + "'" + str(name) + "'" + ";"
        print(sql)
        return self.db.executeSql(sql)


    def get_live_info(self,data):
        sql = "select * from " + self.table + " where 1 ; "
        print(sql)
        return self.db.executeSql(sql)

    def get_chatmsg_info(self,data):
        sql = "select * from " + self.table + " where 1 ; "
        print(sql)
        return self.db.executeSql(sql)

    def get_chatmanmsg_info(self,data):
        sql = "select username from " + self.table + " where 1 ; "
        print(sql)
        return self.db.executeSql(sql)


    def insert_chatmsg_info(self,info,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ") ON DUPLICATE KEY UPDATE " + sUpdateSql[:-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)

    def insert_live_info(self,info,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ") ON DUPLICATE KEY UPDATE " + sUpdateSql[:-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)

    def add_chatman(self,info,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ") ON DUPLICATE KEY UPDATE " + sUpdateSql[:-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)

    def add_Dialog(self, info,noUpdate=False):
        sInsertField = ""
        sInsertValue = ""

        sUpdateSql = ""
        for key in info.keys():
            sInsertField += "," + key
            sInsertValue += ",\"" + str(info[key]) + "\""
            sUpdateSql += key + "=\"" + str(info[key]) + "\","
        if noUpdate:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ") ON DUPLICATE KEY UPDATE " + sUpdateSql[
                                                                                                                            :-1] + ";"
        else:
            sql = "insert into " + self.table + "(" + sInsertField[1:] + ") values(" + sInsertValue[1:] + ");"
        print(sql)
        return self.db.add(sql)

