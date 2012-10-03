#coding=utf-8
import sys
import traceback
import logging
import time
import tempfile
import re
from datetime import datetime
import urlparse

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
from authority import *
from relation.relation import Relation
from generator import generate


from af_front.af_base.AF_Base import *

from af_front.af_base.AF_Tool import *
from af_front.af_user.AF_UserTool import *
from af_front.af_user.AF_GroupTool import *


def fun_new_book(user=None, name='', summary=''):
    if user is None:
        return [1, '请您先登陆！']
    book = Catalog()
    book.owner = user
    book.name = name
    book.about.body = summary
    book_add_manager(book, user)
    
    return [0 ,str(book._id)]
    

def fun_add_node(user=None, book=None, section='', title=''):
    if section is None:
        return [1, '请填写章节！']
    if re.search(r'^\d+(\.\d+)*$', section) is None:
        return [1, '章节填写错误！请填写数字/点，如1，又如1.2']
    if title is None:
        return [1, '标题不能为空！']
    if user is None or book is None:
        return [1, '参数错误！']
    limit = book.authority_verify(user)
    if test_auth(limit, A_WRITE) is False:
        return [1, '您无权添加新目录！']
    
    node_id = book.add_node(title, section)
    return [0, str(node_id)]
    
    
def fun_update_node(user=None, book=None, node_id='0', section='', title=''):
    if section is None:
        return [1, '请填写章节！']
    if re.search(r'^\d+(\.\d+)*$', section) is None:
        return [1, '章节填写错误！请填写数字/点，如1，又如1.2']
    if title is None or node_id is None:
        return [1, '标题不能为空！']
    if user is None or book is None:
        return [1, '参数错误！']
    limit = book.authority_verify(user)
    if test_auth(limit, A_WRITE) is False:
        return [1, '您无权添加新目录！']
    
    tmp_node = book.get_node_dict(node_id)
    if tmp_node is None:
        return [1, '该目录尚不存在！']
    tmp_node['title'] = title
    tmp_node['section'] = section
    #print tmp_node['title']
    return [0, '']
        

def fun_del_node(user=None, book=None, node_id='0'):
    if user is None or book is None or node_id is None:
        return [1, '参数错误！']
    limit = book.authority_verify(user)
    if test_auth(limit, A_DEL) is False:
        return [1, '您无权删除目录！']
    #print 'del node_id', node_id
    book.remove_node(node_id)
    return [0, '删除成功！']

    
def fun_recommend_to_book(user=None, article_id='-1', article_type='blog', section_url=''):
    # in the blog page, and user want to recommend to the book, need the book catalog url
    if user is None or article_id == '-1' or section_url == '':
        return [1, '参数错误！']
    url_tmp = urlparse.urlparse(section_url)
    url_tmp_info = url_tmp.path.split('/')
    if len(url_tmp_info) < 5 or url_tmp_info[1] != 'book' or url_tmp_info[3] != 'catalog':
        return [1, '链接错误！']
    book_id = url_tmp_info[2]
    node_id = url_tmp_info[4]
    try:
        book = Catalog(_id=book_id)
    except Exception, err:
        logging.error(traceback.format_exc())
        logging.error('Catalog not exist, id %s' % book_id)
        return [1, '未找到该知识谱！']
    if article_type == "blog":
        try:
            AF_Object = Blog(_id=article_id)
            if not AF_Object.is_posted:
                return [1, '该文章未发布！']
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('%s not exist, id %s' % (article_type, article_id) )
            return [1, '未找到该文章！']
    else:
        return [1, '暂时不支持！']
    AF_Object.add_to_catalog(book, node_id)
    #book.recommend_blog_to(url_query["id"], AF_Object)
    restr = '成功添加到知识谱<a href="/book/%s" target="_blank">《%s》</a>的章节中！' % (book_id, book.name)
    return [0, restr]

def fun_recommended_to_book(user=None, book_id='', node_id='', article_url=''):    
    if user is None or book_id == '' or node_id=='':
        return [1, '参数错误！']
    if article_url == "":
        return [1, '请填写链接！']
    try:
        book = Catalog(_id=book_id)
    except Exception, err:
        logging.error(traceback.format_exc())
        logging.error('Catalog not exist, id %s' % book_id)
        return [1, '未找到知识谱！']
    tmp_url = urlparse.urlparse(article_url)
    tmp_url_info = tmp_url.path.split('/')
    #tmp_url_info['', 'book', 'xxx']
    if len(tmp_url_info) < 3:
        return [1, '链接错误，无法解析！']
    
    target_id = tmp_url_info[2]
    if tmp_url_info[1] == 'blog':
        try:
            AF_Object = Blog(_id=target_id)
            if not AF_Object.is_posted:
                return [1, '文章未发布！']
            AF_Object.add_to_catalog(book, node_id)
            restr = '成功将文章 <a href="/blog/%s" target="_blank">%s</a> 添加到该知识谱中！' % ( AF_Object._id, AF_Object.name)
            return [0, restr]
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Blog not exist, id %s' % target_id)
            return [1, '未找到文章！']
    elif tmp_url_info[1] == 'book':
        try:
            AF_Object = Catalog(_id=target_id)
            AF_Object.add_to_catalog(book, node_id)
            return [0, '知识谱添加成功！']
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Catalog not exist, id %s' % target_id)
            return [1, '未找到推荐的知识谱！']
    else:
        return [1, '完善中！']
        
    
    
    
def fun_del_recommend(user=None, book_id='', node_id='', relation_id='', want='del_recommend'):
    if user is None:
        return [1, '请登陆！']
    if book_id == '' or node_id == '' or relation_id == '':
        return [1, '参数错误！']
    try:
        relation_obj = Relation(_id=relation_id)
        tmp_info = relation_obj.relation_set
        tmp_info_catalog = tmp_info[0]
        tmp_info_article = tmp_info[1]
        catalog_obj = generate(tmp_info_catalog[1], tmp_info_catalog[0])
        article_obj = generate(tmp_info_article[1], tmp_info_article[0])
        limit = catalog_obj.authority_verify(user)
        if want == 'del_recommend':
            if test_auth(limit, A_DEL) is False:
                return [1, '您无权操作！']
            article_type = article_obj.__class__.__name__
            if article_type == 'Blog':
                article_obj.remove_from_catalog(catalog_obj, node_id, relation_obj)
            elif article_type == "Catalog":
                article_obj.remove_subcatalog(node_id, relation_obj)
            else:
                return [1, '尚不支持类型的该操作！']
            return [0, '删除成功！']
        elif want == "mark_recommend":
            if test_auth(limit, A_MANAGE) is False:
                return [1, '您无权设置！']
            catalog_obj.spec_blog_to(node_id, relation_obj)
            return [0, '设置成功！']
        else:
            return [1, '不支持当前操作！']
    except Exception, err:
        logging.error(traceback.format_exc())
        logging.error('Del relation, id %s' % relation_id)
        return [1, '操作出错！']

       

def fun_get_node_info(user=None, book=None, node_id='0'):
    res_dict = {'book_id': book._id, 'book_name': book.name,
            'node_id': node_id, 'node_title':'', 'node_section':'', 
            'node_main':{}, 'node_articles':[], 'node_catalogs':[], 
            'node_main_script':[], 'node_article_count':0, 'node_subcatalog_count':0,
            'node_spec_count':0}
    if book is None:
        raise Exception
    node_info = book.get_node_dict(node_id)
    
    #print node_info.load_all()
    if node_info.load_all() == {}:
        raise Exception
    res_dict['node_title'] = node_info['title']
    res_dict['node_section'] = node_info['section']
    res_dict['node_article_count'] = node_info['article_count']
    res_dict['node_subcatalog_count'] = node_info['subcatalog_count']
    res_dict['node_spec_count'] = node_info['spec_count']

    main_article = book.get_node_list(node_id, 'main').load_all()
    all_article = book.get_node_list(node_id, 'articles').load_all()
    #print 'all article relation ', all_article
    all_catalog = book.get_node_list(node_id, 'catalogs').load_all()
    if len(main_article) != 0:
        # get main article, we need get releation, and
        try: 
            main_relation = Relation(_id=main_article[-1])
        except Exception, err:
            logging.error(traceback.format_exc())
            logging.error('Relation not exist, %s' % main_article[-1])
        else:
            tmp_obj_and_type = main_relation.relation_set[1]
            AF_Object = generate(tmp_obj_and_type[1], tmp_obj_and_type[0])
            if AF_Object is not None:
                tmp_main_article = { 'article_type': AF_Object.__class__.__name__, 'article_id': AF_Object._id,
                                'article_view_body': AF_Object.view_body, 'article_author_id': AF_Object.author_id,
                                'article_author_name': AF_Object.author_name, 'article_group_id':AF_Object.group_id,
                                'article_father_id':AF_Object.father_id, 'article_father_type': AF_Object.father_type,
                                'article_release_time': AF_Object.release_time, 'article_title': AF_Object.name,
                                'article_relation_id': main_relation._id }
                res_dict['node_main'] = [tmp_main_article]
                res_dict['node_main_script'] = fun_load_code_js(tmp_main_article['article_view_body'])
                #print '*'*10, res_dict['node_main_script']

    # get the recommend article
    recommend_list = fun_get_node_recommend_article(user=user, book=book, node_id=node_id, page=1, page_cap=20)
    res_dict['node_articles'] = recommend_list
    #print recommend_list
    # get the recommend catalog
            
    res_dict['node_catalogs'] = fun_get_node_recommend_article(user=user, book=book, node_id=node_id, page_cap=20, want="catalogs")
    #print 'main article', main_article
    #for item in main_article:
    #    print item
    #print 'all article', all_article
    #print 'all catalog', all_catalog
    return res_dict

def fun_get_node_recommend_article(user=None, book=None, node_id='', page=1, page_cap=10, want='articles'):
    if book is None or node_id == '' or want not in ['articles', 'catalogs']:
        raise Exception
    if want == 'articles':
        all_relation_id = book.get_node_list(node_id, 'articles').load_all()
    else:
        all_relation_id = book.get_node_list(node_id, 'catalogs').load_all()
        
    min_index, max_index = get_index_list_by_page(all_relation_id, page=page, page_cap=page_cap)
    load_relation_instance = Relation.get_instances('_id', all_relation_id[min_index:max_index])
    load_relation_dict = dict()
    '''
        load_relation_dict = { 'Blog': { 'article_id' : 'releation_id' } }    
    '''
    for item in  load_relation_instance:
        tmp_info = item.relation_set
        tmp_info_catalog = tmp_info[0]
        tmp_info_article = tmp_info[1]
        # tmp_info_article = ['aritcle_id', 'article_type']
        #print tmp_info
        if tmp_info_article[1] in load_relation_dict:
            load_relation_dict[tmp_info_article[1]][str(tmp_info_article[0])] = item._id
        else:
            load_relation_dict[tmp_info_article[1]] = { str((tmp_info_article[0])): item._id}
    # load the all
    res_list = []
    
    for i_key, i_list in load_relation_dict.items():
        tmp_instance = generate(i_key, *tuple(i_list.keys()))
        if type(tmp_instance) != list:
            item = tmp_instance
            if want == 'articles':
                res_list.append({'article_type':i_key, 'article_id': item._id, 'aritcle_author_id': item.author_id,
                    'article_author_name': item.author_name, 'article_group_id': item.group_id, 
                    'article_father_id': item.father_id, 'article_father_type': item.father_type, 
                    'article_title': item.name, 'article_view_body': item.view_body, 
                    'article_release_time': item.release_time, 'article_relation_id': i_list[str(item._id)]})
            else:
                res_list.append({'book_id':item._id, 'book_relation_id':i_list[str(item._id)],
                    'book_name': item.name})
        else:
            for item in tmp_instance:
                if want == 'articles':
                    res_list.append({'article_type':i_key, 'article_id': item._id, 'aritcle_author_id': item.author_id,
                        'article_author_name': item.author_name, 'article_group_id': item.group_id, 
                        'article_father_id': item.father_id, 'article_father_type': item.father_type, 
                        'article_title': item.name, 'article_view_body': item.view_body, 
                        'article_release_time': item.release_time, 'article_relation_id': i_list[str(item._id)]})
                else:
                    res_list.append({'book_id':item._id, 'book_relation_id':i_list[str(item._id)],
                        'book_name': item.name})
                    
    return res_list


     

def create_book_catalog_html(node_list, edit=False, book_id=''):
    if len(node_list) < 1:
        return '<ul class="catalog_ul" book_id="'+ str(book_id) +'"></ul>'
    if not edit:
        restr_list = ['<ul class="catalog_ul" book_id="'+ str(book_id) +'">']
    else:
        restr_list = ['<ul class="catalog_ul catalog_edit1" book_id="'+ str(book_id) +'">']
    nest = 1
    normal_li = '<li node_id="%s"><span class="num">%s</span><span><a href="/book/%s/catalog/%s">%s</a></span>%s%s</li>'
    complete_point = '<span class="complete%s">%s/%s/%s&nbsp;%s</span>'
    
    edit_li = '<span class="catalog_edit">修改</span><span class="catalog_del">删除</span></li>'
    for item in node_list:
        tmp_nest = len(item['node_section'].split('.'))
        complete_str = complete_point % (int(item['node_spec_count'] > 0), item['node_spec_count'], 
                    item['node_article_count'], item['node_subcatalog_count'], ('&radic;' if item['node_spec_count'] > 0 else '&times;')) 
        if tmp_nest > nest:
            nest += 1
            restr_list.append('<ul class="margin">')
            if not edit:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], complete_str, '') )
            else:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], '', edit_li) )
        elif tmp_nest == nest:
            if not edit:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], complete_str, '') )
            else:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], '', edit_li) )
        else:
            #nest -= 1
            for i in range(nest - tmp_nest):
                restr_list.append('</ul>')
            nest = tmp_nest
            if not edit:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], complete_str, '') )
            else:
                restr_list.append( normal_li % (item['node_id'], item['node_section'], 
                    str(book_id), item['node_id'], item['node_title'], '', edit_li) )
    restr_list.append('</ul>')
    if nest != 1:
        for item in range(nest -1):
            restr_list.append('</ul>')
    return ''.join(restr_list)
    
    
def book_add_manager(book=None, user=None):
    if user._id in book.managers:
        return None
    managers = book.managers
    managers.append(user._id)
    book.managers = managers
    user.managed_catalog_lib[str(book._id)] = datetime.now();
    return True
    
    

def fun_get_all_book(user, page=1, page_cap=8):
    book_instance = Catalog.get_instances()
    sum_count = len(book_instance)
    min_index, max_index = get_index_list_by_page(book_instance, page=page, page_cap=page_cap)
    
    res_list = []
    for item in book_instance[min_index:max_index]:
        tmp_owner = item.owner
        if item.node_sum == 0:
            complete = 0
        else:
            complete = str(int(100*(float(item.complete_count)/item.node_sum))) 
        res_list.append({'book_id': item._id, 'book_name': item.name, 'book_owner_name': tmp_owner.name,
            'book_owner_id': tmp_owner._id, 'book_complete': complete, 'book_complete_count': item.complete_count, 
            'book_node_sum': item.node_sum})
    return sum_count, res_list
   
def fun_get_user_book(user, page=1, page_cap=8):
    book_dict = user.managed_catalog_lib.load_all()
    #print book_dict
    total_num = len(book_dict)
    if total_num == 0:
        return 0, list()
    book_list = book_dict.keys()
    book_list.sort()
    book_list.reverse()
    min_index, max_index = get_index_list_by_page(book_list, page=page, page_cap=page_cap)

    book_instance = Catalog.get_instances('_id', book_list[min_index: max_index])
    
    res_list = []
    for item in book_instance:
        if item.node_sum == 0:
            complete = 0
        else:
            complete = str(int(100*(float(item.complete_count)/item.node_sum))) 
        res_list.append({'book_id': item._id, 'book_name': item.name, 'book_owner_name': user.name,
            'book_owner_id': user._id, 'book_complete': complete, 'book_complete_count': item.complete_count, 
            'book_node_sum': item.node_sum })
    #print res_list
    res_list.reverse()
    return total_num, res_list
    




