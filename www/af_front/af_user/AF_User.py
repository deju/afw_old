#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import traceback
import time
import Image
import tempfile
import logging
import re
import urlparse

from tornado.escape import json_encode
from tornado.escape import url_unescape
from tornado.web import HTTPError

from user import User
from article.avatar import Avatar
from article.about import About
from article.picture import Picture
from article.blog import Blog
from group.basicgroup import BasicGroup


from af_front.af_base.AF_Base import *
from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_article.AF_EditTool import *
from af_front.af_user.AF_LoginTool import *
from af_front.af_book.AF_BookTool import fun_get_user_book

import afwconfig as AFWConfig


class AuthorHomeHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        #print 'aaa'
        return self.render("blog-lib.html", title=AFUser.name, user=AFUser, search_tag="feed", kind="blog")




class AuthorSettingsHandler(BaseHandler):
    @authfilter
    def get(self, kind):
        if kind not in ['avatar', 'info', 'tag', 'like', 'follow', 'follower', 'password', 'about', 'invite', 'domain']:
            kind = 'invite'
        user = self.current_user
        AFUser = SuperUser(user)
        page = is_value( self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception,e:
            page = 1
        if kind == "avatar":
            self.render("user-setting.html", title= AFUser.name + " - 头像", user= AFUser, 
                    user_base_type="settings", kind=kind) 
            return
        elif kind == "domain":
            return self.render("user-setting.html", title=AFUser.name + " - 个性化", user=AFUser,
                user_base_type="settings", kind=kind)
            pass
        elif kind == "tag":
            return self.render("user-setting.html",title= AFUser.name + " - 文章分类",user=AFUser,
                user_base_type="settings", kind=kind )
        elif kind == "like":
            like_list, total_num = fun_get_like_list(user, page=page)
            return self.render("user-setting.html",title= AFUser.name + " - 喜欢",
                user=AFUser,user_base_type="settings", kind=kind, create_page_block=create_page_block,
                page=page, total_num=total_num, like_list=like_list)
        elif kind == "follow":
            follow_list, total_num = fun_get_follow_list(user, page=page)
            return self.render("user-setting.html",title= AFUser.name + " - 关注者",user=AFUser,
                user_base_type="settings", kind=kind, create_page_block=create_page_block,
                page=page, total_num=total_num, follow_list=follow_list)
        elif kind == "follower":
            follower_list, total_num = fun_get_follow_list(user, page=page, follow="follower")
            return self.render("user-setting.html",title= AFUser.name + " - 被关注",user=AFUser,
                user_base_type="settings", kind=kind, create_page_block=create_page_block,
                page=page, total_num=total_num, follower_list=follower_list)
        elif kind == "about":
            AFUser.get_about(user)
            AF_About = user.about
            [pic_lib, ref_lib, code_lib, math_lib, table_lib] = fun_get_article_src(AF_About)
            src_lib = {'p':pic_lib, 'r':ref_lib, 'c':code_lib, 't':table_lib, 'm':math_lib}
            return self.render("user-setting.html",title= AFUser.name + " - 关于我",user=AFUser,src_lib=src_lib,
                user_base_type="settings", kind=kind )
        elif kind == "password":
            return self.render("user-setting.html",title= AFUser.name + " - 密码",user=AFUser,
                user_base_type="settings", kind=kind )
        elif kind == "invite":
            return self.render("user-setting.html",title= AFUser.name + " - 邀请好友",user=AFUser,
                user_base_type="settings", kind=kind )

    @authfilter
    def post(self):
        result = {'kind':1, 'info':''}
        user = self.current_user      
        kind = is_value(self.get_argument("type", None))
        if kind == "info":
            name = is_value(self.get_argument("name", None))
            if name is None or len(name) < 2:
                result['info'] = '请您填写姓名！'
                self.write(json_encode(result))
                return
            else:
                user.name = name
                result['kind'] = 0
                self.write(json_encode(result))
                return
        elif kind == "password":
            old_pwd = is_value(self.get_argument("old_pwd", None))
            new_pwd = is_value(self.get_argument("new_pwd", None))
            result['kind'], result['info'] = fun_edit_password(user, old_pwd, new_pwd)
            self.write(json_encode(result))
            return
        elif kind == "invite":
            invite_email = is_value(self.get_argument("email", None))
            if invite_email is None:
                result['info'] = '邮箱不为空！'
                self.write(json_encode(result))
                return
            result['kind'], result['info'] = fun_invite_friend(user, email=invite_email)
            self.write(json_encode(result))
            return
        elif kind == "domain":
            new_domain = is_value(self.get_argument("new_domain", None))
            if new_domain is None or re.search(r'^[a-zA-Z0-9.]+$', new_domain) is None:
                result['info'] = '后缀为a-z，A-Z,0-9.'
                self.write(json_encode(result))
                return
            result['kind'], result['info'] = fun_new_domain(user, new_domain)
            self.write(json_encode(result))
            return
        else:
            result['kind'] = 1
            result['info'] = '未知操作！'
            self.write(json_encode(result))
            return


class AuthorAllHandler(BaseHandler):
    ''' for like lib, follow lib, about, book'''
    def get(self, pid):
        url_path = self.request.uri
        url_list = urlparse.urlparse(url_path).path.split('/')
        # url_list = ['', 'bloger', 'xxxx', 'like']
        if len(url_list) < 4:
            raise Exception
        user = self.current_user
        AFUser = None
        AFOther = None
        title = '迷路了'
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception:
            page = 1
        if user is not None:
            AFUser = SuperUser(user)
        if user is not None and pid == str(user._id):
            author = user
            AFOther = AFUser
        else:
            try:
                author = User(_id=pid)
                AFOther = SuperUser(author)
            except Exception, err:
                error_info = {'des': '该用户不存在！', 'reason':['该用户不存在！', '或者该用户已经注销！'],
                    'my_exc_info': traceback.format_exc()}
                return self.send_error(404, **error_info)
        # solve the problem        
        if url_list[3] == "about":
            AFOther.get_about(author)
            script =  fun_load_code_js(AFOther.about_view_body)
            title = author.name + ' - 关于我'
            return self.render("blog-about.html",title=title, user=AFUser, author=AFOther, 
            script=script, search_tag='', kind="about")
        elif url_list[3] == "like":
            like_list, total_num = fun_get_like_list(author, page=page)
            title = AFOther.name + u' - 喜欢'
            return self.render("blog-like.html", title=title, user=AFUser, author=AFOther, 
                like_list=like_list, page=page, total_num=total_num, create_page_block=create_page_block,
                search_tag='', kind="like")  
        elif url_list[3] == "follow":
            follow_list, total_num = fun_get_follow_list(author, page=page, page_cap=9)
            title = author.name + u' - 关注'
            return self.render("blog-follow.html",title=title, user=AFUser, author=AFOther, 
                            follow_list=follow_list, search_tag="",page=page,
                            create_page_block=create_page_block,total_num=total_num, kind="follow")
        elif url_list[3] == "book":
             total_num, book_list = fun_get_user_book(author, page=page, page_cap=8)
             title = author.name + u' - 知识谱'
             return self.render("blog-book.html",title=title, user=AFUser, author=AFOther, 
                            search_tag="",page=page, book_list=book_list,
                            create_page_block=create_page_block,total_num=total_num, kind="book")

     
    


class AuthorBlogLibHandler(BaseHandler):
    ''' for all blog '''
    def get(self, other_id):
        if self.request.uri.find('/bloger') == 0:
            url_page = 'bloger'
        elif self.request.uri.find('/author') == 0:
            url_page = 'author'
        else:
            url_page = 'domain'

        user = self.current_user
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception, e:
            page = 1
        tag = is_value(self.get_argument("tag", 'default'))
        tag = url_unescape(tag)
        
        AFUser = None
        AFOther = None
        blog_list = []
        total_num = 0
        title_name = "子曰 - 迷路了"
        ''' user don't have login '''
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        if url_page == "bloger":
            if other_id == "" or other_id == "/":
                if user is None:
                    AFOther = None
                else:
                    AFOther = AFUser
                    blog_list, total_num = fun_get_blog_list_by_tag(user, tag=tag, page=page)
                    if tag != "default":
                        title_name = AFUser.name + u' - ' + tag
                    else:
                        title_name = AFUser.name
            else:
                try:
                    author = User(_id=other_id[1:])
                except Exception, e:
                    error_info = {'des': '该用户不存在！', 'reason':['该用户不存在！', '或者该用户已经注销！'],
                        'my_exc_info': traceback.format_exc()}
                    return self.send_error(404, **error_info)
                else:
                    AFOther = SuperUser(author)
                    blog_list, total_num = fun_get_blog_list_by_tag(author, tag, page=page)
                    if tag == 'default':
                        title_name = AFOther.name
                    else:
                        title_name = AFOther.name + u' - ' + tag
        else:
            # domain page 
            if other_id == "":
                self.redirect("/")
                return
            else:
                try:
                    #print other_id
                    if url_page == "domain":
                        author = User(domain=other_id)
                    else:
                        author = User(_id=other_id)
                except Exception, e:
                    error_info = {'des': '该用户不存在！', 'reason':['该用户不存在！', '或者该用户已经注销！'],
                        'my_exc_info': traceback.format_exc()}
                    return self.send_error(404, **error_info)
                else:
                    AFOther = SuperUser(author)
                    blog_list, total_num = fun_get_blog_list_by_tag(author, tag, page=page)
                    if tag == 'default':
                        title_name = AFOther.name
                    else:
                        title_name = AFOther.name + u' - ' + tag
        if AFUser is None and AFOther is None:
            self.redirect("/")
            return
        return self.render("blog-lib.html",title=title_name,user=AFUser, author=AFOther, 
                    blog_list=blog_list, total_num = total_num, page=page, create_page_block=create_page_block,
                    tag=tag, kind="blog", search_tag=tag)


class AuthorBlogManageHandler(BaseHandler):
    ''' for all blog '''
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        AFOther = AFUser
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception, e:
            page = 1
        tag = is_value(self.get_argument("tag", 'default'))
        tag = url_unescape(tag)
        ''' user don't have login '''

        blog_list, total_num = fun_get_blog_list_by_tag(user, tag=tag, page=page)
        if tag != "default":
            title_name = AFUser.name + u' - ' + tag
        else:
            title_name = AFUser.name + ' - 所有'      
        return self.render("user-blog-manage.html",title=title_name,user=AFUser, author=AFUser, 
                    blog_list=blog_list, total_num = total_num, page=page, create_page_block=create_page_block,
                    tag=tag, kind="blog", search_tag=tag, user_base_type='blog')


class AuthorNoticeHandler(BaseHandler):
    ''' get the notification by the page  '''
    @authfilter
    def get(self):
        user = self.current_user
        page = is_value( self.get_argument("page", 1) )
        try:
            page = int(page)
        except Exception, e:
            page = 1
        
        AFUser = SuperUser(user)
        title_name = AFUser.name + u' - 消息'
        notice_list, total_num, page = fun_get_notice_list(user, page=page)
        #print notice_list
        return self.render('user-setting.html', title=title_name, user=AFUser, author=AFUser, 
                    notice_list=notice_list, total_num=total_num, page=page, create_page_block=create_page_block,
                    user_base_type="settings", kind="notice" )

    @authfilter
    def post(self):
        user = self.current_user
        result = {'kind':-1, 'info':''}
        do = is_value(self.get_argument("do", 'read'))
        index = is_value(self.get_argument("index", 0))
        is_all = is_value(self.get_argument("is_all", 'no'))
        if is_all != "yes":
            try:
                index = int(index)
            except Exception, e:
                index = -1
        result['kind'], result['info'] = fun_set_notice_flag(user, do=do, index=index, is_all=is_all)
        self.write(json_encode(result))
        return

        

class AuthorDraftLibHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        title_name = AFUser.name + u' - 草稿箱'
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception, e:
            page = 1
        draft_list, total_num = fun_get_draft_list(user, page=page)
        #print draft_list
        return self.render("user-setting.html", title=title_name, user=AFUser, author=AFUser, 
                draft_list=draft_list, total_num=total_num, create_page_block=create_page_block, page=page,
                user_base_type="settings", kind="draft")



class AllUserLibHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception, e:
            page = 1
        title_name = '子曰 - 人群'
        #print User.get_instances()
        user_list, total_num = fun_user_lib(user, page=page)
        #print follow
        return self.render("user-lib.html",title=title_name, user=AFUser, user_list=user_list,
            page=page, total_num=total_num, create_page_block=create_page_block, user_base_type="user-lib") 


class AuthorDoFollowHandler(BaseHandler):
    @authfilter
    def post(self):
        user = self.current_user
        result = {'kind':1, 'info':''} 
        follow_id = is_value(self.get_argument("id", None))
        do = is_value(self.get_argument("do", 'follow'))
        follow_type = is_value(self.get_argument("follow_type", 'author'))
        
        if follow_id is None or do not in ['follow', 'unfollow'] or follow_id == str(user._id):
            result['info'] = '参数错误！'
            self.write(json_encode(result))
            return
        if follow_type != 'group':      
            try:
                follower = User(_id=follow_id)
            except Exception, e:
                logging.error('User is not exist, in AuthorDoFollowHandler, user id: %s' % follow_id)
                result['info'] = '该用户不存在！'
                self.write(json_encode(result))
                return
            else:
                if do == "follow":
                    user.follow_user(follower)
                    result['kind'] = 0
                elif do == "unfollow":
                    user.unfollow_user(follower)
                    result['kind'] = 0
                self.write(json_encode(result))
                return
        else:
            # for group follow
            try:
                group = BasicGroup(_id=follow_id)
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)
                result['info'] = '无此小组！'
                self.write(json_encode(result))
                return
            else:
                if do == "follow":
                    user.follow_group(group)
                    result['kind'] = 0
                else:
                    if group.get_member_type(user) == 'Manager':
                        result['info'] = '管理员无法退出！'
                    else:
                        if str(group._id) != AFWConfig.afewords_group_id:
                            user.unfollow_group(group)
                        result['kind'] = 0
                self.write(json_encode(result))
                return


class AuthorDoLikeHandler(BaseHandler):

    def post(self):
        user = self.current_user
        
        result = {'kind':1, 'info':''}
        kind = is_value(self.get_argument("type", None))
        tmp_id = is_value(self.get_argument("id", None))
        do = is_value(self.get_argument("do", None))
        view_time = self.get_cookie("VT",'')

        if do in ['like', 'unlike']:
            if user is None:
                result['info'] = '您未登陆！'
                self.write(json_encode(result))
                return
            
        if kind is None or tmp_id is None or do is None:
            reuslt['info'] = '参数出错！'
            self.write(json_encode(result))
            return
        if do not in ['like', 'unlike', 'view']:
            result['info'] = '不支持当前操作！'
            self.write(json_encode(result))
            return
        if do == 'view':
            try:
                last_time = time.localtime(float(view_time)) 
                current_time = time.localtime()   
            except Exception, e:
                #logging.error(traceback.format_exc())
                #logging.error('Url Error %s ' % self.request.uri)
                result['info'] = '参数错误！'
                self.write(json_encode(result))
                return
            else:
                tmp1 = datetime(*last_time[:6])
                tmp2 = datetime(*current_time[:6])
                tmp3 = tmp2 - tmp1
                if tmp3.seconds < 5:
                    result['info'] = '时间有误！'
                    self.write(json_encode(result))
                    return
            self.set_cookie("VT",'')
        result['kind'], result['info'] = fun_do_like(user, kind, tmp_id, do)
        self.write(json_encode(result))
        return



class FeedHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        page = is_value(self.get_argument("page", '0'))
        page = int(page)
        code, blog, isall = fun_get_feed_by_page_simple(page)
        return self.render("user-feed.html", title="子曰 - 动态", user=AFUser, blog=blog, page=page, isall=isall, user_base_type="feed")

    @authfilter
    def post(self):
        user = self.current_user
        current_id = is_value(self.get_argument("id", None))
        if current_id is None:
            current_id = 0
        result = {'kind':1, 'info':''}
        result['kind'], result['info'] = fun_get_feed_by_id(user=user, obj_id=current_id)
        self.write(json_encode(result))
        return
        

class AuthorDelDraftHandler(BaseHandler):
    @authfilter
    def post(self):
        user = self.current_user
        article_id = is_value(self.get_argument("article_id", None))
        article_type = is_value(self.get_argument("article_type", None))
        
        result = {'kind':1, 'info':''}
        if article_id is None or article_type is None or (article_type not in ['blog', 'comment', 'feedback', 'topic']):
            result['info'] = '参数错误！'
            self.write(json_encode(result))
            return

        if article_type == "blog":
            try:
                obj = Blog(_id=article_id)
                if obj.author_id != user._id:
                    result['info'] = '无权删除！'
                    return self.write(json_encode(result))
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('Blog not exist, id %s' % article_id)
            else:
                user.drafts_lib.delete_obj(article_id)
                result['kind'] = 0
                return self.write(json_encode(result))
        elif article_type == 'topic':
            try:
                obj = Topic(_id=article_id)
                if str(obj.author_id) != str(user._id):
                    result['info'] = '无权删除！'
                    return self.write(json_encode(result))
            except Exception:
                logging.error(traceback.format_exc())
                logging.error('Topic not exist, id %s' % article_id)
            else:
                user.drafts_lib.delete_obj(article_id)
                result['kind'] = 0
                return self.write(json_encode(result)) 
        elif article_type == 'feedback':
            try:
                obj = Feedback(_id=article_id)
                if str(obj.author_id) != str(user._id):
                    result['info'] = '无权删除！'
                    return self.write(json_encode(result))
            except Exception:
                logging.error(traceback.format_exc())
                logging.error('Feedback not exist, id %s' % article_id)
            else:
                user.drafts_lib.delete_obj(article_id)
                result['kind'] = 0
                return self.write(json_encode(result))
        else:
            result['info'] = '开发中！'
            self.write(json_encode(result))
            return



class AuthorTagControlHandler(BaseHandler):
    @authfilter
    def post(self):
        user = self.current_user
        do = is_value( self.get_argument("do", "add") )
        tag = is_value(self.get_argument("tag", None) )
        tag_page = is_value(self.get_argument("page", 'tag'))
        group_id = is_value( self.get_argument("group_id", '-1'))
        result = {'kind': -1, 'info': ''} 
        if tag is None or len(tag) > 45:
            result['info'] = '分类字数需在15字以内！'
            self.write( json_encode(result) )
            return
        if tag == "alltags" or tag == "default":
            result['info'] = '不能操作默认分类！'
            self.write( json_encode(result) )
            return
        if tag_page != 'group-tag':
            target = user
        else:
            try:
                #print 'group_id', group_id
                group = BasicGroup(_id=group_id)
                if group.get_member_type(user) != 'Manager':
                    result['info'] = '您无权进行设置！'
                    self.write(json_encode(result))
                    return
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('Url Error %s' % self.request.uri)
                
                result['info'] = '小组不存在！'
                self.write(json_encode(result))
                return
            else:
                target = group
        ''' can do the control '''
        if do == "add":
            target.tag_lib.add_tag(tag)
            #print target.tag_lib['alltags']
            result['kind'] = 0
            self.write( json_encode(result) )
            return
        elif do == "remove":
            target.tag_lib.remove_tag(tag)
            result['kind'] = 0
            self.write( json_encode(result) )
            return
        else:
            result['info'] = '此操作未定义！'
            self.write( json_encode(result) )
            return 

class AuthorQuitHandler(BaseHandler):
    def get(self):
        #user = self.current_user
        #user.remove()
        self.clear_all_cookies()
        self.redirect("/")
        return
        
class CropImageHandler(BaseHandler):
    @authfilter
    def post(self):
        result = {'kind':1, 'info':''}
        user = self.current_user
        crop_type = is_value(self.get_argument("crop_type", 'avatar'))
        if crop_type not in ['avatar', 'logo', 'article']:
            result['info'] = '不支持当前操作!'
            self.write(json_encode(result))
            return
        pos_x = is_value(self.get_argument("pos-x", None))
        pos_y = is_value(self.get_argument("pos-y", None))
        pos_w = is_value(self.get_argument("pos-w", None))
        pos_time = is_value(self.get_argument("pos-time", 1))
        #print '(x, y, w, pos_time):', pos_x, pos_y, pos_w , pos_time
        try:
            pos_x = int(pos_x)
            pos_y = int(pos_y)
            pos_w = int(pos_w)
            pos_time = float(pos_time)
        except Exception, e:
            result['info'] = '您设置的参数出错，请您确认您的参数！'
            self.write(json_encode(result))
            return
        if pos_w < 150:
            result['info'] = '您设置的参数出错，请您确认您的参数！'
            self.write(json_encode(result))
            return
        
        if crop_type == "avatar":
            # set user avatar
            user_avatar  = (user.avatar).file_name
            #print 'path: ', user_avatar
            if user_avatar == '' or user_avatar is None:
                result['info'] = '您的头像未设置，请您先上传并设置头像！'
                self.write(json_encode(result))
                return
            image_name = urlparse.urlparse(user_avatar).path.split('/').pop()
            result['kind'], result['info'] = fun_save_thumb(image_name, pos_x=pos_x,
                                                pos_y=pos_y, pos_w=pos_w, pos_time=pos_time)
            self.write(json_encode(result))
            return
        elif crop_type == 'logo':
            # crop group logo
            group_id = is_value(self.get_argument("group_id", 1))
            try:
                tmp_group = BasicGroup(_id=group_id)
                if tmp_group.get_member_type(user) != 'Manager':
                    result['info'] = '您无权进行设置！'
                    self.write(result)
                    return
            except Exception, e:
                result['info'] = '参数错误！'
                self.write(result)
                return
            group_avatar = tmp_group.avatar.file_name
            if group_avatar == '' or group_avatar is None:
                result['info'] = '请您先上传小组的Logo'
                self.write(result)
                return
            image_name = urlparse.urlparse(group_avatar).path.split('/').pop()
            result['kind'], result['info'] = fun_save_thumb(image_name, pos_x=pos_x,
                                                pos_y=pos_y, pos_w=pos_w, pos_time=pos_time,
                                                normal_path = AFWConfig.afewords_image_path +"/static/logo/normal/", 
                small_path=AFWConfig.afewords_image_path + "/static/logo/small/")
            self.write(json_encode(result))
            return
        

class UploadImageHandler(BaseHandler):
    ''' all image upload request entrance 
        picture_type = [avatar || article || ...]
        target_type = [blog || comment || avatar || group ]
        target_id = [id || null ]
        article_type == "comment":  need 2 more arguments --- father, name
        article_type == "blog": need 1 more arguments --- name
        article_type == "avatar": need 0 more arguments
        article_type == "group": need 0 more arguments 
        
        Base path:
            in article: http://picture.afewords.com/static/picture/normal/xxx.xxx
                        http://picture.afewords.com/static/picture/small/xxx.xxx
                        subdomain picture1 for test only
            avatar:     http://picture.afewords.com/static/avatar/small/xxx.xxx
                        http://picture.afewords.com/static/avatar/normal/xxx.xxx
            group logo:
                        http://picture.afewords.com/static/logo/small/xxx.xxx
                        http://picture.afewords.com/static/logo/normal/xxx.xxx
    '''
    @authfilter
    def post(self):
        user = self.current_user
        picture_base_domain = "http://" + AFWConfig.afewords_image_domain + ".afewords.com"
        image_path = {
            'avatar':{ 'normal': "/static/avatar/normal/", 'small': "/static/avatar/small/"},
            'logo': {'normal': '/static/logo/normal/', 'small': "/static/logo/small/" },
            'article': {'normal': "/static/picture/normal/", 'small': "/static/picture/small/"}        
        }
        
        result = {'kind': -1, 'info': ''}
        #print 'request:', self.request
        picture_type = is_value(self.get_argument("picture_type", 'article'))
        if self.request.files == {} or 'picture' not in self.request.files:
            self.write('<script>alert("请选择图片！")</script>')
            return
        # get the file and named send_file
        # send_file { 'body' , 'filename', 'content_type'}
        send_file = self.request.files['picture'][0]
        #print send_file['content_type']
        image_type_list = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
        if send_file['content_type'] not in image_type_list:
            self.write('<script>alert("仅支持jpg,jpeg,bmp,gif,png格式的图片！")</script>')
            return
        #print len(send_file['body'])   
        if len(send_file['body']) > 4 * 1024 * 1024:
            restr = '<script>parent.image_upload_handler("'+ picture_type +'", 1,"请选择4M以内的图片!")</script>'
            self.write(restr)
            return
        tmp_file = tempfile.NamedTemporaryFile(delete=True)
        #print dir(tmp_file), type(tmp_file)
        tmp_file.write( send_file['body'] )
        tmp_file.seek(0)
        #print tmp_file.name, tmp_file.mode, tmp_file.encoding
        image_one = ''
        try:
            image_one = Image.open( tmp_file.name )
        except IOError, error:
            logging.error(error)
            logging.error('+'*30 + '\n')
            logging.error(self.request.headers)
            tmp_file.close()
            restr = '<script>parent.image_upload_handler("'+ picture_type +'", 1,"图片不合法!")</script>'
            self.write(restr)
            return
        #print image_one.size
        #print image_one.format
        if image_one.size[0] < 150 or image_one.size[1] < 150 or \
                image_one.size[0] > 2000 or image_one.size[1] > 2000:
            tmp_file.close()
            restr = '<script>parent.image_upload_handler("'+ picture_type +'", 1,"图片长宽在150px~2000px之间!")</script>'
            self.write(restr)
            return
        image_format = send_file['filename'].split('.').pop().lower()
        store_name = "afw_" + random_string(10).lower() + str(int(time.time())) + '.' + image_format.lower()
        #print 'format', image_format
        #print 'store name ', store_name
        if picture_type in ['article', 'avatar', 'logo']:
            full_name_normal = AFWConfig.afewords_image_path + image_path[picture_type]['normal'] + store_name
            full_name_small = AFWConfig.afewords_image_path + image_path[picture_type]['small'] + store_name
            domain_name_normal = picture_base_domain + image_path[picture_type]['normal'] + store_name
            domain_name_small = picture_base_domain + image_path[picture_type]['small'] + store_name
        else:
            self.write('<script>alert("不支持当前上传！")</script>')
            return
        #image_one.save('./1.jpg')
        #if self.request.files['picture'] and 
        #if self.request.files['picture'][0]
        #print '+'*30, self.request.files
        
        
        if picture_type == "article":
            # this is for article , [blog, comment, about ]            
            #print 'picture_type', picture_type
            title = is_value(self.get_argument("title", None))
            article_id = is_value(self.get_argument("article_id", None))
            article_type = is_value(self.get_argument("article_type", None))
            father_id = is_value( self.get_argument("father_id", None) )
            group_id = is_value(self.get_argument("group_id", None))
            if title is None or article_id is None or article_type is None:
                result['info'] = '标题不能为空！'
                restr = '<script>parent.picture_upload_handler(1,"'+ result['info']+'",0,0,-1,0)</script>'
                
                self.write(restr)
                return
            image_one.thumbnail((750,1000),resample = 1)
            image_one.save(str( full_name_normal) )
            image_one.thumbnail((130,120),resample = 1)
            image_one.save(str( full_name_small) )
            result['kind'], result['info'] = fun_new_article_pic(user, article_id=article_id, group_id=group_id,
                    article_type=article_type, title=title, url=domain_name_normal, thumb=domain_name_small, father_id=father_id)
            if result['kind'] == 1:
                restr = '<script>parent.picture_upload_handler(1,"'+ result['info']+'",0,0,-1,0)</script>'
                self.write(restr)
                return
            # right 
            res = result['info']
            #print res['article'], type(res['article'])
            article_id = res['article']
            restr = []
            restr.append('<script>parent.picture_upload_handler(' )
            restr.append(str(result['kind']) + ',"')
            restr.append(domain_name_small + '",')
            restr.append(str(res['alias']) + ',"')
            restr.append(title + '",' + str(res['isnew']) + ',"')
            restr.append(res['article'])
            restr.append('")</script>')
            '''
            restr = ('<script>parent.picture_upload_handler(' 
                        + str(result['kind']) + ',"' 
                        + domain_name_small + '",' 
                        + str(res['alias']) +',"' 
                        + title +'",' + res['isnew']+
                        + ',"' + res['article'] +'")</script>')'''
            self.write(''.join(restr))
            return
                        
        elif picture_type == "avatar":
            # this is for user to set avatar
            image_one.thumbnail((750,1000),resample = 1)
            image_one.save(str( full_name_normal) )
            result['kind'], result['info'] = fun_save_thumb(store_name)
            if result['kind'] == 1:
                restr = '<script>parent.image_upload_handler("avatar", 1,"请选择图片")</script>'
                self.write(restr)
                return
            # set to user 
            #print domain_name_small
            user_avatar = user.avatar
            user_avatar.set_propertys(**{'file_name':domain_name_normal, 'thumb_name':domain_name_small})
            restr = '<script>parent.image_upload_handler("avatar", 0,"'+ domain_name_normal +'")</script>'
            self.write(restr)
            return
            
        elif picture_type == "logo":
            # this is for group to set logo
            group_id = is_value(self.get_argument("group_id", 1))
            try:
                tmp_group = BasicGroup(_id=group_id)
                if tmp_group.get_member_type(user) != 'Manager':
                    restr = '<script>parent.image_upload_handler("logo", 1,"您无权设置！")</script>'
                    self.write(restr)
                    return
            except Exception, e:
                logging.error(e)
                logging.error('Group not exist, ' + group_id)
                restr = '<script>parent.image_upload_handler("logo", 1,"参数出错！")</script>'
                self.write(restr)
                return
            
            image_one.thumbnail((750,1000),resample = 1)
            image_one.save(str( full_name_normal) )
            result['kind'], result['info'] = fun_save_thumb(store_name,
                normal_path = AFWConfig.afewords_image_path +"/static/logo/normal/", 
                small_path=AFWConfig.afewords_image_path + "/static/logo/small/")
            if result['kind'] == 1:
                restr = '<script>parent.image_upload_handler("logo", 1,"请选择Logo")</script>'
                self.write(restr)
                return

            group_avatar = tmp_group.avatar
            group_avatar.set_propertys(**{'file_name':domain_name_normal, 'thumb_name':domain_name_small})
            restr = '<script>parent.image_upload_handler("logo", 0,"'+ domain_name_normal +'", "'+ group_id +'")</script>'
            self.write(restr)
            return
        else:
            pass

