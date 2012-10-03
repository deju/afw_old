#coding=utf-8

import sys
import traceback
import Image
from datetime import datetime
import logging

from user import User
from article.avatar import Avatar
from group.basicgroup import BasicGroup

from af_front.af_base.AF_Tool import *

import afwconfig as AFWConfig



def fun_reg(email, pwd, sex, name):
    # encrypt the password and token
    tmp = User.is_exist(email=email)
    if tmp is True:
        return [1,'邮箱已经被注册！']
    
    af_pwd = encrypt(pwd)
    af_random = random_string(20)
    token = unicode((af_pwd + af_random), "utf-8")
    usr = User()
    usr.set_propertys(**{'email':email, 'sex':sex, 'name':name, 'token':token, 'domain':unicode(usr._id)})
    tmp_avatar = usr.avatar
    tmp_avatar.thumb_name = '/static/avatar/small/afewords-user.jpg'

    #print 'beta.afewords.com/check?email=', email, '&token=',token
    mail_ok, mail_info = send_mail_reg(email, token, name)
    if mail_ok == 1:
        logging.error('+'*30) 
        logging.error('Email send Failed')
        logging.error('%s %s %s' % (email, token, name))
        logging.error('+'*30)
        return [1,'验证邮件发送失败！']
    else:
        return [0, '']
        
def fun_invite_reg(email, pwd, sex, name):
    tmp = User.is_exist(email=email)
    if tmp is True:
        return [1,'邮箱已经被注册！']
    AFW_Group = BasicGroup(_id=AFWConfig.afewords_group_id)
    tmp_email = email.replace(r'.', r'#')
    if AFW_Group.invitation_lib[tmp_email] is None:
        return [1, '很抱歉您并未被邀请！']
    af_pwd = encrypt(pwd)
    af_random = random_string(20)
    token = unicode((af_pwd + af_random), "utf-8")
    usr = User()
    usr.set_propertys(**{'email':email, 'sex':sex, 'name':name, 'token':token, 'domain':unicode(usr._id)})
    tmp_avatar = usr.avatar
    tmp_avatar.thumb_name = '/static/avatar/small/afewords-user.jpg'

    #print 'beta.afewords.com/check?email=', email, '&token=',token
    mail_ok, mail_info = send_mail_reg(email, token, name)
    if mail_ok == 1:
        logging.error('+'*30) 
        logging.error('Email send Failed')
        logging.error('%s %s %s' % (email, token, name))
        logging.error('+'*30)
        return [1,'验证邮件发送失败！']
    else:
        return [0, '']
    
def fun_reset(email, pwd):
    tmp = User.is_exist(email=email)
    if tmp is False:
        return [1, '邮箱尚未注册！']

    af_pwd = encrypt(pwd)
    af_random = random_string(20)
    token = unicode((af_pwd + af_random), "utf-8")

    user = User(email=email)
    user.token = token
    mail_ok, mail_info = send_mail_reset(email, token, user.name)
    if mail_ok == 1:
        logging.error('+'*30) 
        logging.error('Email send Failed')
        logging.error('%s %s %s' % (email, token, user.name))
        logging.error('+'*30)
        return [1, '重置密码邮件发送错误！']
    else:
        return [0, '']


def fun_check(email, token, kind):
    
    tmp = User.is_exist(email=email)
    if tmp is False:
        return [1,'用户不存在！']
    usr = User(email=email)
    if usr.token == token:
        usr.password = token[:40]
        usr.token = ''
        try:
            AFW_Group = BasicGroup(_id=AFWConfig.afewords_group_id)
            usr.follow_group(AFW_Group)
        except Exception:
            logging.error(traceback.format_exc())
        return [0,'']
    if kind == "mail":
        return [1, "抱歉，邮箱验证失败！"]
    else:
        return [1, "抱歉，密码重置失败！"]

def fun_repeat_mail(email):
    tmp = User.is_exist(email=email)
    if tmp is False:
        return [1,'用户不存在！']
    try:
        user = User(email=email)
        if user.token == '' or user.token is None:
            return [1, '您已经验证成功，可以登录或者重置密码！']
    except Exception, e:
        return [1, '用户不存在！']
    mail_ok, mail_info = send_mail_reset(email, user.token, user.name)
    if mail_ok == 1:
        logging.error('+'*30) 
        logging.error('Email send Failed')
        logging.error('%s %s %s' % (email, token, user.name))
        logging.error('+'*30)
        return [1, '重置密码邮件发送错误！']
    else:
        return [0, '']
       

def fun_login(email, pwd):
    tmp = User.is_exist(email=email)
    if tmp is False:
        return [1,'5','']
    usr = User(email=email)
    af_pwd = encrypt(pwd)
    db_pwd, db_id = usr.get_propertys(*('password', '_id'))
    #print db_id, type(db_id), type(db_pwd)
    db_id = str(db_id)
    db_avatar = usr.avatar
    if db_pwd == '':
        return ['0','/check', db_id]
    if af_pwd == db_pwd:
        if db_avatar.file_name == '':
            return ['0', '/settings-avatar', db_id]
        else:
            return ['0','/home', db_id]  
    else:
        return [1, '4', '']


def fun_invite_friend(user, email=''):
    ''' invite friend by email list, the list is splitby \nor \r\n '''
    email_list = email.split(';')
    #print email_list
    AFW_Group = BasicGroup(_id=AFWConfig.afewords_group_id)
    send_ok_list = []
    true_email = 0
    for one_email in email_list:
        if is_email(one_email):
            true_email = true_email + 1
            if user.domain == 'afewords.com':
                one_email = one_email.lower()
                mail_ok, mail_info = send_mail_invite(one_email, name=user.name, user_id=str(user._id))
                if mail_ok == 0:
                    #print 'one email ', one_email
                    tmp_email = one_email.replace(r'.', r'#')
                    AFW_Group.invitation_lib[tmp_email] = datetime.now()
                    user.invitations = user.invitations + 1
                    send_ok_list.append(one_email)
            else:
                if user.invitations < 5:     
                    # send the email
                    one_email = one_email.lower()
                    mail_ok, mail_info = send_mail_invite(one_email, name=user.name, user_id=str(user._id))
                    if mail_ok == 0:
                        #print 'one email ', one_email
                        tmp_email = one_email.replace(r'.', r'#')
                        AFW_Group.invitation_lib[tmp_email] = datetime.now()
                        #AFW_Group.invitation_lib['deju.tu@gmail.com'] = datetime.now()
                        user.invitations = user.invitations + 1
                        send_ok_list.append(one_email)
                else:
                    if len(send_ok_list) > 0:
                        return [1, '邀请数目操作限制！'+ ";".join(send_ok_list) + '的邀请已经发送！']
                    else:
                        return [1, "邀请数目操作限制！"]
    if true_email > len(send_ok_list):
        return [1, "操作出错！" + ";".join(send_ok_list) + '的邀请已经发送！']
    return [0, '邮件已经发送至' + ";".join(send_ok_list)]

def fun_new_domain(user, domain):
    if domain == user.domain:
        return [1, '后缀与之前相同！']
    tmp = User.is_exist(domain=domain)
    if tmp is True:
        return [1, '后缀已经被使用！']
    user.domain = domain
    return [0, '']
