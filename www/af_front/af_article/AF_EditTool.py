#coding=utf-8

import traceback
import logging

from tornado import escape


from user import User
from article.about import About
from article.blog import Blog
from article.reference import Reference
from article.picture import Picture
from article.equation import Equation
from article.langcode import Langcode
from article.tableform import Tableform
from group.basicgroup import BasicGroup
from article.topic import Topic
from article.feedback import Feedback
from article.bulletin import Bulletin
from authority import *
from catalog import Catalog


from af_front.af_base.AF_Tool import *
from af_front.af_base.AF_Base import *



def fun_article_new_src(user, article_id='-1', article_type='blog', src_type='code',
            title='', body='', source='', code_type='python', math_type='inline', father_id='-1', group_id='-1'):
    if article_type not in Article_Type:
        return [1, '不支持当前文章类型！']
    if src_type not in Agree_Src:
        return [1, '不支持当前类型的资源！']
        
    if title is None:
        return [1, '名称不能为空！']
        
    if body is None:
        if src_type != 'reference':
            return [1, '内容不能为空！']
        else:
            if re.search(r'^(http|https|ftp):\/\/.+$', source) is None:
                return [1, '请填写链接地址或者引用真实内容！']
            body = ''
    else:
        if src_type == 'math':    
            body = math_encode(escape.xhtml_unescape(body))
        elif src_type == 'code':
            if code_type not in Agree_Code:
                return [1, '请选择代码种类！']
    
    if article_type == "about":
        AF_Object = user.about
        article_id = str(user.about._id)
        isnew = False
    elif article_type == "book-about":
        isnew = False
        try:
            book = Catalog(_id=group_id)
            AF_Object = book.about
            limit = book.authority_verify(user)
            if test_auth(limit, A_WRITE) is False:
                return [1, '您无权修改摘要！']
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % group_id)
            return [1, '未找到知识谱！']
    elif article_type == "blog":
        try:
            AF_Object = Blog(_id=article_id)
            isnew = False
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('%s not exist, id %s' % (article_type, article_id))
            AF_Object = Blog()
            AF_Object.author = user
            AF_Object.env = user
            article_id = str(AF_Object._id)
            isnew = True       
            (user.drafts_lib).add_obj(AF_Object)     
    elif article_type == "comment":
        return [1, '完善中']
    elif article_type in Group_Article:
        # for group
        isnew = False
        try:
            group = BasicGroup(_id=group_id)
            limit = group.authority_verify(user)
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('Group not exist, id %s' % group_id)
            return [1, '参数错误，小组不存在！']
        
        class_map = { 'group-info': About, 'group-doc': Blog, 'group-feedback': Feedback, 
            'group-notice': Bulletin, 'group-topic': Topic}
            
        user_role = group.get_member_type(user)
        if user_role is None:
            return [1, '您不是该小组成员！']
        if article_type in ['group-info', 'group-doc', 'group-notice']:
            if user_role != 'Manager':
                return [1, '您不是管理员，无权操作！']
        
        if article_type == "group-info":
            AF_Object = group.about
        else:
            try:
                AF_Object = class_map[article_type](_id=article_id)
            except Exception:
                AF_Object = class_map[article_type]()
                AF_Object.author = user
                AF_Object.env = group
                AF_Object.group_id = group._id
                isnew = True
            if AF_Object.group_id != group._id or AF_Object.author_id != user._id:
                return [1, '您不能操作该文章！']
            if isnew:
                if article_type in ['group-topic', 'group-feedback']:
                    user.drafts_lib.add_obj(AF_Object)
                elif article_type in ['group-notice', 'group-doc']:
                    group.drafts_lib.add_obj(AF_Object)

    article_id = str(AF_Object._id)

    rstring = {'isnew':isnew, 'article':article_id, 'alias':''}

    if src_type == 'reference':
        ref_lib =  AF_Object.reference_lib
        alias = get_max_alias(ref_lib.load_all().keys())
        new_ref = Reference()
        new_ref.set_propertys(**{'alias':alias, 'url':source, 'name':title, 'body':body})
        ref_lib.add_obj(new_ref)
        rstring['alias'] = alias
        return [0, rstring]
    elif src_type == 'code':
        code_lib = AF_Object.langcode_lib
        alias = get_max_alias(code_lib.load_all().keys())
        new_code = Langcode()
        new_code.set_propertys(**{'alias':alias, 'name':title, 'code':body, 'lang':code_type})
        code_lib.add_obj(new_code)
        rstring['alias'] = alias
        return [0, rstring]
    elif src_type == 'math':
        math_lib = AF_Object.equation_lib
        alias = get_max_alias(math_lib.load_all().keys())
        new_math = Equation()
        new_math.set_propertys(**{'alias':alias, 'name':title, 'equation':body, 'mode':math_type})
        math_lib.add_obj(new_math)
        rstring['alias'] = alias
        return [0, rstring]
    elif src_type == 'table':
        table_lib = AF_Object.tableform_lib
        alias = get_max_alias(table_lib.load_all().keys())
        new_table = Tableform()
        new_table.set_propertys(**{'alias':alias, 'name':title, 'tableform':body})
        table_lib.add_obj(new_table)
        rstring['alias'] = alias
        return [0, rstring]
    else:
        return [1,'本站尚不支持此类型资源，我们将继续改进！']



def fun_new_article_pic(user, article_id=0, article_type='blog', title='', url='', thumb='', father_id=0, group_id='-1'):
    isnew = 0
    if article_type not in Article_Type:
        return [1, '不支持当前文章类型！']
        
    if article_type == "about":
        AF_Object = About(_id=user.about._id)
        isnew = 0
    elif article_type == "book-about":
        try:
            book = Catalog(_id=group_id)
            AF_Object = book.about
            limit = book.authority_verify(user)
            if test_auth(limit, A_WRITE) is False:
                return [1, '您无权修改摘要！']
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % group_id)
            return [1, '未找到该目录！']
        #print 'in about update', AF_Object
    elif article_type == "blog":
        try:
            AF_Object = Blog(_id=article_id)
            #print AF_Object.author_id, user._id
            if str(AF_Object.author_id) != str(user._id):
                return [1, '无权限操作他人的文章！'] 
            isnew = 0
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('%s not exist, id %s' % (article_type, article_id))
            AF_Object = Blog()
            AF_Object.author = user
            AF_Object.env = user
            article_id = str(AF_Object._id)
            isnew = 1  
            user.drafts_lib.add_obj(AF_Object)    
    elif article_type == "comment":
        return [1, '评论中不支持图片！']
    else:
        # for group
        isnew = 0 # not new 
        try:
            group  = BasicGroup(_id=group_id)
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('Group not exist ' + group_id)
            return [1, '小组不存在！']
            
        class_map = { 'group-info': About, 'group-doc': Blog, 'group-feedback': Feedback, 
            'group-notice': Bulletin, 'group-topic': Topic}
        user_role = group.get_member_type(user)
        if user_role is None:
            return [1, '您不是该小组成员！']
        if article_type in ['group-info', 'group-doc', 'group-notice']:
            if user_role != 'Manager':
                return [1, '您不是管理员，无权操作！']
        
        if article_type == "group-info":
            AF_Object = group.about
        else:
            try:
                AF_Object = class_map[article_type](_id=article_id)
            except Exception:
                AF_Object = class_map[article_type]()
                AF_Object.author = user
                AF_Object.env = group
                AF_Object.group_id = group._id
                isnew = 1
            if AF_Object.group_id != group._id or AF_Object.author_id != user._id:
                return [1, '您不能操作该文章！']
            if isnew == 1:
                if article_type in ['group-topic', 'group-feedback']:
                    user.drafts_lib.add_obj(AF_Object)
                elif article_type in ['group-notice', 'group-doc']:
                    group.drafts_lib.add_obj(AF_Object)


    img_lib = AF_Object.picture_lib
    alias = get_max_alias(img_lib.load_all().keys())
    new_img = Picture()
    new_img.set_propertys(**{'alias':alias, 'name':title, 'file_name':url, 'thumb_name':thumb})
    img_lib.add_obj(new_img)
    article_id = str(AF_Object._id)
    rstring = {'isnew':isnew, 'article':article_id, 'alias':alias}
    return [0, rstring]
    

def fun_article_update_src(user, article_id=0, article_type='blog', 
                            src_type='code', alias='1', title='', 
                            body='', source='', code_type='python', math_type='inline', group_id='-1'):
    '''
        update the lib of the article, article_type is about|blog|comment
        article_id must be have
        need alias too, then we find the lib _id, create the object, and set of it
    '''
    if article_type not in Article_Type:
        return [1, '不支持当前文章类型！']
    if src_type not in Agree_Src:
        return [1, '暂不支持当前资源的类型！']
        
    if title is None:
        return [1, '请您填写标题/名称！']
              
    if src_type != 'image':
        if body is None:
            if src_type == 'r':
                if source is None:
                    return [1, '出处不能为空']
                if re.search(r'^(http|https|ftp):\/\/.+$', source) is None:
                    return [1, '请填写链接地址或者引用真实内容！']
                body = ''
            else:
                return [1, '内容不能为空！']
        
        if src_type == 'math':
            if math_type not in ['display', 'inline']:
                math_type  = 'display'
                body = math_encode( xhtml_unescape(body) )

        if src_type == 'code':
            if code_type not in Agree_Code:
                return [1, '目前不支持此类型的程序代码！']
                
    if article_type == "about":
        AF_Object = About(_id=user.about._id)
    elif article_type == "book-about":
        try:
            book = Catalog(_id=group_id)
            AF_Object = book.about
            limit = book.authority_verify(user)
            if test_auth(limit, A_WRITE) is False:
                return [1, '您无权修改！']
            pass
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % group_id)
            return [1, '未找到该知识谱！']
    elif article_type == "blog":
        try:
            AF_Object = Blog(_id=article_id)
            if str(AF_Object.author_id) != str(user._id):
                return [1, '无权限操作他人的文章！']
        except Exception, e:
            return [1, '文章不存在']      
    elif article_type in Group_Article:
        # for group
        try:
            group = BasicGroup(_id=group_id)
            limit = group.authority_verify(user)
        except Exception, e:
            logging.error('Group not exist, id %s' % group_id)
            return [1, '小组不存在！']
            
        class_map = { 'group-info': About, 'group-doc': Blog, 'group-feedback': Feedback, 
            'group-notice': Bulletin, 'group-topic': Topic}
        user_role = group.get_member_type(user)
        if user_role is None:
            return [1, '您不是该小组成员！']
        if article_type in ['group-info', 'group-doc', 'group-notice']:
            if user_role != 'Manager':
                return [1, '您不是管理员，无权操作！']
        
        if article_type == "group-info":
            AF_Object = group.about
        else:
            try:
                AF_Object = class_map[article_type](_id=article_id)
            except Exception:
                AF_Object = class_map[article_type]()
                AF_Object.author = user
                AF_Object.env = group
                AF_Object.group_id = group._id
            if AF_Object.group_id != group._id or AF_Object.author_id != user._id:
                return [1, '您不能操作该文章！']

    if src_type == 'reference':
        # update reference source
        ref_lib = AF_Object.reference_lib
        old_ref =  ref_lib.get_obj(alias)
        if old_ref is None:
            return [1, '该资源不存在！']
        old_ref.set_propertys(**{'url':source, 'name':title, 'body':body})
        ref_lib.add_obj(old_ref)
        return [0, '']
    elif src_type == 'code':
        # update code source 
        code_lib = AF_Object.langcode_lib
        old_code = code_lib.get_obj(alias)
        if old_code is None:
            return [1, '该资源不存在！']
        old_code.set_propertys(**{'name':title, 'code':body, 'lang':code_type})
        code_lib.add_obj(old_code)
        return [0, '']
    elif src_type == 'math':
        # update math source 
        math_lib = AF_Object.equation_lib
        old_math = math_lib.get_obj(alias)
        if old_math is None:
            return [1, '该资源不存在！']
        
        old_math.set_propertys(**{'name':title, 'equation':body, 'mode':math_type})
        math_lib.add_obj(old_math)
        return [0, '']
    elif src_type == 'table':
        # update table source 
        table_lib = AF_Object.tableform_lib
        old_table = table_lib.get_obj(alias)
        if old_table is None:
            return [1, '该资源不存在！']
        old_table.set_propertys(**{'name':title, 'tableform':body})
        table_lib.add_obj(old_table)
        return [0, '']
    elif src_type == "image":
        # update image source 
        img_lib = AF_Object.picture_lib
        old_img = img_lib.get_obj(alias)
        if old_img is None:
            return [1, '该资源不存在！']
        old_img.name = title
        img_lib.add_obj(old_img)
        return [0, '']


def fun_article_delete_src(user, article_id=0, article_type='blog', src_type='code', alias=0, group_id='-1'):

    if article_type not in Article_Type:
        return [1, '不支持当前文章类型！']
    if src_type not in Agree_Src:
        return [1, '不支持当前类型的资源！']
        
    if article_type == "about":
        AF_Object = About(_id=user.about._id)
    elif article_type == "book-about":
        try:
            book = Catalog(_id=group_id)
            AF_Object = book.about
            limit = book.authority_verify(user)
            if test_auth(limit, A_WRITE) is False:
                return [1, '您无权删除！']
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % group_id)
            return [1, '未找到该知识谱！']
    elif article_type == "blog":
        try:
            AF_Object = Blog(_id=article_id)
            if str(AF_Object.author_id) != str(user._id):
                return [1, '无权限操作他人的文章！']
        except Exception, e:
            return [1,'该文章不存在！请您检查参数！']           
    elif article_type in Group_Article:
        # for group
        try:
            group = BasicGroup(_id=group_id)
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('group not exist, id %s' % group_id)
            return [1, '小组不存在！']
            
        class_map = { 'group-info': About, 'group-doc': Blog, 'group-feedback': Feedback, 
            'group-notice': Bulletin, 'group-topic': Topic}
        user_role = group.get_member_type(user)
        if user_role is None:
            return [1, '您不是该小组成员！']
        if article_type in ['group-info', 'group-doc', 'group-notice']:
            if user_role != 'Manager':
                return [1, '您不是管理员，无权操作！']
        
        if article_type == "group-info":
            AF_Object = group.about
        else:
            try:
                AF_Object = class_map[article_type](_id=article_id)
            except Exception:
                AF_Object = class_map[article_type]()
                AF_Object.author = user
                AF_Object.env = group
                AF_Object.group_id = group._id
            if AF_Object.group_id != group._id or AF_Object.author_id != user._id:
                return [1, '您不能操作该文章！']
    
    
    if src_type == 'reference':
        AF_Object.reference_lib.remove_obj(alias)
        return [0, '']
    elif src_type == 'code':
        #print AF_Object.langcode_lib.get_obj(alias)
        AF_Object.langcode_lib.remove_obj(alias)
        return [0, '']
    elif src_type == 'math':
        #print AF_Object.equation_lib.get_obj(alias)
        AF_Object.equation_lib.remove_obj(alias)
        return [0, '']
    elif src_type == 'table':
        AF_Object.tableform_lib.remove_obj(alias)
        return [0, '']
    elif src_type == 'image':
        AF_Object.picture_lib.remove_obj(alias)
        return [0, '']
    else:
        return [1,'本站尚不支持此类型资源，我们将继续改进！']
