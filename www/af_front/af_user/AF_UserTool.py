#coding=utf-8

import Image
import re
import logging
import math

from user import User
from article.blog import Blog
from article.status import Status
from article.picture import Picture
from article.tableform import Tableform
from article.equation import Equation
from article.reference import Reference
from article.langcode import Langcode
from article.comment import Comment
from group.basicgroup import BasicGroup
from dbase.basedata import convert_id

from af_front.af_base.AF_Tool import *
import afwconfig as AFWConfig

def fun_save_thumb(name, pos_x=0, pos_y=0, pos_w=150, pos_time=1, 
    normal_path = AFWConfig.afewords_image_path +"/static/avatar/normal/", 
    small_path=AFWConfig.afewords_image_path + "/static/avatar/small/"):
    ''' save thumb contains user avatar, grouop logo, default is user avatar '''
    try:
        #print 'path ', normal_path + name
        obj_img = Image.open(normal_path + name)
    except IOError, e:
        log_error('Wrong: image is' + normal_path + name)
        return [1, '操作图片出错！']
    
    img_w, img_h = obj_img.size
    try:
        left_l = int(pos_x * pos_time)  # distance of left
        upper_l = int(pos_y * pos_time)  # distance of the top
        pos_w = int(pos_w * pos_time)   # width
        #print pos_time
        
    except ValueError, e:
        #log_error('Wrong: crop image paragram wrong')
        return [1, '裁剪参数出错！']
    lower_l = upper_l + pos_w  # 
    right_l = left_l + pos_w  # 
    #print 'top, right, bottom, left, time, width', upper_l, right_l, lower_l, left_l, pos_time, img_w
    #print 'width, height ', img_w, img_h
    if lower_l > img_h or right_l > img_w or img_w < 150:
        return [1, '裁剪参数出错！']
    box = (left_l, upper_l, right_l, lower_l)
    try:
        img_tmp = obj_img.crop(box)
        img_tmp.thumbnail((200, 200))
        img_tmp.save(str(small_path + name))
    except SystemError, e:
        log_error('Wrong: crop image paragram wrong')
        return [1, '裁剪参数出错！']
    return [0, '']
    

def fun_crop_img(pos_x, pos_y, pos_w, avatar):
    base_path = './static/avatar/650/'
    small_base = './static/avatar/200/'
    #avatar = avatar[4:]
    obj_img = Image.open(base_path + avatar)
    img_w, img_h = obj_img.size
    left_l = int(pos_x)
    upper_l = int(pos_y)
    pos_w = int(pos_w)
    lower_l = upper_l + pos_w
    right_l = left_l + pos_w
    if lower_l > img_h or right_l > img_w:
        return [1,'您设置的参数有误，请确认参数！']
    box = (left_l, upper_l, right_l, lower_l)
    img_tmp = obj_img.crop(box)
    img_tmp.thumbnail((200, 200))
    img_tmp.save(str(small_base + avatar))
    return [0, '']


def fun_get_article_src(target):
    # target is blog or about 
    pic_lib_result = []
    math_lib_result = []
    code_lib_result = []
    table_lib_result = []
    ref_lib_result = []

    img_lib = target.picture_lib
    math_lib = target.equation_lib
    code_lib = target.langcode_lib
    table_lib = target.tableform_lib
    ref_lib = target.reference_lib

    pic_con = Picture.get_instances('_id', img_lib.load_all().values())
    ref_con = Reference.get_instances('_id', ref_lib.load_all().values())
    code_con = Langcode.get_instances('_id', code_lib.load_all().values())
    math_con = Equation.get_instances('_id', math_lib.load_all().values())
    table_con = Tableform.get_instances('_id', table_lib.load_all().values())

    #tmp = {'alias':}
    for iii in pic_con:
        pic_lib_result.append({'alias':iii.alias, 'name':iii.name, 'thumb_name':iii.thumb_name})
    #print pic_lib_result

    for iii in ref_con:
        ref_lib_result.append({'alias':iii.alias, 'name':iii.name, 'url':iii.url, 'body':iii.body})
    #print ref_lib_result

    for iii in code_con:
        code_lib_result.append({'alias':iii.alias, 'name':iii.name, 'lang':iii.lang, 'body':iii.code})
    #print code_lib_result

    for iii in math_con:
        math_lib_result.append({'alias':iii.alias, 'name':iii.name, 'mode':iii.mode, 'body':iii.equation})
    #print math_lib_result

    for iii in table_con:
        table_lib_result.append({'alias':iii.alias, 'name':iii.name, 'body':iii.tableform})
    #print table_lib_result

    return [pic_lib_result, ref_lib_result, code_lib_result, math_lib_result, table_lib_result]


def fun_get_blog_list_by_tag(user, tag='default', page=1, page_cap=10):
    page = int(page)
    if tag == "default":
        tmp_list = user.blog_list.load_all()
    else:
        tmp_list = user.tag_lib[tag]
    if tmp_list is None:
        return ([], 0)
    sum_count = len(tmp_list)
    #print 'total num', sum_count
    sum_page = (sum_count % page_cap and sum_count /page_cap + 1) or sum_count / page_cap
    if page > sum_page:
        return ([], 0)
    tmp_list.reverse()
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)
    
    #print tmp_list
    #print tmp_list[min_index:max_index]
    blog_con = Blog.get_instances('_id', tmp_list[min_index:max_index])
    
    tmp_con = []
    
    for iii in blog_con:
        tmp_con.append({'id':iii._id, 'title':iii.name, 'time':iii.release_time, 
            'summary':iii.abstract, 'view_body':strip_tags(iii.view_body) + '<a target="_blank" class="blog_detail" href="/blog/'+ str(iii._id) +'">...</a>'})

    tmp_con.reverse()
    return (tmp_con, sum_count)

    

def fun_set_notice_flag(user=None, do='read', index=-1, is_all='no'):
    if is_all == 'yes':
        all_list = user.notification_list.load_all()
        if do == "read":
            for ii in range(len(all_list)):
                if all_list[ii] is None:
                    continue
                all_list[ii][1] = True
                user.notification_list[ii] = all_list[ii]
            return [0, '']
        elif do == "delete":
            for ii in range(len(all_list)):
                if all_list[ii] is None:
                    continue
                del user.notification_list[ii]
            return [0, '']
        else:
            return [1, '不支持此操作！']
    else:
        # for only one notificaton
        if do == "read":
            try:
                tmp_noti = user.notification_list[index]
                tmp_noti[1] = True
                user.notification_list[index] = tmp_noti
            except Exception, e:
                return [1, '参数错误！']
            else:
                return [0, '']
        elif do == "delete":
            try:
                del user.notification_list[index]
            except Exception, e:
                return [1, '参数出错！']
            else:
                return [0, '']
        else:
            return [1, '不支持此种操作！']


def fun_get_notice_list(user=None, page=1, page_cap=10):
    pass
    tmp_list = user.notification_list.load_all()
    
    useful_tmp_list = []
    for ii in range(len(tmp_list)):
        if tmp_list[ii] == [] or tmp_list[ii] == None:
            continue
        useful_tmp_list.append({'index':ii, 'noti': tmp_list[ii]})

    #print useful_tmp_list    
    
    # we page the useful_tmp_list 
    sum_count = len(useful_tmp_list)
    sum_page = int( math.ceil(float(sum_count) / page_cap) )
    if page < 0 or page > sum_page:
        page = 1
        
    useful_tmp_list.reverse()
    ret_list = useful_tmp_list[(page-1)*page_cap : page*page_cap]
    
    return [ret_list, sum_count, page]
    


def fun_get_draft_list(user, page=1, page_cap=10):
    tmp_dict = user.drafts_lib.load_all()
    tmp_list = tmp_dict.keys()
    tmp_list.sort()
    tmp_list.reverse()
    
    #print tmp_list
    sum_count = len(tmp_list)

    sum_page = (sum_count % page_cap and sum_count /page_cap + 1) or sum_count / page_cap
    if page > sum_page:
        return ([], 0)
    tmp_list.reverse()
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)
      
    
    tmp_draft = []
    com_draft = []
    com_list = []
    blog_draft = []
    feedback_draft = []
    topic_draft = []
    
    for iii in tmp_list[min_index:max_index]:
        #print 'draft type ', tmp_dict[iii][0]
        if tmp_dict[iii][0] == 'Blog':
            blog_draft.append({'type': tmp_dict[iii][0], 'id':iii, 'time':tmp_dict[iii][1]})
        elif tmp_dict[iii][0] == 'Comment':
            com_list.append(iii) 
        else:
            tmp_draft.append({'type': tmp_dict[iii][0], 'id':iii, 'time':tmp_dict[iii][1]}) 

    com_con = Comment.get_instances('_id', com_list)
    for kkk in com_con:
        com_draft.append({'type': 'Comment', 'id':kkk._id, 'time':kkk.update_time, 'father':kkk.father_id})
    
    tmp_draft.extend(blog_draft)
    tmp_draft.extend(com_draft)
    tmp_draft.reverse()
    return (tmp_draft, sum_count)


def fun_user_lib(user, page=1, page_cap=16):
    # get all user of the afewords 
    tmp_con = User.get_instances()
    tmp_list = []
    sum_count = 0
    
    #print len(tmp_con), [(kkk._id, kkk.name, kkk.password) for kkk in tmp_con]
    for iii in tmp_con:
        try:
            if str(user._id) != str(iii._id):
                tmp_avatar = iii.avatar
                if iii.password != '' and iii.password is not None:
                    tmp_list.append({'id':iii._id, 'thumb':tmp_avatar.thumb_name, 'name':iii.name})
                    sum_count = sum_count + 1
        except Exception, e:
            continue
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)
    
    return (tmp_list[min_index:max_index], sum_count)

    
def fun_get_follow_list(user, page=1, page_cap=16, follow="follow"):
    if follow == "follow":
        tmp_dict = user.follow_user_lib.load_all()
    else:
        tmp_dict = user.follower_user_lib.load_all()
    #print 'tmp_dict ', tmp_dict
    tmp_list = tmp_dict.keys()
    tmp_list.sort()
    
    sum_count = len(tmp_list)
    sum_page = (sum_count % page_cap and sum_count /page_cap + 1) or sum_count / page_cap
    if page > sum_page:
        return ([], 0)
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)  

    tmp_list_follow = []
    #print 'tmp_list, ', tmp_list[min_index:max_index]
    tmp_con_user = User.get_instances('_id', tmp_list[min_index:max_index])

    for kkk in tmp_con_user:
        tmp_avatar = kkk.avatar
        tmp_list_follow.append({'id':kkk._id, 'thumb':tmp_avatar.thumb_name, 'name':kkk.name})

    #print 'follow list ', tmp_list_follow
    return (tmp_list_follow, sum_count)


    
def fun_get_like_list(user, page=1, page_cap=10):
    tmp_dict = user.favorite_lib.load_all()
    tmp_list = tmp_dict.keys()
    tmp_list.sort()
    tmp_list.reverse()

    sum_count = len(tmp_list)

    sum_page = (sum_count % page_cap and sum_count /page_cap + 1) or sum_count / page_cap
    if page > sum_page:
        return ([], 0)
    min_index, max_index = get_index_list_by_page(tmp_list, page=page, page_cap=page_cap)   
    

    tmp_con_blog = Blog.get_instances('_id', tmp_list[min_index:max_index])
    like_list = []
    for kkk in tmp_con_blog:
        like_list.append({'id':kkk._id, 'title':kkk.name})

    like_list.reverse()
    return (like_list, sum_count)
    

def fun_do_like(user, kind="blog", obj_id='0', want="like"):
    #print user.favorite_lib.load_all()
    try:
        #print want
        if kind == "blog":
            obj = Blog(_id=obj_id)
        else:
            return [1, '暂不支持此类型！']
    except Exception, e:
        logging.error('Blog not exist, id %s ' % str(obj_id))
        return [1, '参数错误，对象不存在！']
    else:
        if want == "like":
            #print obj, type(obj)
            user.like_post(obj)
            return [0, '']
        elif want == "unlike":
            user.dislike_post(obj)
            return [0, ''] 
        elif want == 'view':
            if user is not None and user._id == obj.author_id:
                return [1, '']
            obj.statistics.view_count = obj.statistics.view_count + 1
            return [0, '']
        else: 
            return [1, '不知道您想做什么！']


def fun_edit_password(user, old_pwd, new_pwd):
    ''' modify the password  '''
    if old_pwd is None or new_pwd is None or len(old_pwd) < 4 or len(new_pwd) < 4:
        return [1, '密码长度至少为4位！']
    tmp_old_pwd = encrypt(old_pwd)
    tmp_new_pwd = encrypt(new_pwd)

    if user.password != '' and user.password == tmp_old_pwd:
        user.password = tmp_new_pwd
        return [0, '']
    else:
        return [1, '请输入正确的原密码！']




def fun_get_feed_by_id(user=None, obj_id=0, page_cap=20):
    # find by the post id 
    
    #feed_id_list = [] #BlogPool().load_all()
    AFW_Group = BasicGroup(_id=AFWConfig.afewords_group_id)
    feed_id_list = AFW_Group.recommended_list.load_all()
    feed_id_list.reverse()
    #feed_id_list = [str(kk) for kk in feed_id_list]

    #print feed_id_list
    if obj_id == '0' or obj_id == 0:
        index = -1
    else:
        index = index_at_list(feed_id_list, convert_id(obj_id))
    if index is None:
        return [1, '操作出错！']
    
    load_list_id = feed_id_list[index+1: index+page_cap+1]
    if len(load_list_id) < page_cap:
        is_all = 'yes'
    else:
        is_all = 'no'
    #print 'index', index
    #print 'load list', load_list_id
    if load_list_id == []:
        last_id = 0
    else:
        last_id = load_list_id[len(load_list_id)-1]
    tmp_blog_con = Blog.get_instances('_id', load_list_id)

    tmp_blog_list = []
    for one_blog in tmp_blog_con:
        try:
            tmp_user = User(_id=one_blog.author_id)
        except Exception, e:
            log_error('User is not exist, User ID: ' + one_blog.author_id)
            continue
        else:
            tmp_avatar = tmp_user.avatar
            tmp_blog_list.append({'blog_id':str(one_blog._id), 'title':one_blog.name, 'author_id':str(tmp_user._id), 
                            'view_body':strip_tags(one_blog.view_body) + '<a target="_blank" class="blog_detail" href="/blog/'+ str(one_blog._id) +'">...</a>',
                            'summary':one_blog.abstract, 'author_avatar': tmp_avatar.thumb_name, 
                            'author_name':tmp_user.name})

    tmp_blog_list.reverse()
    return [0, {'feed':tmp_blog_list, 'last_id': str(last_id), 'is_all':is_all}]
        

def fun_get_feed_by_page(page):
    # find post by page
    pass

def fun_get_feed_by_page_simple(page):
    count = 10
    feed_id_list = [] #BlogPool().load_all()
    feed_id_list.reverse()

    try:
        page = int(page)
    except Exception, e:
        return [1, '页数错误！']

    page_start = page * count
    page_end = (page+1) * count

    load_list_id = feed_id_list[page_start:page_end]
    if len(load_list_id) < count:
        isall = True
    else:
        isall = False
    tmp_blog_con = Blog.get_instances('_id', load_list_id)

    tmp_blog_list = []
    for one_blog in tmp_blog_con:
        if one_blog.author_id is not None and one_blog.author_id !='':
            tmp_blog_list.append({'blog_id':str(one_blog._id), 'title':one_blog.name, 'author_id':str(one_blog.author_id), 
                            'author_name':one_blog.author_name})

    tmp_blog_list.reverse()
    return [0, tmp_blog_list, isall]