#coding=utf-8

import Image
import re

from user import User
from article.blog import Blog
from article.status import Status
from article.picture import Picture
from article.tableform import Tableform
from article.equation import Equation
from article.reference import Reference
from article.langcode import Langcode
from article.comment import Comment
from article.topic import Topic
from group.basicgroup import BasicGroup
from article.feedback import Feedback
from article.bulletin import Bulletin


import afwconfig as AFWConfig
from af_front.af_base.AF_Tool import *



def fun_group_create(user, group_name='', group_detail='', group_class=''):
    if AFWConfig.afewords_group_open is not True:
        return [1, '创建小组暂时未开放！']
    if group_name == '' or group_detail == '':
        return [1, '小组信息不完整！']
    
    new_group = BasicGroup()
    new_group.set_propertys(**{'name': group_name, 'alias': group_name})
    new_group.about.body = group_detail
    new_group.avatar.thumb_name = '/static/img/afewords-group.jpg'
    user.follow_group(new_group)
    new_group.set_manager(user)

    return [0, str(new_group._id)]
    

def fun_group_user_group(user):
    
    group_list_dict = user.follow_group_lib.load_all()
    group_list = group_list_dict.keys()
    group_topic_list = []
    
    group_instance_list = BasicGroup.get_instances('_id', group_list)
    for item in group_instance_list:
        tmp_topic_list, total_num, page = fun_get_topic_list(item, 1, 5)
            
        group_topic_list.append({'group_name': item.name, 'group_avatar': item.avatar.thumb_name, 
            'group_id': str(item._id), 'group_topic': tmp_topic_list })
    
    return group_topic_list

def fun_group_lib(user=None, page=1, page_cap=10):
    group_instance = BasicGroup.get_instances()
    
    group_lib = []
    #print type(group_instance)
    #print 'page ', page
    min_index, max_index = get_index_list_by_page(group_instance, page=page, page_cap=page_cap)
    #print 'all ', len(group_instance)
    #print 'min,max', min_index, max_index
    for item in group_instance[min_index: max_index]:
        try:
            group_lib.append({'group_id': str(item._id), 'group_name': item.name, 'group_detail': item.about.view_body,
                'group_member_count': len(item.member_lib), 'group_avatar': item.avatar.thumb_name })
        except Exception, e:
            item.remove()
            continue
            
    return group_lib, len(group_instance), page


def fun_get_member_list(group=None, page=1, page_cap=9):
    if type(page) != int:
        logging.error('page must be int type ')
        return [], 0, 1
    
    # get the member list by page 
    member_list = group.member_lib.load_all().keys()
    
    min_index, max_index = get_index_list_by_page(member_list, page=page, page_cap=page_cap)
    
    user_list = member_list[min_index:max_index]
    user_instance_list = User.get_instances('_id', user_list)
    
    res_list = []
    for item in user_instance_list:
        try:
            res_list.append({'user_id': str(item._id), 'user_name': item.name, 
                'user_domain': item.domain, 'user_avatar': item.avatar.thumb_name })
        except Exception, e:
            continue
    sum_count = len(member_list)
    return res_list, sum_count, page

def fun_get_topic_list(group=None, page=1, page_cap=10):
    if type(page) != int:
        logging.error('page must be int page ')
        return [], 0, 1
        
    topic_list = group.topic_list.load_all()
    topic_list.reverse()
    
    min_index, max_index = get_index_list_by_page(topic_list, page=page, page_cap=page_cap)
    topic_list_instance = Topic.get_instances('_id', topic_list[min_index:max_index])
    
    res_list = []
    for item in topic_list_instance:
        res_list.append({'topic_id': str(item._id), 'topic_title': item.name, 'topic_body': item.view_body,
            'topic_comment_count': len(item.comment_list), 'topic_update_time': item.update_time,
            'topic_author_id': str(item.author_id), 'topic_author_name': item.author_name})
    
    res_list.reverse()
    return res_list, len(topic_list), page
    
def fun_get_feedback_list(group=None, page=1, page_cap=10):
    
    feedback_list = group.feedback_list.load_all()
    #print feedback_list
    if feedback_list is None:
        feedback_list = []
    feedback_list.reverse()
    
    min_index, max_index = get_index_list_by_page(feedback_list, page=page, page_cap=page_cap)
    
    feedback_list_instance = Feedback.get_instances('_id', feedback_list[min_index:max_index])
    
    res_list = []
    for item in feedback_list_instance:
        res_list.append({'feedback_id': str(item._id), 'feedback_title': item.name,
            'feedback_author_id': str(item.author_id), 'feedback_author_name': item.author_name})
            
    return res_list, len(feedback_list), page
    

def fun_get_notice_list(group=None, page=1, page_cap=10):
    pass
    notice_list = group.bulletin_board.load_all()
    notice_list.reverse()
    min_index, max_index = get_index_list_by_page(notice_list, page=page, page_cap=page_cap)
    
    #print min_index, max_index
    notice_list_instance = Bulletin.get_instances('_id', notice_list[min_index:max_index])
    #print 'notice_list', notice_list 
    #print 'notice list instance ', notice_list_instance
    res_list = []
    for item in notice_list_instance:
        res_list.append({'notice_id': str(item._id), 'notice_title': item.name, 
            'notice_author_id': str(item.author_id), 'notice_author_name': item.author_name})
    
    #print 'notice result ', res_list 
    res_list.reverse()
    return res_list, len(notice_list), page    

def fun_get_doc_list(group=None, page=1, page_cap=10, tag='default'):
    if tag == "default":
        tmp_list = group.blog_list.load_all()
    else:
        tmp_list = group.tag_lib[tag]
    if tmp_list is None:
        return ([], 0, page)
    sum_count = len(tmp_list)
    #print 'total num', sum_count
    sum_page = (sum_count % page_cap and sum_count /page_cap + 1) or sum_count / page_cap
    if page > sum_page:
        return ([], 0, page)
    tmp_list.reverse()
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)
    
    #print tmp_list
    #print tmp_list[min_index:max_index]
    doc_list_instance = Blog.get_instances('_id', tmp_list[min_index:max_index])
    
    res_list = []
    
    for item in doc_list_instance:
        res_list.append({'doc_id':item._id, 'doc_title':item.name, 'doc_time':item.release_time})

    res_list.reverse()
    return (res_list, sum_count, page)
    
    
