#coding=utf-8
import sys
import traceback
import logging
import time
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
from catalog import Catalog


from af_front.af_base.AF_Base import *

from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_user.AF_GroupTool import *
from af_front.af_book.AF_BookTool import *


class BookHandler(BaseHandler):
    def get(self, book_id):
        user = self.current_user
        AFUser = None
        AFBook = None
        if user is not None:
            AFUser = SuperUser(user)
        #print self.request.uri
        try:
            book = Catalog(_id=book_id)
            AFBook = BaseBook(book)
        except Exception:
            error_info = {'des': '未找到该知识谱！', 'my_exc_info': traceback.format_exc(),
                'reason': ['该知识谱不存在！', '或者该知识谱已经被删除！']}
            return self.send_error(status_code=404, **error_info)

        want = self.get_argument("want", "cover")
        if want not in ["cover", "summary", "catalog"]:
            want = "cover"
        title = AFBook.name + ' - 知识谱'
        #print AFBook.node_lib
        node_block_html = create_book_catalog_html(AFBook.node_lib,book_id=book._id)
        #print node_block_html
        return self.render("book.html", title=title, user=AFUser, book=AFBook, kind="book", want=want,
            node_block_html=node_block_html)

class BookLibCenterHandler(BaseHandler):
    ''' contain topic lib, feedback lib'''
    def get(self, book_id):
        user = self.current_user
        if user is not None:
            AFUser = SuperUser(user)
        page = is_value(self.get_argument("page", '1'))
        try:
            page = int(page)
        except Exception, err:
            page = 1
        AFBook = None
        title = '知识谱 - '
        try:
            book = Catalog(_id=book_id)
            AFBook = BaseBook(book)
        except Exception, err:
            error_info = {'des': '未找到该知识谱！', 'my_exc_info': traceback.format_exc(),
                'reason': ['该知识谱不存在！', '或者该知识谱已经被删除！']}
            return self.send_error(status_code=404, **error_info)

        req_url = self.request.uri
        if req_url.startswith('/book-topic-lib/'):
            pass
            want = "topic"
        elif req_url.startswith('/book-feedback-lib/'):
            pass
            want = "feedback"
        else:
            return self.redirect("/")
        return self.render("book.html", title=title, user=AFUser, book=AFBook, kind="book-lib", want=want)


class BookOneCenterHandler(BaseHandler):
    ''' contain one topic, one feedback '''
    def get(self):
        pass


class BookEditHandler(BaseHandler):
    ''' edit the book '''
    @authfilter
    def get(self, book_id):
        user = self.current_user
        want = self.get_argument("want", 'summary')
        if want not in ['summary', 'catalog']:
            want = 'summary'
        AFUser = SuperUser(user)
        AFBook = None
        try:
            book = Catalog(_id=book_id)
            AFBook = BaseBook(book)
        except Exception, err:
            error_info = {'des': '未找到该知识谱！', 'my_exc_info': traceback.format_exc(),
                'reason': ['该知识谱不存在！', '或者该知识谱已经被删除！']}
            return self.send_error(status_code=404, **error_info)
        
        title = book.name + ' - 编辑知识谱'
        AFBook.about_object = SuperArticle(book.about)
        article = AFBook.about_object
        node_block_html = create_book_catalog_html(AFBook.node_lib, edit=True, book_id=book._id)
        return self.render("book.html", title=title, user=AFUser, book=AFBook, kind="book-edit", 
            want=want, node_block_html=node_block_html, article=article)


class BookCatalogHandler(BaseHandler):
    def get(self, book_id, node_id):
        user = self.current_user
        AFUser = None
        if user is not None:
            AFUser = SuperUser(user)
        AFBook = None
        try:
            book = Catalog(_id=book_id)
            AFBook = BaseBook(book)
        except Exception:
            error_info = {'des': '未找到该知识谱！', 'my_exc_info': traceback.format_exc(),
                'reason': ['该知识谱不存在！', '或者该知识谱已经被删除！']}
            return self.send_error(status_code=404, **error_info)
        try:
            node_info = fun_get_node_info(user=user, book=book, node_id=node_id)
        except Exception:
            error_info = {'des': '该知识谱没有此章节！', 'my_exc_info': traceback.format_exc(),
                'reason': ['该章节不存在！', '或者该章节已经被删除！']}
            return self.send_error(status_code=404, **error_info)
            
        
        node_block_html = create_book_catalog_html(AFBook.node_lib, book_id=book._id)
        title = node_info['node_section'] + ' - ' + node_info['node_title'] + ' - ' + book.name
        #print node_info
        return self.render("book-node.html", title=title, user=AFUser, book=AFBook, kind="view-node", want="node", 
                node_block_html=node_block_html, current_node=node_info)


class BookRecommendHandler(BaseHandler):
    @authfilter
    def post(self):
        user = self.current_user
        do = is_value(self.get_argument("do", None))
        result = {'kind':1, 'info': ''}
        if do not in ['recommend_to_book', 'recommended_to_book', 'del_recommend', 'mark_recommend']:
            result['info'] = '无法识别操作！'
            return self.write(json_encode(result))
        if do == "recommend_to_book":
            article_id = is_value(self.get_argument("article_id", '-1'))
            article_type = is_value(self.get_argument("article_type", 'blog'))
            section_url = is_value(self.get_argument("url",'-1'))
            if article_type not in ['blog']:
                result['info'] = '不支持推荐的当前的文章！'
                return self.write(json_encode(result))
            result['kind'], result['info'] = fun_recommend_to_book(user=user, article_id=article_id,
                    article_type=article_type, section_url=section_url)
            return self.write(json_encode(result)) 
        else:
            book_id = is_value( self.get_argument("book_id", None))
            node_id = is_value( self.get_argument("node_id", None))
            relation_id = is_value(self.get_argument("relation_id", None))
            if book_id is None or node_id is None:
                result['info'] = '参数错误，请提供知识谱和章节！'
                return self.write(json_encode(result))
            
            if do == "del_recommend":
            
                if relation_id is None:
                    result['info'] = '请说明删除的文章！'
                    return self.write(json_encode(result))
                result['kind'], result['info'] = fun_del_recommend(user=user, book_id=book_id,
                        node_id=node_id, relation_id=relation_id)
                return self.write(json_encode(result))
                
            elif do == "mark_recommend":
                if relation_id is None:
                    result['info'] = '请指定文章！'
                    return self.write(json_encode(result))
                result['kind'], result['info'] = fun_del_recommend(user=user, book_id=book_id,
                        node_id=node_id, relation_id=relation_id, want="mark_recommend")
                return self.write(json_encode(result))  
            else:
                # recommend the catalog to catalog
                target_url = is_value(self.get_argument("url", None))
                if target_url is None:
                    result['info'] = '请填写链接！'
                    return self.write(json_encode(result))
                result['kind'], result['info'] = fun_recommended_to_book(user=user, book_id=book_id, node_id=node_id, article_url=target_url)
                
                return self.write(json_encode(result))


class BookCatalogControlHandler(BaseHandler):
    @authfilter
    def post(self):
        user = self.current_user
        result = {'kind':1 ,'info':''}
        do = is_value(self.get_argument("do", "add_catalog"))
        if do not in ["add_catalog", "edit_catalog", "del_catalog"]:
            result['info'] = '不支持当前操作！'
            return self.write(json_encode(result))
        
        book_id = is_value(self.get_argument("book_id", None))
        if book_id is None:
            result['info'] = '未指定知识谱，无法操作！'
            return self.write(json_encode(result))
            
        try:
            book = Catalog(_id=book_id)
        except Exception, err:
            logging.error(traceback.format_exc())
            result['info'] = '找不到该知识谱！'
            return self.write(json_encode(result))
        section = is_value(self.get_argument("section", None))
        title = is_value(self.get_argument("title", None))
        node_id = is_value(self.get_argument("node_id", None))
        if do == "add_catalog":
            result['kind'], result['info'] = fun_add_node(user, book=book, section=section, title=title)
            return self.write(json_encode(result))
        elif do == "edit_catalog":
            result['kind'], result['info'] = fun_update_node(user, book=book, node_id=node_id, section=section, title=title)
            return self.write(json_encode(result))
        else:
            result['kind'], result['info'] = fun_del_node(user, book=book, node_id=node_id)
            return self.write(json_encode(result))
                




class BookUserBookHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        title = '我的知识谱 - 子曰'
        page = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception:
            page = 1
        total_num, book_list = fun_get_user_book(user, page=page, page_cap=8)
        return self.render("user-book-base.html", user=AFUser, title=title, user_base_type="user-book",
            kind="user-book", book_list=book_list,total_num=total_num, page=page, create_page_block=create_page_block)
        
        
class BookLibHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        page  = is_value(self.get_argument("page", 1))
        try:
            page = int(page)
        except Exception:
            page = 1 
        title = '知识谱 - 子曰'
        total_num, book_list = fun_get_all_book(user=user, page=page, page_cap=8)
        return self.render("user-book-base.html", user=AFUser, title=title, user_base_type="user-book",
            kind="book-lib", book_list=book_list, total_num=total_num, page=page, create_page_block=create_page_block)
    
    

class BookCreateHandler(BaseHandler):
    @authfilter
    def get(self):
        user = self.current_user
        AFUser = SuperUser(user)
        title = '创建知识谱 - 子曰' 
        return self.render("user-book-base.html", user=AFUser, title=title, user_base_type="user-book",kind="book-create")  
           
    @authfilter
    def post(self):
        user = self.current_user
        result = {'kind':1, 'info': ''}
        title = is_value( self.get_argument("book_name", None) )
        summary = is_value( self.get_argument("book_summary", None) )
        if title is None or len(title) > 100:
            result['info'] = '请填写知识谱名！'
            return self.write(json_encode(result))
        if summary is None or summary == "":
            result['info'] = '请您填写内容摘要！'
            return self.write(json_encode(result))
        result['kind'], result['info'] = fun_new_book(user=user, name=title, summary=summary)
        return self.write(json_encode(result))
    