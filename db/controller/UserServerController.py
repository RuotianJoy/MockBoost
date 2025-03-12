import sys
import time


sys.path.append("../")

from db.model.CommonDb import *
import datetime
from db.frameworks.utils.ApiUtil import *

class UserServerController:
    def __init__(self):
        pass

    # def adduserServerStatus(self, status_data):
    #     model = CommonDb('user')
    #     consequence = model.selectAll(f"username='{status_data['username']}' and password='{status_data['password']}'")
    #     if consequence:
    #         result = False
    #         print('已有此用户，无法添加')
    #     else:
    #         result = model.add(status_data)
    #     return result

    def adduser_student_ServerStatus(self, status_data):
        model = CommonDb('student')
        consequence = model.selectAll(f"username='{status_data['username']}' and password='{status_data['password']}' and stu_no='{status_data['stu_no']}' and major='{status_data['major']}'")
        consequence2 = model.selectAll(f"username='{status_data['username']}'")
        # print("啊？" + str(consequence2))
        print(consequence)
        if consequence != None:
            flag1 = False
        else:
            flag1 = True
        if consequence2 != None:
            flag = False
        else:
            flag = True
        if flag1 and not flag:
            result = False
            print('已有此用户，无法添加')
        else:
            result = model.add(status_data)
        return result

    def adduser_teacher_ServerStatus(self, status_data):
        model = CommonDb('teacher')
        consequence = model.selectAll(f"username='{status_data['username']}' and password='{status_data['password']}' and teach_no='{status_data['teach_no']}' and major='{status_data['major']}'")
        consequence2 = model.selectAll(f"username='{status_data['username']}'")
        # print("啊？"+str(consequence2))
        print(consequence)
        if consequence != None:
            flag1 = False
        else:
            flag1 = True
        if consequence2 != None:
            flag = False
        else:
            flag = True
        if flag1 and not flag:
            result = False
            print('已有此用户，无法添加')
        else:
            result = model.add(status_data)
        return result

    def findlogin_student_ServerStatus(self, status_data):
        model = CommonDb('student')
        consequence = model.selectAll(f"username='{status_data['username']}' and password='{status_data['password']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return result

    def find_student_ServerStatus(self, status_data):
        model = CommonDb('student')
        consequence = model.selectAll(f"username='{status_data['username']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return result

    def findlogin_teacher_ServerStatus(self, status_data):
        model = CommonDb('teacher')
        consequence = model.selectAll(f"username='{status_data['username']}' and password='{status_data['password']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return result

    def make_selfplan(self, status_data):
        model = CommonDb('student')
        consequence = model.selectAll(f"username='{status_data['username']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}

    def get_teacher_info_ServerStatus(self, status_data):
        model = CommonDb('teacher')

        consequence = model.selectAll(f"username='{status_data['username']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}


    def get_student_info_ServerStatus(self, status_data):
        model = CommonDb('student')
        consequence = model.selectAll(f"username='{status_data['username']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}

    def get_recommend_info_ServerStatus(self, status_data):
        model = CommonDb('recommend')
        consequence = model.select_recommend()
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}

    def get_course_info_ServerStatus(self, status_data):
        model = CommonDb('course')

        consequence = model.selectAll_Direct(f"major='{status_data}'","course")

        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}

    def output_string(self,elements):
        return '"' + ''.join(elements) + '"'

    # 调用函数

    def delete_course_info_ServerStatus(self, status_data):
        model = CommonDb('course')
        course = status_data['course']
        course ='"' + course[0] +'"'
        consequence = model.delete_where(f"course={course} and major='{status_data['major']}'")
        print(consequence)
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return {'result': result, 'consequence': consequence}

    def add_course_info_ServerStatus(self, status_data):
        # if status_data['major'] == '计算机科学':
        #     model = CommonDb('cs_course')
        # elif status_data['major'] == '软件工程':
        #     model = CommonDb('se_course')
        model = CommonDb('course')
        course = status_data['course']
        consequence = model.selectAll(f"course='{course}'")
        if consequence:
            result = False
            print('已有，无法添加')
        else:
            result = model.add({'course': course, 'major': status_data['major']})
        return result

    def find_student_Post_ServerStatus(self,data):
        if self.find_student_ServerStatus(data):
            post_model = CommonDb('post')
            comment_model = CommonDb('comment')
            post_consequence = post_model.selectAllPost_Direct(f"")
            comment_consequence = comment_model.selectAllPost_Direct(f"")
            print(post_consequence)
            print(comment_consequence)
            return {'Post': post_consequence, 'Comment': comment_consequence}

    def add_likes_to_post_ServerStatus(self,data):
        model = CommonDb('post')
        likes = {'like_count': int(data['like']) + 1}
        consequence = model.update(likes,'post_no='+str('"'+data['post_no']+'"'))
        print(consequence)
        return True

    def add_comments_to_post_ServerStatus(self,data):
        model = CommonDb('comment')

        consequence = model.add_comment(data)
        print(consequence)
        return True

    def add_post_ServerStatus(self,data):
        model = CommonDb('post')

        consequence = model.add_comment(data)
        print(consequence)
        return True

    def get_sid(self,sname):
        model = CommonDb('student')
        consequence = model.select_sid(sname)
        return consequence


    def get_student_info(self,major):
        model = CommonDb('student')
        consequence = model.select_sinfo(major)
        return consequence

    def get_course_recommend(self):
        model = CommonDb('recommend')
        consequence = model.select_recommend()
        return consequence

    def get_course_recommend_iframe(self,data):
        model = CommonDb('recommend')
        consequence = model.select_recommend_iframe(f"cname='{data['cname']}' and tname ='{data['tname']}'")
        return consequence

    def addcourse_grade(self,data):
        model = CommonDb('student')
        consequence = model.add_grade(data)
        return consequence

    def findlogin_user_ServerStatus(self, data):
        model = CommonDb('user')
        consequence = model.selectAll(f"Name='{data['username']}' and Password='{data['password']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return result

    def find_dialog_info(self,data):
        model = CommonDb('Dialog')
        consequence = model.selectAll(f"UUID='{data['Uid']}'")
        if not consequence:
            result = False
            print('无此项')
        else:
            result = True
        return consequence

    def getUid(self,data):
        model = CommonDb('user')
        consequence = model.selectAll(f"Name='{data['username']}'")
        return consequence


    def adduser_user_ServerStatus(self, status_data):
        model = CommonDb('user')
        consequence = model.selectAll(
            f"Name='{status_data['Name']}' and Password='{status_data['Password']}' and Email='{status_data['Email']}' and Major='{status_data['Major']}' and Job = '{status_data['Job']}' and UUID='{status_data['UUID']}'")
        consequence2 = model.selectAll(f"Name='{status_data['Name']}'")
        # print("啊？"+str(consequence2))
        print(consequence)
        if consequence != None:
            flag1 = False
        else:
            flag1 = True
        if consequence2 != None:
            flag = False
        else:
            flag = True
        if flag1 and not flag:
            result = False
            print('已有此用户，无法添加')
        else:
            result = model.add(status_data)
        return result

    def find_blob_ServerStatus(self, data):
        model = CommonDb('user')
        consequence = model.select_blob(data)
        # consequence = model.select_blob2()

        return consequence


    def insert_blob_ServerStatus(self, name, data):
        model = CommonDb('user')
        consequence = model.insert_blob(name, data)
        return consequence

    def insert_info(self,name,info):
        model = CommonDb('user')
        consequence = model.insert_info(name,info)
        return consequence

    def get_healthy_info(self,name):
        model = CommonDb('user')
        consequence = model.get_info(name)
        return consequence

    def get_table_commit(self,name, data):
        model = CommonDb('user')
        consequence = model.get_table_commit(name, data)
        return consequence

    def get_table_get(self,name):
        model = CommonDb('user')
        consequence = model.get_table_get(name)
        return consequence

    def insert_live_info(self,data):
        model = CommonDb('livemsg')
        consequence = model.insert_live_info(data)
        return consequence

    def get_live_info(self,data):
        model = CommonDb('livemsg')
        consequence = model.get_live_info(data)
        return consequence

    def get_chatmsg_info(self,data):
        model = CommonDb('chatbox')
        consequence = model.get_chatmsg_info(data)
        return consequence

    def get_chatmanmsg_info(self,data):
        model = CommonDb('chatperson')
        consequence = model.get_chatmanmsg_info(data)
        return consequence

    def insert_chatmsg_info(self,data):
        model = CommonDb('chatbox')
        consequence = model.insert_chatmsg_info(data)
        return consequence

    def delete_chatman(self,data):
        model = CommonDb('chatperson')
        consequence = model.delete_chatman(data)
        return consequence

    def add_chatman(self, data):
        model = CommonDb('chatperson')
        consequence = model.add_chatman(data)
        return consequence

    def addUid(self, info):
        model = CommonDb('Dialog')
        consequence = model.add_Dialog(info)
        return consequence
