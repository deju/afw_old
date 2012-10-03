#coding=utf-8

import re
import time
import datetime
from bson import *
import logging
import sys
import traceback

from user import User
from article.blog import Blog
from article.comment import Comment
from article.bulletin import Bulletin
from article.feedback import Feedback
from article.status import Status
from dbase.basedata import convert_id
from generator import get_log_info
from group.basicgroup import BasicGroup
from authority import *
from article.topic import Topic
from article.about import About
from catalog import Catalog

from resys.recommender import *


from af_front.af_base.AF_Tool import *
import afwconfig as AFWConfig




def fun_update_article(user, group=None, group_id='-1', article_id = 0, article_type='blog', title='', summary='', body='',
                     permission='public', keys=[], classes=[], father_id='-1', father_type='blog', do="post", ref_comments='',
                     isedit='false'):

    if keys != []:
        keys = keys_to_list(keys)
    
        
    if article_type == "blog":
        # write blog start 
        
        try:
            AF_Object = Blog(_id=article_id)
            if str(AF_Object.author_id) != str(user._id):
                return [1, '无权限操作他人的文章！']
        except Exception, e:
            AF_Object = Blog()
            AF_Object.author = user
            AF_Object.env = user
            article_id = AF_Object._id
            
            (user.drafts_lib).add_obj(AF_Object)
        return fun_update_blog(user=user, blog=AF_Object, title=title, summary=summary, 
            body=body, keys=keys, permission=permission, classes=classes, do=do)
            
        # write blog end 
    elif article_type == "about":
        # write user about start
        AF_Object = user.about
        AF_Object.body = body
        AF_Object.env = user
        return [0, '']
        # write user about end 
    elif article_type == "book-about":
        try:
            book = Catalog(_id=group_id)
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % group_id)
        else:
            limit = book.authority_verify(user)
            if test_auth(limit, A_WRITE) is False:
                return [1, '您无权修改摘要！']
            book.about.body = body
            book.about.env = book
            return [0, '摘要更新成功！']
        
    elif article_type == "comment":
        # write comment, maybe blog comment, topic reply, and so on
        return fun_update_comment(user=user, article_id=article_id, group_id=group_id, father_id=father_id, 
            father_type=father_type, ref_comments=ref_comments, article_type=article_type, body=body)
        # write comment end
    else:
        # for group
        return fun_update_group_article(user=user, group_id=group_id, article_id=article_id, article_type=article_type,
            title=title, body=body, classes=classes, do=do) 
        


def fun_update_blog(user=None, blog=None, title='', summary='', body='', keys=[], permission='public', classes=[], do='post'):
    if type(keys) != list:
        keys = keys_to_list(keys)
    AF_Object = blog
    temp_tag = AF_Object.tag
    remove_tag_list = list( set(temp_tag) - set(classes) )
    add_tag_list = list( set(classes) - set(temp_tag) ) 
    
    blog.set_propertys(**{'name':title, 'abstract':summary,'body':body, "keywords":keys, 'privilege': permission})
                         
    if not AF_Object.is_posted:
        # not post
        for iii in remove_tag_list:
            if iii != 'default':
                AF_Object.remove_from_tag(iii)
        for iii in add_tag_list:
            AF_Object.add_to_tag( iii )
        if do == "post":
            user.post_blog(AF_Object)  
            AFW_Group = BasicGroup(_id=AFWConfig.afewords_group_id)
            AFW_Group.recommended_list.push(AF_Object._id)
        return [0, str(AF_Object._id)]
    else:
        # have post the blog
        for iii in remove_tag_list:
            if iii != 'default':
                user.remove_from_tag(AF_Object, iii)
        for iii in add_tag_list:
            user.add_to_tag(AF_Object, iii)
            
        return [0, str(AF_Object._id)]


def fun_update_group_article(user=None, group_id='-1', article_id = '-1', article_type='blog', title='', summary='', body='',
                     permission='public', keys=[], classes=[], father_id='-1', father_type='blog', do="post"):

    try:
        group = BasicGroup(_id=group_id)
        limit = group.authority_verify(user)
        #print 'User limit ', limit
    except Exception, e:
        logging.error(traceback.format_exc())
        logging.error('Group not exist %s' % group_id)
        return [1, '小组不存在！']
        
    class_map = {'group-doc':Blog, 'group-notice': Bulletin, 'group-topic': Topic, 
        'group-feedback': Feedback, 'group-info': About}    
    
    # group is exist 
    user_role = group.get_member_type(user)
    isnew = False
    if user_role is None:
        return [1, '您不是该小组成员！']    
    else:
        if article_type in ['group-doc', 'group-notice', 'group-info'] and user_role != 'Manager':
            return [1, '您不是该组的管理员，无法操作此类型的文章！']
    if article_type == 'group-info':
        group.about.body = body
        return [0, str(group.about._id)]
    # for other
    if article_id == '-1' or article_id == '0' or article_id == 0:
        AF_Object = class_map[article_type]()
        AF_Object.author = user
        AF_Object.env = group
        AF_Object.group_id = group._id
        isnew = True
        if article_type in ['group-doc', 'group-notice']:
            group.drafts_lib.add_obj(AF_Object)
        else:
            user.drafts_lib.add_obj(AF_Object)   
    else:
        try:
            AF_Object = class_map[article_type](_id=article_id)      
        except Exception:
            logging.error(traceback.format_exc())
            return [1, '该文章不存在！']
    if AF_Object.author_id != user._id or AF_Object.group_id != group._id:
        return [1, '您无权操作他人的文章！']

    AF_Object.set_propertys(**{'name': title, 'body':body })

    if article_type == 'group-doc':
        temp_tag = AF_Object.tag
        remove_tag_list = list( set(temp_tag) - set(classes) )
        add_tag_list = list( set(classes) - set(temp_tag) )
                  
    if do == "post":
        if AF_Object.is_posted is not True:
            ''' no post '''
            if article_type == 'group-topic':
                user.post_topic(AF_Object, group)
            elif article_type == 'group-feedback':
                user.post_feedback(AF_Object, group)
            elif article_type == 'group-notice':
                group.post_bulletin(AF_Object)
            elif article_type == 'group-doc':
                for iii in remove_tag_list:
                    if iii != 'default':
                        AF_Object.remove_from_tag(iii)
                for iii in add_tag_list:
                    AF_Object.add_to_tag( iii )
                group.post_blog(AF_Object)  
                print 'add tag', add_tag_list
                print 'remove tag', remove_tag_list 
        else:
            ''' have post '''
            if article_type == 'group-doc':
                print 'add tag', add_tag_list
                print 'remove tag', remove_tag_list 
                for iii in remove_tag_list:
                    if iii != 'default':
                        group.remove_from_tag(AF_Object, iii)
                for iii in add_tag_list:
                    group.add_to_tag(AF_Object, iii)
            
    return [0, str(AF_Object._id)]
                
    


def fun_update_comment(user, group_id='-1', article_id = 0, article_type='blog', title='', summary='', body='',
                     permission='public', keys=[], classes=[], father_id='-1', father_type='blog', do="post", ref_comments=''):
    # update comment, all comments 
    group = None
    if father_type == 'blog':
        try:
            AF_Object = Blog(_id=father_id)
        except Exception, e:
            return [1, '文章不存在！']
    else:
        # for group 
        if father_type == 'group-notice':
            try:
                AF_Object = Bulletin(_id=father_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) is None:
                    return [1, '您不是该小组成员']
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('%s not exist, id %s' %(father_type, father_id))
                return [1, '该公告不存在！']
        elif father_type == "group-doc":
            try:
                AF_Object = Blog(_id=father_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) is None:
                    return [1, '您不是该小组成员']
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('%s not exist, id %s' %(father_type, father_id))
                return [1, '该文档不存在！']
        elif father_type == "group-topic":
            try:
                AF_Object = Topic(_id=father_id)
                group = BasicGroup(_id=AF_Object.group_id)
                if group.get_member_type(user) is None:
                    return [1, '您不是该小组成员']
                AF_Object.update_time = datetime.datetime.now()       
                group.topic_list.pull(AF_Object._id)
                group.topic_list.push(AF_Object._id)
            except Exception, e:
                logging.error(traceback.format_exc())
                logging.error('%s not exist, id %s' %(father_type, father_id))
                return [1, '该话题不存在！']
        elif father_type == "group-feedback":
            return [1, '不支持当前操作！']
        else:
            return [1, '完善中！']
    # create comment and save it
    ref_comments_list = str_to_int_list(ref_comments)  
    #print ref_comments_list
    AF_Comment = Comment()
    AF_Comment.author = user
    AF_Comment.set_propertys(**{'body':body, 'father':AF_Object, 'ref_comments':ref_comments_list})
    
    if father_type != 'blog':
        AF_Comment.set_propertys(**{'group_id': AF_Object.group_id})
    # post to the AF_Object
    AF_Object.comment_list.push(AF_Comment._id)
    # post notification
    
    to_blog_author_mes = format_notification(note_from=user, note_to_what=AF_Object, 
                                    note_from_what=AF_Comment, father_type=father_type, group=group)
    to_comment_author_mes = format_notification(note_from=user, note_to_what=AF_Object, 
                                    note_from_what=AF_Comment,do="reply_comment", father_type=father_type, group=group)
                                    
    ''' first post to the object[blog] author, tell him his blog hava comments  '''
    AF_Author = user
    if str(AF_Object.author_id) != str(user._id):
        ''' the author is not myself '''
        try:
            AF_Author = User(_id=AF_Object.author_id)
        except Exception, e:
            logging.error(traceback.format_exc())
            return [1, '作者已经注销！']

    #AF_Author.notification_list.push(to_blog_author_mes)
    #print 'reply_blog', AF_Author , ' noti'
    ''' second post to the ref_comment author , tell them his commented was replyed '''
    #post_list.append(AF_Object.)
    all_comment_list = AF_Object.comment_list.load_all()
    all_comment_length = len(all_comment_list)
    ref_comment_id_list = []
    post_list = []
    
    reply_to_blog_author_comment = False
    
    for ref_index in ref_comments_list:
        if ref_index-1 > all_comment_length:
            continue
        ref_comment_id_list.append(all_comment_list[ref_index])
    
    # load all ref_comments
    Comment_all_instance = Comment.get_instances('_id', ref_comment_id_list)
    for one_instance in Comment_all_instance:
        if one_instance.author_id == user._id:
            ''' my self '''
            continue
        try:
            AF_Comment_Author = User(_id=one_instance.author_id)
        except Exception, e:
            logging.error(traceback.format_exc())
            logging.error('User not exist, id is %s' % str(one_instance.author_id))
            continue
        else:
            if AF_Comment_Author._id == AF_Author._id:
                reply_to_blog_author_comment = True
                #AF_Author.notification_list.push(to_comment_author_mes)
                continue
            AF_Comment_Author.notification_list.push(to_comment_author_mes)
            #print 'reply_comment', AF_Comment_Author , ' noti'
    if AF_Author._id != user._id:
        if reply_to_blog_author_comment != True:
            AF_Author.notification_list.push(to_blog_author_mes)
        else:
            AF_Author.notification_list.push(to_comment_author_mes)
        
    return [0, '']


def fun_get_comment_by_position(article_id=None, pos=0, article_type="blog", page_cap=10, load_one='no', 
    load_before='no',before_pos=0):
    ''' get comment by position, return [1|0, 'info', first_post, last_pos, len] '''
    ''' info contains a dict{ 'comment':{'0': comment(0) }, 'ref_commet':{'1':comment(0) } } '''
    try: 
        if article_type == "blog":
            AF_Object = Blog(_id=article_id)
        elif article_type == "group-topic":
            AF_Object = Topic(_id=article_id)
        elif article_type == 'group-notice':
            AF_Object = Bulletin(_id=article_id)
        elif article_type == 'group-feedback':
            AF_Object = Feedback(_id=article_id)
        elif article_type == "group-doc":
            AF_Object = Blog(_id=article_id)
        else:
            return [1, '不支持当前类型！']
    except Exception ,e:
        logging.error(traceback.format_exc())
        logging.error('%s not exist, id %s' % (article_type, article_id) )
        return [1, '文章不存在!']
    else:
        comment_list = AF_Object.comment_list.load_all()
    #print comment_list
    all_length = len(comment_list)
    load_one_index = -1
    
    if load_one != "yes":
        # not load one comment, load all comments by page
        if pos < 0:
            pos = 0
        if load_before != 'yes':
            last_pos = pos+page_cap
            load_list = comment_list[pos:last_pos]
        else:
            load_list = comment_list[pos:before_pos]
            last_pos = before_pos
    else:
        try:
            objid_pos = ObjectId(pos)
            if objid_pos in comment_list:
                load_list = []
                load_list.append(objid_pos)
                load_one_index = comment_list.index(objid_pos)
        except Exception, e:
            logging.error('Wrong comment id %s in blog %s ' %( pos ,article_id))
            load_list = []
    #print 'load_list first ', load_list
    res_load_list = []
    Comment_instance = Comment.get_instances('_id', load_list)
    
    ret_comment_dict = {}
    ref_comment_list = []
    ret_ref_comment_dict = {}
    for tmp_one in Comment_instance:
        ''' comment list '''
        tmp_index = comment_list.index(tmp_one._id)
        if type(tmp_one.ref_comments) == list:
            ref_comment_list.extend(tmp_one.ref_comments)
        try:
            tmp_user = User(_id=(tmp_one.author_id))
            tmp_avatar = tmp_user.avatar.thumb_name
                #print tmp_avatar
        except Exception, e:
            ret_comment_dict[tmp_index] = {'author_id':'anonymous', 'author_avatar':'/static/img/afewords-user.jpg', 
                        'comment_body':tmp_one.view_body, 'author_name':'该用户已经注销', 'ref_comments': tmp_one.ref_comments,
                        'comment_id': str(tmp_one._id), 'comment_time':str(tmp_one.release_time)[0:19] }
            log_error('User not found, his ID is :' + tmp_one.author_id, **{})
            continue
        else:
            ret_comment_dict[tmp_index] = {'author_id':str(tmp_one.author_id), 'author_avatar':tmp_avatar, 
                        'comment_body':tmp_one.view_body, 'author_name':tmp_user.name, 'ref_comments': tmp_one.ref_comments,
                        'comment_id': str(tmp_one._id), 'comment_time':str(tmp_one.release_time)[0:19] }

    # delete the same index
    ref_comment_list = list( set( ref_comment_list ) )
    ref_comment_id_list = []
    for iii in ref_comment_list:
        try:
            if comment_list[iii] not in load_list:
                ref_comment_id_list.append(comment_list[iii])
        except Exception, e:
            continue
    ref_comment_instance = Comment.get_instances('_id', ref_comment_id_list)
    
    for tmp_one in ref_comment_instance:
        '''ref comments '''
        tmp_index = comment_list.index(tmp_one._id)
        try:
            tmp_user = User(_id=(tmp_one.author_id))
            tmp_avatar = tmp_user.avatar.thumb_name
        except Exception, e:
            ret_ref_comment_dict[tmp_index] = {'author_id':'anonymous', 'author_avatar':'/static/img/afewords-user.jpg', 
                        'comment_body':tmp_one.view_body, 'author_name':'该用户已经注销', 'ref_comments':tmp_one.ref_comments,
                        'comment_id': str(tmp_one._id), 'comment_time':str(tmp_one.release_time)[0:19] }
            log_error('User not found, his ID is :' + tmp_one.author_id, **{})
            continue
        else:
            ret_ref_comment_dict[tmp_index] = {'author_id':str(tmp_one.author_id), 'author_avatar':tmp_avatar, 
                        'comment_body':tmp_one.view_body, 'author_name':tmp_user.name, 'ref_comments':tmp_one.ref_comments,
                        'comment_id': str(tmp_one._id), 'comment_time':str(tmp_one.release_time)[0:19] }
    
    if load_one != "yes":
        return [0, {'comment': ret_comment_dict, 'ref_comment': ret_ref_comment_dict, 
                    'first_pos':pos,'last_pos':last_pos, 'len':all_length, 'load_before':load_before, 
                    'load_one':'no'} ]    
    else:
        return [0, {'comment': ret_comment_dict, 'ref_comment': ret_ref_comment_dict, 
                    'first_pos':load_one_index, 'last_pos':load_one_index+1, 'len': all_length, 'load_one':'yes', 
                    'load_before':'no'} ]


   
def fun_view_blog(bid):
    try:
        AF_Article = Blog(_id=bid)
    except Exception, e:
        return [1,'无此文章！', '', '', '', '']
    rrtitle, rrabstract, rrview, rrauthor, rrtime = AF_Article.get_propertys(*('name', 'abstract', 'view_body', 'author_id', 'release_time'))
    AF_User = User(_id=rrauthor)
    rrname = AF_User.name
    rravatar = (AF_User.avatar).thumb_name
    return [0, rrtitle, rrabstract, rrview, rrname, rravatar, rrtime]



def fun_get_feed_home(page):
    try:
        page = int(page)
    except Exception, e:
        return [1, False, '页数出错！']

    tmp_con = BlogPool().load_all()
    tmp_con_test = BlogPool().get_slice(-20,10)
    tmp_blog = Blog.get_instances('_id', tmp_con)
    tmp_blog_list = []
    for kkk in tmp_blog:
        tmp_user = User(_id=kkk.author_id)
        tmp_avatar = tmp_user.avatar
        tmp_blog_list.append({'blog_id':str(kkk._id), 'title':kkk.name, 'author_id':str(tmp_user._id), 'blog_body':kkk.view_body,
                            'summary':kkk.abstract, 'author_avatar': tmp_avatar.thumb_name, 'author_name':tmp_user.name})
    #print tmp_blog_list
    # 20 page one time
    return [0, False, tmp_blog_list]
    

def fun_get_recommender_list(blog_id):
    try:
        hour = time.localtime().tm_hour
        if hour > 12:
            SD_Object = SimilarityDB_A(objectid=blog_id)
        else:
            SD_Object = SimilarityDB_B(objectid=blog_id)
        #print SD_Object
        if SD_Object is None:
            return []
        relate_list = SD_Object['sim_list']
    
        relate_list_instance = Blog.get_instances('_id', relate_list[0:10])
        res_list = []
        for item in relate_list_instance:
            res_list.append({'blog_id': item._id, 'blog_title': item.name })
        
        return res_list
    except TypeError:
        return []
    except Exception:
        logging.error(traceback.format_exc())
        return []
    

