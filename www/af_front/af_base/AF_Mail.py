#coding=utf-8

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging

afewords_admin = 'afewords@afewords.com'

def send_mail(to, subject, html_con):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = afewords_admin
    msg['To'] = to

    part_html = MIMEText(html_con,_subtype='html', _charset='utf-8')
    #part_text = MIMEText(text_con,'plain')
    #msg.attach(part_text)
    msg.attach(part_html)

    
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(afewords_admin, to, msg.as_string())
		#print s.getreply()
    except smtplib.SMTPException, e:
        logging.error('+'*30)
        logging.error('Wrong: Email SMTPException')
        logging.error(e)
        logging.error('+'*30)
        smtp.quit()
        return [1, '邮件服务器出问题了！']
    else:
        return [0, '']
    
