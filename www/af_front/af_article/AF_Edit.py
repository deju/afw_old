#coding=utf-8
import sys
import codecs
import traceback
import time
import Image
import tempfile
import re
import logging
from tornado.escape import *

from af_front.af_base.AF_Base import *
from af_front.af_base.AF_Tool import *
from af_front.af_article.AF_EditTool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_user.AF_GroupTool import *

from article.blog import Blog
from article.bulletin import Bulletin
from article.topic import Topic
from article.feedback import Feedback






class ArticleSrcHandler(BaseHandler):
    ''' In this class, we help user to create,update, delete the source which the user need '''
    @authfilter
    def post(self):
        user = self.current_user
        #print 'in new src'
        result = {'kind':1,'info':''}
        do = is_value(self.get_argument("do", 'new'))
        article_id = is_value( self.get_argument("article_id", 0) )
        alias = is_value( self.get_argument("oid", 0))
        src_type = is_value( self.get_argument("src_type", None) )
        article_type = is_value(self.get_argument("article_type", 'blog'))
        father_id = is_value(self.get_argument("father_id", None))
        title = is_value( self.get_argument("title", None) )
        body = is_value( self.get_argument("body", None) )
        source = is_value( self.get_argument("source", None) )
        code_type = is_value( self.get_argument("code_type", 'python') )
        math_type = is_value( self.get_argument("math_type", 'display') )
        group_id = is_value( self.get_argument("group_id", -1) )        
        
        if src_type is None or src_type not in ['math', 'reference', 'code', 'table', 'image']:
            result['info'] = '不支持当前类型的操作！'
            self.write(json_encode(result))
            return
        if do == 'new':
            result['kind'], result['info'] = fun_article_new_src(user, article_id=article_id, article_type=article_type, 
                    src_type=src_type, title=title, body=body, source=source, code_type=code_type, 
                    math_type=math_type, group_id=group_id)
            self.write(json_encode(result))
            return
        
        elif do == "update":
            result['kind'], result['info'] = fun_article_update_src(user, article_id=article_id, article_type=article_type, 
                            src_type=src_type, alias=alias, title=title, group_id=group_id,
                            body=body, source=source, code_type=code_type, math_type=math_type)
            self.write(json_encode(result))
            return
        elif do == "delete":
            pass
            #print 'delete ', src_type 
            result['kind'], result['info'] = fun_article_delete_src(user,group_id=group_id,
                    article_id=article_id, article_type=article_type, src_type=src_type, alias=alias)
            self.write( json_encode(result) )
            return
        else:
            pass
            return


class ArticleWriteHandler(BaseHandler):
    @authfilter
    def get(self):
        #print self.request
        article_id = is_value(self.get_argument("id", None))
        kind = is_value(self.get_argument("type", 'blog'))
        article_type = kind
        group_id = is_value(self.get_argument("group", None))
        if kind not in ['blog', 'group-info', 'group-doc', 'group-feedback', 'group-topic', 'about', 'group-notice']:
            kind = 'blog'
        user = self.current_user
        AFUser = SuperUser(user)
        AFGroup = None
        #print self.get_argument("id", None)

        class_map = { 'blog': Blog, 'group-info': About, 'group-feedback': Feedback, 'group-topic': Topic,
            'about': About, 'group-doc':Blog, 'group-notice':Bulletin }        
        
        mark_map = {'blog':'博客', 'group-info':'关于', 'group-feedback': '反馈', 'group-topic': '话题',
            'about': '关于我', 'group-doc': '文档', 'group-notice': '公告'}
        AF_Object_Env =  None
        edit = False
        mark_str = '写文章'
        if article_id is not None:    
            # this mean is in draft or edit the article
            # /write?id=xxx&type=group-topic
            # /write?id=xxxx
            try:
                AF_Object = class_map[kind](_id=article_id)
                AF_Env = AF_Object.env
                if kind in ['group-info', 'group-topic', 'group-feedback', 'group-doc', 'group-notice']:
                    if AF_Env.__class__.__name__ != 'BasicGroup':
                        error_info = { 'my_exc_info': '参数有误，文章并非属于小组！', 'next_url': '/write', 
                            'des': '参数有误，文章并非属于小组！', 'title':'出错了 - 子曰'}
                        return self.send_error(404, **error_info)
                    else:
                        AF_Object_Env = AFWBasicGroup(AF_Env)
                    mark_str = ('编辑投递在小组<a href="/group/'+ str(AF_Object_Env._id) +
                        '" target="_blank">'+ AF_Object_Env.name +'</a>中的' + mark_map[article_type] ) 
                elif kind in ['blog', 'about']:
                    if AF_Env.__class__.__name__ != 'User':
                        error_info = { 'my_exc_info': '参数有误，文章并非属于您！', 'next_url': '/write', 
                            'des': '参数有误，文章并非属于您！', 'title':'出错了 - 子曰'}
                        return self.send_error(404, **error_info)
                    else:
                        AF_Object_Env = AFUser
                    mark_str = ('编辑' + mark_map[article_type] )
            except Exception, e:
                error_info = { 'my_exc_info': traceback.format_exc(), 'next_url': '/write', 
                    'des': '您无法修改不存在的文章！', 'reason': ['该文章不存在！', '或者该文章已经被删除！']}
                return self.send_error(404, **error_info)
            else:
                edit = True
                AFBlog = SuperArticle(AF_Object)
        else:
            AFBlog = None
            edit = False
            mark_str = '写' + mark_map[article_type]
            if kind in ['group-notice', 'group-feedback', 'group-topic', 'group-doc']:
                try:
                    AF_Env = BasicGroup(_id=group_id)
                    AF_Object_Env = AFWBasicGroup(AF_Env)
                    
                    mark_str = ('给小组<a href="/group/'+ group_id +'" target="_blank">'+ 
                        AF_Object_Env.name +'</a>投递' + mark_map[article_type])
                except Exception, e:
                    error_info = { 'my_exc_info': traceback.format_exc(), 'next_url': '/write', 
                        'des': '小组不存在！', 'reason': ['小组不存在！']}
                    return self.send_error(404, **error_info)
            
            
        #print edit
        #print dir(self.application.reverse_url)
        #print self.application.reverse_url.im_self
        return self.render("user-write.html",title="子曰 - 执笔", user=AFUser, 
            blog=AFBlog, isedit=edit, env=AF_Object_Env, article_type=kind, mark_str = mark_str)
        

