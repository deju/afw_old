#coding=utf-8
import sys
import traceback
import time
import Image
import tempfile

from tornado.escape import json_encode
from tornado.web import HTTPError

from user import User
from article.avatar import Avatar
from article.about import About
from article.picture import Picture
from article.blog import Blog
from group.basicgroup import BasicGroup
from article.bulletin import Bulletin
from dbase.baserrors import *


from af_front.af_base.AF_Base import *

from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_user.AF_GroupTool import *



class GroupHandler(BaseHandler):
    def get(self, group_id):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        AFGroup = None
        member_type = None
        try:
            group = BasicGroup(_id=group_id)
            AFGroup = AFWBasicGroup(group)
            title = group.name + ' - 小组'
            topic_list, topic_count, topic_page = fun_get_topic_list(group=group, page=1, page_cap=20)
            notice_list, notice_count, notice_page = fun_get_notice_list(group=group, page=1, page_cap=5)
            if user is not None:
                member_type = group.get_member_type(user)
        except Exception:
            error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该小组！',
                'reason': ['该小组不存在！', '或者该小组已经被删除！']}
            return self.send_error(404, **error_info)
        return self.render("group.html", title=title, user=AFUser, group=AFGroup, group_base_type="home",
            topic_list=topic_list, notice_list=notice_list, member_type=member_type)

class GroupLibHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        page = is_value( self.get_argument("page", 1) )
        try:
            page = int(page)
        except Exception, e:
            page = 1
        group_list, total_num, current_page = fun_group_lib(page=page)
        title = '所有小组 - 子曰'
        return self.render("user-group-base.html", user=AFUser, title=title, user_base_type="user-group", 
            kind="group-lib", group_list=group_list,create_page_block=create_page_block,
            total_num=total_num, page=current_page)


class GroupUserGroupHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        AFGroup = {}
        title = '我的小组'
        group_topic_list = fun_group_user_group(user)
        return self.render("user-group-base.html", user=AFUser, title=title, user_base_type="user-group", 
            group=AFGroup, kind="user-group", group_list=group_topic_list)

class GroupApplyHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        AFGroup = {}
        title = '小组 - 正在申请中'
        return self.render("user-group-base.html", user=AFUser, title=title, user_base_type="user-group", 
            group=AFGroup, kind="group-apply")


class GroupCreateHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)

        AFGroup = None
        return self.render("user-group-base.html",title='创建小组 - 子曰',user=AFUser, group=AFGroup, user_base_type="user-group", 
            kind="group-create")
    
    @authfilter
    def post(self):
        user = self.current_user
        result = { 'info':'', 'kind':1 }
        group_name = is_value(self.get_argument("group_name", None))
        group_class = is_value( self.get_argument("group_class", None) )
        group_detail = is_value( self.get_argument("group_des", None) )

        if group_name is None or group_detail is None:
            result['info'] = '请您将小组的信息填写完整！'
            self.write(json_encode(result))
            return
        """ para are ok """
        # create group 
        result['kind'], result['info'] = fun_group_create(user, group_name=group_name, 
            group_detail= group_detail, group_class=group_class)
        self.write(json_encode(result))
        return


class GroupSetLogoHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        group_id = is_value( self.get_argument("id", 1) )
        AFGroup = None
        try:
            group = BasicGroup(_id=group_id)
            #print 'author ,', group.authority_verify(user)
            #print 'member, ', group.member_lib.load_all()
            if group.get_member_type(user) != 'Manager':
                AFGroup = None
            else:
                AFGroup = AFWBasicGroup(group)
        except Exception, e:
            error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该小组！',
                'reason': ['该小组不存在！', '或者该小组已经被删除！']}
            return self.send_error(404, **error_info)

        return self.render("user-group-base.html",title='设置小组Logo - 子曰',user=AFUser, group=AFGroup, user_base_type="user-group", 
            kind="group-logo")


class GroupLibCenterHandler(BaseHandler):
    def get(self, group_id):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception, e:
            page = 1
        try:
            group = BasicGroup(_id=group_id)
        except Exception, e:
            error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该小组！',
                'reason': ['该小组不存在！', '或者该小组已经被删除！']}
            return self.send_error(404, **error_info)
            
        member_type = None
        if user is not None:
            member_type = group.get_member_type(user)
        AFGroup = AFWBasicGroup(group)
        req_url = self.request.uri
        url_path = urlparse.urlparse(req_url)
        url_list = url_path.path.split('/')

        if len(url_list) < 4 or url_list[3] not in ['notice', 'doc', 'topic', 'info', 'feedback', 'member']:
            error_info = { 'my_exc_info': '', 'des':'不支持当前链接！'}
            return self.send_error(404, **error_info) 
        
        if url_list[3] == "notice":
            title = group.name + ' - 小组公告板'
            notice_list, total_num, current_page = fun_get_notice_list(group, page=page)
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='notice', notice_list=notice_list, total_num=total_num, page=current_page,
                create_page_block=create_page_block, member_type=member_type)
        elif url_list[3] == "doc":
            title = group.name + ' - 小组文档'
            tag = is_value(self.get_argument("tag", 'default'))
            doc_list, total_num, current_page = fun_get_doc_list(group, page=page, tag=tag)
            tag_list = group.tag_lib['alltags']
            #print 'tag_list', tag_list
            if tag_list is None:
                tag_list = []
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='doc',create_page_block=create_page_block, tag=tag, doc_list=doc_list,
                total_num=total_num, tag_list=tag_list, member_type=member_type, page=current_page)
        elif url_list[3] == "topic":
            title = group.name + ' - 小组话题'
            topic_list, total_num, current_page = fun_get_topic_list(group, page=page)
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='topic', total_num=total_num, page=current_page, topic_list=topic_list,
                create_page_block=create_page_block, member_type=member_type)
        elif url_list[3]  == "member":
            title = group.name + ' - 小组成员'
            member_list, total_num, current_page = fun_get_member_list(group, page=page, page_cap=9)
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='member', member_list=member_list, total_num=total_num, 
                page=current_page, create_page_block=create_page_block, member_type=member_type)
        elif url_list[3] == "info":
            title = group.name + ' - 关于小组'
            AFGroup.about = group.about.view_body
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='info', member_type=member_type)
        elif url_list[3] == "feedback":
            title = group.name + ' - 小组反馈'
            feedback_list, total_num, current_page = fun_get_feedback_list(group, page=page)
            return self.render("group-lib-base.html", user=AFUser, group=AFGroup, title=title, 
                group_base_type='feedback', feedback_list=feedback_list, create_page_block=create_page_block,
                total_num=total_num, page=current_page, member_type=member_type)
        else:
            pass
            return
           

        

class GroupOneCenterHandler(BaseHandler):
    def get(self, group_id, article_id):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        req_url = self.request.uri
        url_path = urlparse.urlparse(req_url)
        url_list = url_path.path.split('/')
        AFGroup = None
        if len(url_list) < 5 or url_list[3] not in ['topic', 'feedback', 'doc', 'notice']:
            raise Exception
        try:
            group = BasicGroup(_id=group_id)
            AFGroup = AFWBasicGroup(group)
        except Exception:
            error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该小组！',
                'reason': ['该小组不存在！', '或者该小组已经被删除！']}
            return self.send_error(404, **error_info)
        member_type = None
        script = []
        if url_list[3] == "topic":
            try:
                AF_Object = Topic(_id=article_id)
                if AF_Object.group_id != group._id and  AF_Object.is_posted is not True:
                    raise Exception
                if user is not None:
                    member_type = group.get_member_type(user)
            except Exception, e:
                error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该话题！',
                    'reason': ['该话题不存在！', '或者该话题已经被删除！']}
                return self.send_error(404, **error_info)
            else:
                title = AF_Object.name + ' - '+ group.name + '小组话题'
                script = fun_load_code_js(AF_Object.view_body)
                return self.render('group-lib-one-base.html', user=AFUser, group=AFGroup, title=title,
                        group_base_type='topic', article=AF_Object, member_type=member_type, script=script)
                        
        elif url_list[3] == "notice":
            try:
                AF_Object = Bulletin(_id=article_id)
                if AF_Object.group_id != group._id and  AF_Object.is_posted is not True:
                    raise Exception
                if user is not None:
                    member_type = group.get_member_type(user)
            except Exception, e:
                error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该公告！',
                    'reason': ['该公告不存在！', '或者该公告已经被删除！']}
                return self.send_error(404, **error_info)
            else:
                title = AF_Object.name + ' - ' + group.name + '小组公告'
                script = fun_load_code_js(AF_Object.view_body)
                return self.render("group-lib-one-base.html", user=AFUser, group=AFGroup, title=title,
                    group_base_type='notice', article=AF_Object, member_type=member_type, script=script)
        elif url_list[3] == "feedback":
            try:
                AF_Object = Feedback(_id=article_id)
                if AF_Object.group_id != group._id and  AF_Object.is_posted is not True:
                    raise Exception
                if user is not None:
                    member_type = group.get_member_type(user)
            except Exception, e:
                error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该反馈！',
                    'reason': ['该反馈不存在！', '或者该反馈已经被删除！']}
                return self.send_error(404, **error_info)
            else:
                script = fun_load_code_js(AF_Object.view_body)
                title = AF_Object.name + ' - ' + group.name + '小组反馈'
                return self.render("group-lib-one-base.html", user=AFUser, group=AFGroup, title=title,
                    group_base_type='feedback', article=AF_Object, member_type=member_type, script=script)
        elif url_list[3] == "doc":
            try:
                AF_Object = Blog(_id=article_id)
                if AF_Object.group_id != group._id and  AF_Object.is_posted is not True:
                    raise Exception
                if user is not None:
                    member_type = group.get_member_type(user)
            except Exception, e:
                error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该文档！',
                    'reason': ['该文档不存在！', '或者该文档已经被删除！']}
                return self.send_error(404, **error_info)
            else:
                title = AF_Object.name + ' - ' + group.name + '小组文档'
                script = fun_load_code_js(AF_Object.view_body)
                return self.render("group-lib-one-base.html", user=AFUser, group=AFGroup, title=title,
                    group_base_type='doc', article=AF_Object, member_type=member_type, script=script)



class GroupWriteHandler(BaseHandler):
    @authfilter
    def get(self, group_id):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        if user is None:
            return self.redirect('/group/'+ group_id)
        AFGroup = None
        try:
            group = BasicGroup(_id=group_id)
            AFGroup = AFWBasicGroup(group)
        except Exception, e:
            error_info = { 'my_exc_info': traceback.format_exc(), 'des':'未找到该小组！',
                    'reason': ['该小组不存在！', '或者该小组已经被删除！']}
            return self.send_error(404, **error_info)
            
        article_type = is_value(self.get_argument("type", 'topic'))
        article_edit = is_value(self.get_argument("edit", 'false'))
        if article_type not in ['topic', 'doc', 'feedback', 'notice', 'info']:
            article_type = 'topic'
        if article_edit not in ['true', 'false']:
            article_edit = 'false'
        if article_edit == 'false':
            title = {'topic':'写新话题 - '+ group.name ,'doc':'写新文档 - '+group.name,
                     'feedback':'反馈 - '+group.name, 'notice':'写新公告 - '+ group.name,
                     'info':'编辑关于小组 - '+group.name }[article_type]
        else:
            title = {'topic':'修改话题 - '+ group.name ,'doc':'修改文档 - '+group.name,
                     'feedback':'修改反馈 - '+group.name, 'notice':'修改公告 - '+ group.name,
                     'info':'编辑关于小组 - '+group.name }[article_type]
        tag_list = group.tag_lib['alltags']
        if tag_list is None:
            tag_list = []
        if article_type == 'info':
            AFGroup.get_about(group)
        member_type = group.get_member_type(user)
        return self.render("group-write.html",title=title,user=AFUser, group=AFGroup, group_base_type=article_type,
            edit=article_edit, article_type=article_type, tag_list=tag_list, member_type=member_type)



class GroupEditHandler(BaseHandler):
    @authfilter
    def get(self, article_id):
        user = self.current_user
        AFUser = SuperUser(user)
        article_type = is_value(self.get_argument("type", 'topic'))
        if article_type not in ['topic', 'doc', 'notice', 'feedback']:
            return self.redirect("/")
            
        if article_type == 'topic':
            try:
                AF_Object = Topic(_id=article_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) is None or str(AF_Object.author_id) != str(user._id):
                    AFGroup = None
                else:
                    AFGroup = AFWBasicGroup(group)
                    AFObject = SuperArticle(AF_Object)
                    # get the want data
            except (ItemNotFoundError, InvalidIDError, DBIndexError, BaseDBError), e:
                logging.error(e.msg)
                logging.error('Url Error %s' % self.request.uri)
            except Exception, e:
                AFGroup = None
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)

        elif article_type == 'doc':
            try:
                AF_Object = Blog(_id=article_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) != 'Manager' or str(AF_Object.author_id) != str(user._id):
                    AFGroup = None
                else:
                    AFGroup = AFWBasicGroup(group)
                    AFObject = SuperArticle(AF_Object)
                    AFObject.tag_all = AF_Object.tag
            except (ItemNOtFoundError, InvalidIDError, DBIndexError, BaseDBError), e:
                logging.error(e.msg)
                logging.error('Url Error %s' % self.request.uri)
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)
                AFGroup = None
        elif article_type == 'notice':
            try:
                AF_Object = Bulletin(_id=article_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) != 'Manager' or str(AF_Object.author_id) != str(user._id):
                    AFGroup = None
                else:
                    AFGroup = AFWBasicGroup(group)
                    AFObject = SuperArticle(AF_Object)
            except (ItemNotFoundError, InvalidError, DBIndexError, BaseDBError), e:
                logging.error(e.msg)
                logging.error('Url Error %s' % self.request.uri)
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)
                AFGroup = None
        elif article_type == 'feedback':
            try:
                AF_Object = Feedback(_id=article_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) is None or str(AF_Object.author._id) != str(user._id):
                    AFGroup = None
                else:
                    AFGroup = AFWBasicGroup(group)
                    AFObject = SuperArticle(AF_Object)
            except Exception:
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)
                AFGroup = None
        else:
            AFGroup = None
        
        if AFGroup is None:
            return self.redirect("/")
        title = {'topic':'修改话题 - '+ group.name ,'doc':'修改文档 - '+group.name,
                     'feedback':'修改反馈 - '+group.name, 'notice':'修改公告 - '+ group.name,
                     'info':'编辑关于小组 - '+group.name }[article_type]
        tag_list = group.tag_lib['alltags']
        if tag_list is None:
            tag_list = []
        
        member_type = group.get_member_type(user)
        return self.render("group-write.html",title=title,user=AFUser, group=AFGroup, group_base_type=article_type,
            article_type=article_type, tag_list=tag_list, edit='true', article=AFObject, member_type=member_type)
                
        
        

