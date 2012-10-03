#coding=utf-8

import re
import hashlib
import random
import string
import Image, ImageDraw, ImageFont, random
import StringIO
import logging
import traceback
from HTMLParser import HTMLParser

from tornado.escape import url_escape
from tornado.escape import xhtml_escape

from generator import get_log_info

from af_front.af_base.AF_Mail import *


def log_error(des='error', **kw):
    logging.info('+'*30)
    logging.info('Error description : ' )
    logging.info(des)
    for oo in kw:
        logging.info(oo + kw[oo])
    logging.info('+'*30)
    
def log_warning(des='Warn', **kw):
    logging.info('+'*30)
    logging.info('Warn description : ' )
    logging.info(des)
    for oo in kw:
        logging.info(oo + kw[oo])
    logging.info('+'*30)

def log_info(des='INFO', **kw):
    logging.info('+'*30)
    logging.info('INFO description : ' )
    logging.info(des)
    for oo in kw:
        logging.info(oo + kw[oo])
    logging.info('+'*30)



def is_value(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return value
    result = re.search('\S', value)
    if result is None:
        return None
    return xhtml_escape(value)
    
def math_encode(value):
    return value.replace('<','&lt;').replace('>', '&gt;')
    
def is_email(email):
    reg = r"^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$"
    return re.match(reg, email)

def encrypt(pwd):
    ''' first use MD5, the use SHA1, result is 40 byte '''
    result = hashlib.md5(pwd).hexdigest()
    result = hashlib.sha1(result).hexdigest()
    return result
    
def random_string(num):
    ''' num is the nums of random string '''
    salt = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return salt
    
def send_mail_reg(to, token, name):   
    subject = u'子曰--验证注册'
    html = (u"<html><head></head><body>"
        u"<p>" + name + u"，欢迎您注册子曰，请您点击下面链接进行邮箱验证操作！</p>"
        u"<br>"
        u"<p><a href='http://www.afewords.com/check?email="+ url_escape(to)+ u"&token=" + token + u"'>验证链接</a></p><br>"
        u"<p>或者将链接复制至地址栏完成邮箱激活：http://www.afewords.com/check?email="+url_escape(to)+"&token=" + token + u"</p>"
        u"</body></html>")
    return send_mail(to, subject, html)

def send_mail_reset(to, token, name):
    subject = u'子曰--密码重置'
    html = (u"<html><head></head><body>"
            u"<p>" + name + u"，您对密码进行了重置，请您点击下面链接完成密码重置操作！</p><br>"
            u"<p><a href='http://www.afewords.com/check?type=reset&email=" + url_escape(to)+ u"&token="+ token +u"'>重置链接</a></p>"
            u"<p>或者将链接复制至地址栏完成密码重置：http://www.afewords.com/check?type=reset&email="+url_escape(to)+"&token=" + token + u"</p>"
            u"<body></html>")
    return send_mail(to, subject, html)


def send_mail_invite(to, name='子曰', email='', user_id = ''):
    subject = u'子曰--邀请注册'
    html = (u"<html><head></head><body>"
            u"<p>您的好友&nbsp;<a href='http://www.afewords.com/bloger/"+ str(user_id) +"'>" + name + 
            u"</a>&nbsp;邀请您注册<a href='http://www.afewords.com'>子曰</a></p><br/><p><a href='http://www.afewords.com/reg?email="+ to + 
            u"'>注册链接</a>或者将链接复制至地址栏进行注册：http://www.afewords.com/reg?email=" + to + "</p>"
            "</body></html>")
    return send_mail(to, subject, html)
    

def create_vertify_code():
    background = (random.randrange(230,255),random.randrange(230,255),random.randrange(230,255))
    line_color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
    img_width = 90
    img_height = 30
    font_color = ['black','darkblue','darkred','red','blue','green']
    font_size = 18
    font = ImageFont.truetype(r'FreeSans.ttf',font_size)
    #font = ImageFont(font_size)
    #font = ImageFont.truetype("arial.ttf", 15)
    #request.session['verify'] = ''
    #新建画布
    im = Image.new('RGB',(img_width,img_height),background)
    draw = ImageDraw.Draw(im)
    code = random_string(6)
    #新建画笔
    draw = ImageDraw.Draw(im)
    for i in range(random.randrange(7,9)):
        xy = (random.randrange(0,img_width),random.randrange(0,img_height),random.randrange(0,img_width),random.randrange(0,img_height))
        draw.line(xy,fill=line_color,width=1)
        #写入验证码文字
    x = 4
    for i in code:
        y = random.randrange(0,10)
        draw.text((x,y), i,font=font, fill=random.choice(font_color))
        x += 14
    del x
    del draw
    buf = StringIO.StringIO()
    im.save(buf,'gif')
    buf.closed
    return [buf.getvalue(),"".join(code)]


def index_at_list(alist, obj):
    try:
        index = alist.index(obj)
        return index
    except Exception, e:
        return None
    
def keys_to_list(keys):
    tmp = re.sub(r'<','&lt;', keys)
    tmp = re.split(u',|，', tmp)
    tmp_tmp = [ re.sub(u'\n|\n\t|\t|\r\n|\r', '',i).strip() for i in tmp ]
    #tmp = re.sub(u'\s|\n|\n\t|\t|\r\n|\r', '', keys)
    #tmp = re.sub(r'<','&lt;', tmp)
    #tmp_tmp = re.split(u',|，', tmp)
    #print 'tmp_tmp', tmp_tmp
    tmp_list = []
    for iii in tmp_tmp:
        if iii != '':
            tmp_list.append(iii)

    return tmp_list


def get_max_alias(alist):
    alias = 1
    while 1:
        if str(alias) in alist:
            alias = alias + 1
        else:
            break
    return str(alias)
    
def get_index_list_by_page(alist, page=1, page_cap=10):
    sum_count = len(alist)
    sum_page = (sum_count %page_cap and sum_count / page_cap + 1) or sum_count / page_cap
    #print 'sum_page < page ', sum_page < page
    #print 'sum_page ', sum_page, type(sum_page) , 'page', page, type(page)
    if sum_page < page or page < 1:
        return (0,0)
    min_index = (page - 1) * page_cap
    max_index = (page_cap * page > sum_count and  sum_count) or page_cap * page
    
    #print min_index, max_index
    return (min_index, max_index)
    
def str_to_int_list(value):
    ''' pass str , return list, split by ',' '''
    #print type(value)
    if type(value) != unicode and type(value) != str:
         return []
    
    #print 'in last'
    tmp_list = value.split(',')
    ret_list = []
    for tmp_one in tmp_list:
        try:
            tmp_index = int(tmp_one)
        except Exception, e:
            #print 'error ', tmp_one
            continue
        else:
            ret_list.append(tmp_index)
    
    ret_list.sort() 
    return ret_list
    

def format_notification(note_to=None, note_from=None, note_to_what=None, note_from_what=None, do='reply_blog', 
    father_type='blog', group=None ):
    ''' note_to represent the to the author, note_from represent the note come from , note_to_what represent the blog 
        note_to = User(_id=1) ,  note_from = User(_id=2), note_to_what = Blog(_id=1), note_from_what = Comment(_id=1)     
    '''
    display_info = ''
    type_info = do
    try:
        if do == 'reply_blog':
            if father_type == 'blog':
                display_info = ('文章评论：您的文章<a class="noti_blog_name" target="_blank" href="/blog/' + str(note_to_what._id) + '">' + note_to_what.name + 
                            '</a>' +'被<a class="noti_author_name" target="_blank" href="/bloger/' + str(note_from._id)  + '">' + note_from.name  + 
                            '</a>' +'评论了，<a class="noti_link" target="_blank" href="/blog/'+ str(note_to_what._id) +'#com-'+  
                            str(note_from_what._id) +'">查看评论</a>')
            elif father_type == 'group-topic':
                display_info = ('话题评论：您的话题<a class="noti_blog_name" target="_blank" href="/group/' + str(group._id) + '/topic/' + str(note_to_what._id) + '">' + note_to_what.name + 
                            '</a>' +'被<a class="noti_author_name" target="_blank" href="/bloger/' + str(note_from._id)  + '">' + note_from.name  + 
                            '</a>' +'评论了，<a class="noti_link" target="_blank" href="/group/' + str(group._id) + '/topic/' + str(note_to_what._id) +'#com-'+  
                            str(note_from_what._id) +'">查看评论</a>')
            elif father_type == 'group-doc':
                display_info = ('文档评论：文档<a class="noti_blog_name" target="_blank" href="/group/' + str(group._id) + '/doc/' + str(note_to_what._id) + '">' + note_to_what.name + 
                            '</a>' +'被<a class="noti_author_name" target="_blank" href="/bloger/' + str(note_from._id)  + '">' + note_from.name  + 
                            '</a>' +'评论了，<a class="noti_link" target="_blank" href="/group/'+ str(group._id) +'/doc/'+ str(note_to_what._id) +'#com-'+  
                            str(note_from_what._id) +'">查看评论</a>')
            elif father_type == 'group-notice':
                display_info = ('公告评论：您的公告<a class="noti_blog_name" target="_blank" href="/group/'+ str(group._id) +'/notice/' + str(note_to_what._id) + '">' + note_to_what.name + 
                            '</a>' +'被<a class="noti_author_name" target="_blank" href="/bloger/' + str(note_from._id)  + '">' + note_from.name  + 
                            '</a>' +'评论了，<a class="noti_link" target="_blank" href="/group/' + str(group._id)+ '/notice/'+ str(note_to_what._id) +'#com-'+  
                            str(note_from_what._id) +'">查看评论</a>')
            else:
                pass
            #print 'dispaly_info ', display_info
            return get_log_info(display_info, type_info, note_from_what)
            
        if do == "reply_comment":
            if father_type == 'blog':
                display_info = ('回复文章：<a class="noti_author_name" target="_blank" href="/bloger/'+ str(note_from._id) +'">'+ note_from.name +
                        '</a>回复了您在文章<a class="noti_blog_name" target="_blank" href="/blog/'+ str(note_to_what._id) +'">' +
                        note_to_what.name + '</a>中的评论，'+ 
                        '<a class="noti_link" target="_blank" href="/blog/'+ str(note_to_what._id) + '#com-'+ 
                        str(note_from_what._id) + '">查看回复</a>')
            elif father_type == 'group-notice':
                display_info = ('回复公告：<a class="noti_author_name" target="_blank" href="/bloger/'+ str(note_from._id) +'">'+ note_from.name +
                        '</a>回复了您在公告<a class="noti_blog_name" target="_blank" href="/group/'+ str(group._id) +'/notice/'+ str(note_to_what._id) +'">' +
                        note_to_what.name + '</a>中的评论，'+ 
                        '<a class="noti_link" target="_blank" href="/group/' +str(group._id)+ '/notice/'+ str(note_to_what._id) + '#com-'+ 
                        str(note_from_what._id) + '">查看回复</a>')
            elif father_type == 'group-doc':
                display_info = ('回复文档：<a class="noti_author_name" target="_blank" href="/bloger/'+ str(note_from._id) +'">'+ note_from.name +
                        '</a>回复了您在文档<a class="noti_blog_name" target="_blank" href="/group/'+ str(group._id) +'/doc/'+ str(note_to_what._id) +'">' +
                        note_to_what.name + '</a>中的评论，'+ 
                        '<a class="noti_link" target="_blank" href="/group/'+ str(group._id) +'/doc/'+ str(note_to_what._id) + '#com-'+ 
                        str(note_from_what._id) + '">查看回复</a>')
            elif father_type == 'group-feedback':
                pass
            elif father_type == 'group-topic':
                display_info = ('回复话题：<a class="noti_author_name" target="_blank" href="/bloger/'+ str(note_from._id) +'">'+ note_from.name +
                        '</a>回复了您在话题<a class="noti_blog_name" target="_blank" href="/group/'+str(group._id)+'/topic/'+ str(note_to_what._id) +'">' +
                        note_to_what.name + '</a>中的评论，'+ 
                        '<a class="noti_link" target="_blank" href="/group/'+str(group._id)+'/topic/'+ str(note_to_what._id) + '#com-'+ 
                        str(note_from_what._id) + '">查看回复</a>')
            else:
                pass
            #print 'dispaly_info ', display_info
            return get_log_info(display_info, type_info, note_from_what)
            
    except Exception, e:
        logging.error(traceback.format_exc())
        return None
    

def strip_tags(html):
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()
    return ''.join(result)[:200]
    
    
def create_page_block(page_link, current_page=1, sum_count=0, page_cap=10, page_count=5):
    ''' sum_count is the sum of object, page_cap is every contains the nums of object , 
        page_count is the num of every page contains page links ,this must be even
    '''
    if current_page == 1 and sum_count < current_page * page_cap:
        return ''
    sum_page = ( sum_count % page_cap and sum_count / page_cap +1 )or sum_count / page_cap
    if current_page > sum_page:
        return ''
    extend = page_count / 2
    tmp_max_page = current_page + extend
    tmp_min_page = current_page - extend
    if tmp_max_page > sum_page or tmp_min_page < 1:
        if tmp_max_page > sum_page:
            max_page = sum_page
            more_extend = tmp_max_page - max_page
            tmp_tmp_min_page = tmp_min_page - more_extend
            min_page = ( tmp_tmp_min_page < 1 and 1 ) or tmp_tmp_min_page
            
        else:
            #tmp_min_page < 1:
            min_page = 1
            more_extend = 1 - tmp_min_page
            tmp_tmp_max_page = tmp_max_page + more_extend
            max_page = (tmp_tmp_max_page > sum_page and sum_page) or tmp_tmp_max_page
            
    else:
        min_page = tmp_min_page
        max_page = tmp_max_page
    #print min_page , max_page
    restr = "<div class='body_page'><span>页</span>"
    for ii in range(min_page, max_page+1):
        if ii == current_page:
            restr += "<span><a href='"+ page_link + str(ii) +"' class='current'>"+ str(ii) +"</a></span>"
            continue
        restr += "<span><a href='" + page_link + str(ii) + "'>" + str(ii) + "</a></span>"
    restr += "</div>"
    #print 'page block', restr
    return restr


def fun_load_code_js(viewbody):
    ''' for blog, load js'''
    if viewbody is None or viewbody == '':
        return []
    # viewbody is not None
    tmp = re.findall(r'<pre class="brush:(.+?);">', viewbody)
    tmp_list = []
    code_dict = {'applescript':'AppleScript','as3':'AS3','bash':'Bash','coldfusion':'ColdFusion','c++':'Cpp',
        'c#':'CSharp','css':'Css','delphi':'Delphi','diff':'Diff','erlang':'Erlang','groovy':'Groovy','java':'Java',
        'javafx':'JavaFX','javascript':'JScript','lisp': 'Lisp','perl':'Perl','php':'Php','plain':'Plain','python':'Python',
        'ruby':'Ruby','sass':'Sass','scala':'Scala','sql':'Sql','vb':'Vb','xml':'Xml'};
    for kkk in tmp:
        if kkk in tmp_list:
            continue
        if kkk not in code_dict:
            kkk = 'plain'
        tmp_list.append('shBrush'+code_dict[kkk]+'.js')

    #print tmp_list
    return tmp_list

def fun_authority_group(group=None):
    pass
