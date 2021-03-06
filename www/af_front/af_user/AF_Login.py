#coding=utf-8
import sys
import traceback
import time
from datetime import datetime
import logging

from tornado.escape import json_encode

from af_front.af_base.AF_Base import *
from af_front.af_base.AF_Tool import *

from af_front.af_user.AF_LoginTool import *
from af_front.af_user.AF_UserTool import fun_get_feed_by_id


class LoginDoHandler(BaseHandler):
    def get(self):
        user = self.current_user
        if user is not None:
            self.redirect("/bloger")
            return
        result = fun_get_feed_by_id(user=None, obj_id=0, page_cap=30)
        if result[0] == 0:
            blog_list = result[1]['feed']
        else:
            blog_list = []
        return self.render("afewords-login.html",title="子曰 - 登录",user=self.current_user, blog_list=blog_list);
        
    def post(self):
        user = self.current_user
        if user is not None:
            self.redirect("/home")
            return
        email = is_value(self.get_argument("email",None))
        password = is_value(self.get_argument("pwd",None))
        token = is_value(self.get_argument("token", None))
        cookie_code = self.get_secure_cookie("ver_code", None)
        if email is None or password is None:
            self.redirect('/login?error=1')
            return
        if token is None or token.lower() != cookie_code:
            self.redirect('/login?email='+email+'&error=2')
            return
            
        rr1, rr2, usr_id = fun_login(email.lower(), password)
        if rr1 == 1:
            self.redirect('/login?email='+email+'&error=' + rr2)
            return
        self.set_cookie("UI", str(usr_id), expires_days=7)
        self.set_secure_cookie("UT", str(usr_id))
        self.set_secure_cookie("IT", self.request.remote_ip)
        self.redirect(rr2)
        return


class RegisterHandler(BaseHandler):
    def get(self):
        user = self.current_user
        if user is not None:
            self.redirect("/bloger")
            return
        self.set_secure_cookie("ver_code", "xxtest")
        if user is not None:
            self.redirect("/bloger")
            return
        result = fun_get_feed_by_id(user=None, obj_id=0, page_cap=30)
        if result[0] == 0:
            blog_list = result[1]['feed']
        else:
            blog_list = []
        return self.render("afewords-reg.html",title="子曰 - 注册", user=user, blog_list=blog_list)
        
    def post(self):
        result = {'kind':1, 'info':''}
        email = is_value(self.get_argument("email", None))
        pwd = is_value(self.get_argument("pwd", None))
        sex = is_value(self.get_argument("sex", '男'))
        name = is_value(self.get_argument("name", None))  
        token = is_value(self.get_argument("token", None))
        
        if name is None or len(name) < 2:
            result['info'] = '请您填写正确的姓名！'
            self.write(json_encode(result))
            return

        if email is None or is_email(email) is None:
            result['info'] = '邮箱格式不正确！'
            self.write(json_encode(result))
            return
        
        if pwd is None or len(pwd) < 4:
            result['info'] = '请您填写密码，至少4位！'
            self.write(json_encode(result))
            return
        cookie_token = self.get_secure_cookie("ver_code", None)
        if token is None or token.lower() != cookie_token:
            result['info'] = '验证码错误！'
            self.write(json_encode(result))
            return 
        #result['kind'], result['info'] = fun_reg(email.lower(), pwd, sex, name)
        result['kind'], result['info'] = fun_invite_reg(email.lower(), pwd, sex, name)
        if(result['kind'] == 0):
            self.set_cookie("repeat", str(time.time()))
        self.write(json_encode(result) )
        return
        
        
class ResetHandler(BaseHandler):
    def get(self):
        user = self.current_user
        if user is not None:
            return self.redirect("/bloger")
        result = fun_get_feed_by_id(user=None, obj_id=0, page_cap=30)
        if result[0] == 0:
            blog_list = result[1]['feed']
        else:
            blog_list = []
        return self.render("afewords-reset.html",title="子曰 - 密码重置",user=self.current_user, blog_list=blog_list)
        
    def post(self):
        result = {'kind':1, 'info':''}
        email = is_value(self.get_argument("email",None))
        pwd = is_value(self.get_argument("pwd", None))
        token = is_value(self.get_argument("token", None))
        if email is None or is_email(email) is None:
            result['info'] = '请填写正确的邮箱！'
            self.write(json_encode(result))
            return
        if pwd is None or len(pwd) < 4:
            result['info'] = '请您设置新密码，4位以上！'
            self.write(json_encode(result))
            return
        result['kind'], result['info'] = fun_reset(email.lower(), pwd)
        if(result['kind'] == 0):
            self.set_cookie("repeat", str(time.time()))
        self.write(json_encode(result))
        return
        
        
class CheckHandler(BaseHandler):
    def get(self):
        user = self.current_user 
        if user is not None:
            self.redirect("/bloger")
            return
        email = is_value(self.get_argument("email",None))
        token = is_value(self.get_argument("token", None))
        kind = is_value(self.get_argument("type","mail"))

        result= {'kind':1, 'info':''}

        if email is None or token is None:
            result['info'] = '非法参数！'
        else:
            if kind != "mail" and kind != "reset":
                kind = "mail"
            result['kind'], result['info'] = fun_check(email.lower(), token, kind)
        return self.render("afewords-check.html",title="子曰 - 验证邮件/密码重置",user=None, result=result, kind=kind)
        

class RepeatMailHandler(BaseHandler):
    def post(self):
        user = self.current_user
        if user is not None:
            self.redirect("/bloger")
            return
        result = {'kind':1, 'info':''}
        email = is_value(self.get_argument("email", None))
        repeat = self.get_cookie("repeat", None);
        if email is None or repeat is None:
            result['info'] = '参数错误！'
            self.set_cookie("repeat", str(time.time()))
            self.write(json_encode(result))
            return
        try:
            last_time = time.localtime(float(repeat)) 
            current_time = time.localtime()   
        except Exception, e:
            logging.error(traceback.format_exc())
            result['info'] = '参数错误！'
            self.set_cookie("repeat", str(time.time()))
            self.write(json_encode(result))
            return
        else:
            tmp1 = datetime(*last_time[:6])
            tmp2 = datetime(*current_time[:6])
            tmp3 = tmp2 - tmp1
            if tmp3.seconds < 30:
                result['info'] = '时间有误！'
                self.set_cookie("repeat", str(time.time()))
                self.write(json_encode(result))
                return
        result['kind'], result['info'] = fun_repeat_mail(email.lower())
        self.set_cookie("repeat", str(time.time()))
        self.write(json_encode(result))
        return

class InviteHandler(BaseHandler):
    @authfilter
    def get(self):
        return self.render("user-invite.html",title="子曰--邀请注册",user=self.current_user)


        
