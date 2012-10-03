#coding=utf-8

import sys
import traceback
import logging
import time

from tornado.escape import json_encode

from user import User
from dbase.basedata import convert_id
from article.about import About
from article.status import Status


from af_front.af_base.AF_Base import *
from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_article.AF_BlogTool import *


''' this moudle solve the Specified object, like blog, status, message '''

class BlogHandler(BaseHandler):
    #@authfilter
    def get(self, bid):
        user = self.current_user
        do = is_value(self.get_argument('preview','no'))
        if do not in ['yes', 'no']:
            do = 'no'
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
            #print 'noti list ', AFUser.notification_list
            AFUser.get_like_lib(user)
        recommender_list = []
        
        try:
            #print 'in blog view '
            blog = Blog(_id=bid)
            if not blog.is_posted:
                if user is None or str(blog.author_id) != str(user._id): 
                    raise Exception, 'blog ' + bid + ' have not post!'
                do = 'yes'
            #print 'blog author', blog.author_id
            author = User(_id=blog.author_id)
            AFOther = BaseUser(author)
            title_name = blog.name
            statistics = blog.statistics
            #print statistics, dir(statistics)
            script = fun_load_code_js(blog.view_body)
            blog.comment_count = len(blog.comment_list)
            self.set_cookie('VT', str(time.time()))
            if do == 'no':
                recommender_list = fun_get_recommender_list(blog._id)
        except Exception, e:
            error_info = {'my_exc_info': traceback.format_exc(), 'des': '未找到该文章！',
                'reason': ['该文章不存在！', '或者该文章已被删除！', '或者该文章是不公开的！']}
            return self.send_error(404, **error_info)

        return self.render("blog-view.html",title=title_name, user=AFUser, author=AFOther, 
                blog=blog, statis=statistics, script=script, preview=do, recommender_list=recommender_list)



class UpdateArticleHandler(BaseHandler):
    ''' update the article[maybe create], contains blog post, blog preview, user's about , blog comment'''
    @authfilter
    def post(self):
        user = self.current_user
        do = is_value( self.get_argument("do", "preview"))
        article_id = is_value( self.get_argument("article_id", '-1') )
        title = is_value( self.get_argument("title", None) )
        article_type = is_value( self.get_argument("article_type", None))
        body = is_value( self.get_argument("text", None) )
        summary = is_value( self.get_argument("summary", None) )
        keys = is_value( self.get_argument("keys", []))
        permission = is_value(self.get_argument("permission", 'public'))
        father_id = is_value(self.get_argument("father_id", None))
        father_type = is_value(self.get_argument('father_type', 'blog'))
        classes = is_value(self.get_arguments('classes[]', None))
        ref_comments = is_value(self.get_argument("ref_comment", None))
        group_id = is_value(self.get_argument("group_id", -1))
        isedit = is_value(self.get_argument("edit", 'false'))
        
        #print 'in updateArticle classes', classes
        result = {'kind':1, 'info':''}    
        #print 'want to post', article_id  
        if article_id is None or body is None:
            result['info'] = '内容不能为空！'
            self.write( json_encode(result) )
            return
        if article_type in  ["blog", 'group-doc', 'group-feedback', 'group-notice', 'group-topic']:
            if title is None:
                result['info'] = '标题不能为空！'
                self.write( json_encode(result) )
                return
        else:
            pass

        if summary is None or summary == u"摘要":
            summary = ''

        if permission is None or permission not in ["private", 'public', 'protect']:
            permission = "public"
        if keys is None:
            keys = []
        if classes is None:
            classes = []
        
        result['kind'], result['info'] = fun_update_article(user, article_id=article_id, group_id=group_id,
                                father_type=father_type, father_id=father_id, ref_comments=ref_comments, 
                                title = title, summary=summary,body=body, article_type=article_type, 
                                permission=permission, keys=keys, classes=classes, do=do)
        return self.write( json_encode(result) )
        
        

class GetCommentHandler(BaseHandler):
    def post(self):
        pass
        user = self.current_user
        result = {'kind':1, 'info':''}
        pos = is_value(self.get_argument("pos", 0))
        load_one = is_value( self.get_argument("load_one", 'no') )
        article_type = is_value(self.get_argument("article_type", "blog"))
        article_id = is_value(self.get_argument("article_id", None))
        before_pos = is_value(self.get_argument("before_pos", pos))
        load_before = is_value(self.get_argument("load_before", 'no'))
        #blog_id = is_value(self.get_argument("blog", None))
        #print 'pos: ', pos
        if article_id is None:
            result['info'] = '参数错误！'
            self.write(json_encode(result))
            return
        try:
            if load_one != "yes":
                pos = int(pos)
                before_pos = int(before_pos)
        except Exception, e:
            result['info'] = '参数错误！'
            self.write(json_encode(result))
            return
            
        (result['kind'], result['info']) = fun_get_comment_by_position(article_id=article_id, 
                pos=pos, article_type=article_type, load_one=load_one, before_pos=before_pos, load_before=load_before)
                
        self.write(json_encode(result))
        return

