#coding=utf-8

import bson
import functools
import urlparse
import urllib
import logging as log
from urllib2 import HTTPError

import tornado.web
from tornado.escape import json_encode

from user import User
from article.blog import Blog
from article.status import Status
from article.picture import Picture
from article.tableform import Tableform
from article.equation import Equation
from article.reference import Reference
from article.langcode import Langcode
from article.comment import Comment

from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import fun_get_article_src
import afwconfig as AFWConfig

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        #usr_ip = self.request.headers.get('X-Forwarded-For', self.request.headers.get('X-Real-Ip', self.request.remote_ip))
        #print 'ip', usr_ip
        #print 'In BaseHandler, the client IP is ', self.request.remote_ip
        #print 'settings ', self.application.settings
        #print type(self.request.remote_ip)
        usr_id = self.get_cookie("UI", None)
        usr_id_token = self.get_secure_cookie("UT", None)
        if usr_id is None:
            return None
        if usr_id != usr_id_token:
            self.clear_all_cookies()
            return None
        try:
            usr = User(_id=usr_id)
            if self.request.remote_ip != self.get_secure_cookie('IT', None):
                self.clear_all_cookies()
                return None
        except Exception, e:
            usr = None
        return usr
    
    def get(self):
        return self.redirect("/")
        
    def post(self):
        result = {'kind':-1, 'info':'请您先登陆！'}
        self.write(json_encode(result));
        return 
    
    def get_error_html(self, status_code=500, **kwargs):
    	user = self.current_user
    	if user is not None:
            AFUser = SuperUser(user)
        else:
            AFUser = None
        error_info = dict()
        error_info = kwargs
        error_info['url'] = self.request.protocol + "://" + self.request.host + self.request.uri
        error_info['code'] = status_code
        error_info['debug'] = AFWConfig.afewords_debug
        if 'title' not in error_info:
            title = '迷路了 - 子曰'
        if "des" not in error_info:
            if status_code >=500:
                error_info['des'] = '抱歉，服务器出错！请您将这里的信息复制并作为反馈提交给我们，我们将尽快修复这个问题！'
            else:
                error_info['des'] = "开发人员未给出具体描述！"
        if "next_url" not in error_info:
            error_info['next_url'] = '/'
        if "exc_info" not in error_info:
            if "my_exc_info" not in error_info:
                if status_code >=500:
                    error_info['exc_info'] = '抱歉，服务器出错！'
                else:
                    error_info['exc_info'] = '错误栈未传入错误输出程序！'
            else:
                error_info['exc_info'] = error_info['my_exc_info']
        if "reason" not in error_info:
            error_info['reason'] = [error_info['des']]
        if status_code >= 500:
            logging.error(error_info['exc_info'])
            logging.error('Url Error %s' % self.request.uri)
            
            
        return self.render_string("error.html", user=AFUser, title=title, error=error_info)

class CodeHandler(BaseHandler):
    def get(self):
        ''' create vertify code  '''
        self.set_header('Content-Type','image/gif')
        [buf,code] = create_vertify_code()
        self.set_secure_cookie('ver_code',code.lower())
        self.write(buf)
        return


class BaseUser(object):
    ''' BaseUser package the User'''
    def __init__(self, user):
        self.name = user.name
        self.sex = user.sex      
        self._id = user._id
        self.domain = user.domain     
        tmp_avatar = user.avatar
        self.avatar = tmp_avatar.file_name
        self.thumb_avatar = tmp_avatar.thumb_name
        self.invitations = user.invitations

    def get_base(self, user):
        self.email = user.email
        self.password = user.password
        self.token = user.token

    def get_about(self, user):
        tmp_about = user.about
        self.about_body = tmp_about.body
        self.about_view_body = tmp_about.view_body
        self.about_id = tmp_about._id

    def get_about_lib(self, user):
        tmp_about = user.about
        self.about_img_lib = tmp_about

    def get_drafts(self, user):
        tmp_draft = user.drafts_lib.load_all()
        self.drafts_lib = tmp_draft

    def get_blog(self, user):
        tmp_blog = user.blog
        self.blog = tmp_blog

    def get_follow_lib(self, user):
        self.follow_lib = user.follow_user_lib

    def get_like_lib(self, user):
        self.like_lib = user.favorite_lib
        
    def get_tag(self, user):
        self.tag_lib = user.tag_lib['alltags']
        
    def get_notification_list(self, user):
        self.notification_list = user.notification_list.load_all()
        
    def get_follow_group_lib(self, user):
        self.follow_group_lib = user.follow_group_lib
        
    

class SuperUser(BaseUser):
    def __init__(self, user):
        super(SuperUser, self).__init__(user)
        super(SuperUser, self).get_drafts(user)
        super(SuperUser, self).get_base(user)
        super(SuperUser, self).get_tag(user)
        super(SuperUser, self).get_notification_list(user)
        super(SuperUser, self).get_follow_lib(user)
        super(SuperUser, self).get_follow_group_lib(user)
        self.notification_list_not_read = [i for i in self.notification_list if i is not None and i[1] == False]

class AFWBasicGroup(object):
    def __init__(self, group):
        tmp_avatar = group.avatar
        self.avatar_file = tmp_avatar.file_name
        self.avatar = tmp_avatar.thumb_name
        self._id = group._id
        self.name = group.name
        self.about_view_body = group.about.view_body
        self.about_id = group.about._id
        self.tag_lib = group.tag_lib['alltags']
    
    def get_about(self, group):
        self.about_body = group.about.body
        about_src_list = fun_get_article_src(group.about)
        self.about_src_lib = {'picture_lib': about_src_list[0],
                            'reference_lib': about_src_list[1], 'langcode_lib': about_src_list[2],
                            'equation_lib': about_src_list[3], 'tableform_lib': about_src_list[4]}
        


class BaseArticle(object):
    ''' base article '''
    def __init__(self, blog):
        self.title = blog.name
        self._id = blog._id
        self.abstract = blog.abstract
        self.privilege = blog.privilege
        self.viewbody = blog.view_body
        self.author_id = blog.author_id
        self.statistics = blog.statistics
        self.release_time = blog.release_time
        self.keywords = blog.keywords
        self.tag = blog.tag
        self.body = blog.body

    def get_all_lib(self, blog):
        self.picture_lib = []
        self.equation_lib = []
        self.langcode_lib = []
        self.tableform_lib = []
        self.reference_lib = []
        
        img_lib = blog.picture_lib
        math_lib = blog.equation_lib
        code_lib = blog.langcode_lib
        table_lib = blog.tableform_lib
        ref_lib = blog.reference_lib

        pic_con = Picture.get_instances('_id', img_lib.load_all().values())
        ref_con = Reference.get_instances('_id', ref_lib.load_all().values())
        code_con = Langcode.get_instances('_id', code_lib.load_all().values())
        math_con = Equation.get_instances('_id', math_lib.load_all().values())
        table_con = Tableform.get_instances('_id', table_lib.load_all().values())

        for iii in pic_con:
            self.picture_lib.append({'alias':iii.alias, 'name':iii.name, 'thumb_name':iii.thumb_name})
        for iii in ref_con:
            self.reference_lib.append({'alias':iii.alias, 'name':iii.name, 'url':iii.url, 'body':iii.body})
        for iii in code_con:
            self.langcode_lib.append({'alias':iii.alias, 'name':iii.name, 'lang':iii.lang, 'body':iii.code})
        for iii in math_con:
            self.equation_lib.append({'alias':iii.alias, 'name':iii.name, 'mode':iii.mode, 'body':iii.equation})
        for iii in table_con:
            self.tableform_lib.append({'alias':iii.alias, 'name':iii.name, 'body':iii.tableform})   
               
        
class SuperArticle(BaseArticle):
    ''' super blog  '''
    def __init__(self, blog):
        super(SuperArticle, self).__init__(blog)
        super(SuperArticle, self).get_all_lib(blog)

class BaseBook(object):
    def __init__(self, book):
        self.name = book.name
        self._id = book._id
        tmp_owner = book.owner
        self.owner_id = tmp_owner._id
        self.owner_name = tmp_owner.name
        self.owner_avatar = tmp_owner.avatar.thumb_name
        self.about_view_body = book.about.view_body
        self.about_body = book.about.body
        self.node_lib = node_lib_sort(book.node_lib.load_all())
        self.node_sum = book.node_sum
        self.complete_count = book.complete_count
        if book.node_sum == 0:
            self.complete = 0
        else:
            self.complete = str(int(100*(float(book.complete_count)/book.node_sum)))
        self.about_script = fun_load_code_js(self.about_view_body)
        


def node_lib_sort(node_dict):
    # node_dict = {'1': ['1.1.1', 'section 1']}
    res_list = []
    if len(node_dict) <= 1:
        for item in node_dict:
            tmp_value = node_dict[item]
            res_list.append({ 'node_id':item, 'node_section':tmp_value['section'], 
                'node_title': tmp_value['title'], 'node_article_count': tmp_value['article_count'],
                'node_spec_count': tmp_value['spec_count'], 'node_subcatalog_count': tmp_value['subcatalog_count'] })
        return res_list
    def wrap(x,y):
        x_list = node_dict[x]['section'].split('.')
        x_nest = len(x_list)
        y_list = node_dict[y]['section'].split('.')
        y_nest = len(y_list)
        deep = 0
        def mycmp(deep):
            #    return cmp(node_dict[x][0], node_dict[y][0])
            #print 'deep', deep
            x_int = int(x_list[deep])
            y_int = int(y_list[deep])
            #print 'x_int %s, y_int %s' %(x_int, y_int)
            if deep+1 >= min(x_nest, y_nest):
                if x_nest == y_nest:
                    return cmp(x_int, y_int)
                else:
                    if x_int == y_int:
                        return cmp(node_dict[x]['section'], node_dict[y]['section'])
                    return cmp(x_int, y_int)
                #return cmp(node_dict[x][0], node_dict[y][0])
            if x_int != y_int:
                return cmp(x_int, y_int)
            else:
                deep += 1
                return mycmp(deep)
        return mycmp(0)
    node_id_list = sorted(node_dict, cmp=wrap )
    
    for item in node_id_list:
        tmp_value = node_dict[item]
        res_list.append({ 'node_id': item ,'node_section': tmp_value['section'], 
            'node_title': tmp_value['title'], 'node_article_count': tmp_value['article_count'],
            'node_spec_count': tmp_value['spec_count'], 'node_subcatalog_count': tmp_value['subcatalog_count'] })
        
    return res_list
    



def authfilter(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user is None:
            if self.request.method in ("GET", "POST"):
                #if self.request.method != "POST"  
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urllib.urlencode(dict(next=next_url))
                if self.request.method == "POST":
                    result = {'kind':-1, 'info':'请您先登陆！'}
                    self.write(json_encode(result));
                    return
                else: 
                    self.redirect(url)
                    return  
            raise HTTPError(403)
            return 
        else:  
            return method(self, *args, **kwargs)
    return wrapper


class ErrorHandler(BaseHandler):
    def __init__(self, application, request, status_code):
        #print 'error init'
        tornado.web.RequestHandler.__init__(self, application, request)
        self.set_status(status_code)

    def get_error_html(self, status_code, **kwargs):
        #self.require_setting("static_path")
        if status_code in [403, 404, 500, 503]:
            self.render("error.html", title='子曰--出错了', user=self.current_user, code=status_code)
            return
    
    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)
    
    def get(self):
        self.render("error.html", title='子曰--出错了', user=self.current_user, code=status_code)

tornado.web.ErrorHandler = ErrorHandler


Group_Article = ['group-topic', 'group-info', 'group-feedback', 'group-notice', 'group-doc']
User_Article = ['blog', 'about']
Article_Type = Group_Article + User_Article

Agree_Code = (['as3','applescript','bash','c#','coldfusion','c++','css','delphi','diff',
                            'erlang','groovy','javascript','java','javafx','lisp', 'perl','php','plain',
                            'powershell','python','ruby','sass','scala','sql','vb','xml'])

Agree_Code_Dict = {'applescript':'AppleScript','as3':'AS3','bash':'Bash','coldfusion':'ColdFusion','c++':'Cpp',
        'c#':'CSharp','css':'Css','delphi':'Delphi','diff':'Diff','erlang':'Erlang','groovy':'Groovy','java':'Java',
        'javafx':'JavaFX','javascript':'JScript','lisp': 'Lisp','perl':'Perl','php':'Php','plain':'Plain','python':'Python',
        'ruby':'Ruby','sass':'Sass','scala':'Scala','sql':'Sql','vb':'Vb','xml':'Xml'}
        
Agree_Src = ['math', 'reference', 'table', 'image', 'code']

    