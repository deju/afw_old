# coding=utf-8
import os
import sys
import unicodedata
import codecs
import socket

import tornado.httpserver
import tornado.web
import tornado.ioloop

#from tornado.options import define, options
import tornado.options

from af_front.af_base.AF_Base import *
from af_front.af_base.AF_Tool import is_value
from af_front.af_article import AF_Edit as af_edit
from af_front.af_article import AF_Blog as af_blog
from af_front.af_user import AF_User as af_user
from af_front.af_user import AF_Login as af_login
from af_front.af_user.AF_LoginTool import fun_login
from af_front.af_user import AF_Group as af_group
from af_front.af_book import AF_Book as af_book
from af_front.af_user.AF_UserTool import fun_get_feed_by_id
import afwconfig as AFWConfig


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                (r"/", LoginHandler),
                (r"/code", CodeHandler),
                (r"/reg", af_login.RegisterHandler),
                (r"/check", af_login.CheckHandler),
                (r"/reset", af_login.ResetHandler),
                (r"/login", af_login.LoginDoHandler),
                (r"/repeat-mail", af_login.RepeatMailHandler),
        
                (r"/feed", af_user.FeedHandler),
                #(r"/feed-home", af_user.FeedHomeHandler),
                (r"/user-lib", af_user.AllUserLibHandler),

                (r"/home(.*)", af_user.AuthorBlogLibHandler),             
                (r"/settings-(.+)", af_user.AuthorSettingsHandler),
                (r"/settings", af_user.AuthorSettingsHandler),
                (r"/notice", af_user.AuthorNoticeHandler),
                (r"/upload-image", af_user.UploadImageHandler),
                (r"/crop-image", af_user.CropImageHandler),
                (r"/tag-control", af_user.AuthorTagControlHandler),
                
                (r"/author/(\w+)", af_user.AuthorBlogLibHandler),
                (r"/me:(.+)", af_user.AuthorBlogLibHandler),
                
                (r"/blog-lib", af_user.AuthorBlogManageHandler),
                
                (r"/blog/(.+)", af_blog.BlogHandler),
                
                (r"/bloger/(\w+)/about", af_user.AuthorAllHandler),
                (r"/bloger/(\w+)/follow", af_user.AuthorAllHandler),
                (r"/bloger/(\w+)/like", af_user.AuthorAllHandler),
                (r"/bloger/(\w+)/book", af_user.AuthorAllHandler),
                (r"/bloger(.*)", af_user.AuthorBlogLibHandler),
                (r"/draft", af_user.AuthorDraftLibHandler),
                
                (r"/quit",af_user.AuthorQuitHandler),
                (r"/do-follow", af_user.AuthorDoFollowHandler),
                (r"/do-like", af_user.AuthorDoLikeHandler),
                (r"/del-draft", af_user.AuthorDelDraftHandler),
                (r"/user-group", af_group.GroupUserGroupHandler),

                (r"/update-article", af_blog.UpdateArticleHandler),
                (r"/getcomment", af_blog.GetCommentHandler),              
                
                (r"/write",af_edit.ArticleWriteHandler),
                (r"/article-src-control", af_edit.ArticleSrcHandler),
                
                
                (r"/group-create", af_group.GroupCreateHandler),
                (r"/group-set-logo", af_group.GroupSetLogoHandler),
                (r"/group-lib", af_group.GroupLibHandler),
                (r"/group/(\w+)/topic", af_group.GroupLibCenterHandler),
                (r"/group/(\w+)/notice", af_group.GroupLibCenterHandler),
                (r"/group/(\w+)/doc", af_group.GroupLibCenterHandler),
                (r"/group/(\w+)/member", af_group.GroupLibCenterHandler),
                (r"/group/(\w+)/info", af_group.GroupLibCenterHandler),
                (r"/group/(\w+)/feedback", af_group.GroupLibCenterHandler),
                #(r"/group/(\w+)/write", af_group.GroupWriteHandler),
                (r"/group/(\w+)/edit", af_group.GroupEditHandler),
                (r"/group/(\w+)/topic/(\w+)", af_group.GroupOneCenterHandler),
                (r"/group/(\w+)/doc/(\w+)", af_group.GroupOneCenterHandler),                
                (r"/group/(\w+)/feedback/(\w+)", af_group.GroupOneCenterHandler),
                (r"/group/(\w+)/notice/(\w+)", af_group.GroupOneCenterHandler),

                #(r"/group-edit/(.+)", af_group.GroupEditHandler),


                (r"/group-apply", af_group.GroupApplyHandler),
                (r"/group/(\w+)", af_group.GroupHandler),
                
                (r"/book/(\w+)/catalog/(\w+)", af_book.BookCatalogHandler),
                (r"/book/(\w+)", af_book.BookHandler),
                (r"/book-lib", af_book.BookLibHandler),
                (r"/book-topic-lib/(.+)", af_book.BookLibCenterHandler),
                (r"/book-feedback-lib/(.+)", af_book.BookLibCenterHandler),
                (r"/book-edit/(.+)", af_book.BookEditHandler), 
                (r"/book-create", af_book.BookCreateHandler),
                (r"/user-book", af_book.BookUserBookHandler),
                (r"/book-topic/(.+)", af_book.BookOneCenterHandler),
                (r"/book-feedback/(.+)", af_book.BookOneCenterHandler),
                (r"/book-recommend", af_book.BookRecommendHandler),  
                
                (r"/catalog-control", af_book.BookCatalogControlHandler),
                (r"/help-(.*)", AfewordsHelpHandler),

                (r"/(.*)", NotFoundHandler),
        ]
        
        settings = dict(
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                #debug=True,
                cookie_secret="xxxxx",
                login_url="/",
                autoescape=None,
                xsrf_cookies=True,
                picture_domain="picture1",
                #localhost = True,
        )
        if AFWConfig.afewords_debug is True:
            settings.update({ 'debug': True})
        tornado.web.Application.__init__(self, handlers, **settings)


class LoginHandler(BaseHandler):
    def get(self):
        #print 'ip in login', self.request.remote_ip
        user = self.current_user
        result = {'kind':-1, 'info':''}
        if user is not None:
            return self.redirect("/bloger")
        result = fun_get_feed_by_id(user=None, obj_id=0, page_cap=30)
        if result[0] == 0:
            blog_list = result[1]['feed']
        else:
            blog_list = []
        #result = [0, {'feed':tmp_blog_list, 'last_id': str(last_id), 'is_all':is_all}]
        return self.render("afewords.html",title="子曰 - 执笔写下收获",user=self.current_user, blog_list=blog_list);

    def post(self):
        email = is_value(self.get_argument("email",None))
        password = is_value(self.get_argument("pwd",None))
        
        if email is None or password is None:
            self.redirect('/login?error=1')
            return
        rr1, rr2, usr_id = fun_login(email.lower(), password)
        if rr1 == 1:
            self.redirect('/login?email=' + email + '&error=' + rr2)
            return
        else:
            self.set_cookie("UI", usr_id, expires_days = 7)
            self.set_secure_cookie("UT", usr_id)
            self.set_secure_cookie("IT", self.request.remote_ip)
            self.redirect(rr2)
            return

class AfewordsHelpHandler(BaseHandler):
    def get(self, help):
        if help not in ['about', 'feedback', 'editor-table', 'editor-reference', 'editor-normal',
            'editor-picture', 'editor-letter', 'editor-code', 'editor-math', 'editor-help']:
            next_url = '/group/' + AFWConfig.afewords_group_id
        else:
            group_url = '/group/'+AFWConfig.afewords_group_id
            if help == 'about':
                next_url = group_url + '/info'
            elif help == 'feedback':
                next_url = '/write?group='+ AFWConfig.afewords_group_id +'&type=group-feedback'
            elif help == 'editor-help':
                next_url = group_url + '/doc?tag=Editor'
            elif help == 'editor-table':
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['table']
            elif help == "editor-reference":
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['reference']
            elif help == "editor-code":
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['code']
            elif help == "editor-math":
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['math']
            elif help == "editor-picture":
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['picture']
            elif help == "editor-normal":
                next_url = group_url + '/doc/' + AFWConfig.afewords_edit['normal']
            else:
                next_url = '/group/' + AFWConfig.afewords_group_id
        
        self.redirect(next_url)
        return
        


class NotFoundHandler(BaseHandler):
    def get(self, args):
        user = self.current_user
        if user is None:
            AFUser = None
        else:
            AFUser = SuperUser(user)
        my_error_info = {'des': '本站尚未使用此种链接！',
                          'reason': ['本站未定义该链接！']}
        return self.send_error(404, **my_error_info)

def main():
    port = sys.argv[1]
    if AFWConfig.afewords_debug is not True:
        tornado.options.options['log_file_prefix'].set( AFWConfig.afewords_log_path + str(port))
        tornado.options.parse_command_line()
        tornado.options.options['logging'].set('error')
    
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)  

    http_server.bind(port)
    http_server.start(1)  # Forks multiple sub-processes
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
