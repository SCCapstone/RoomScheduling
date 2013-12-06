#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import logging
import urllib
import datetime
import time

from google.appengine.ext import db
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.api import mail
from aeoid import middleware, users
from webapp2_extras import jinja2

from models import *

class BaseHandler(webapp2.RequestHandler):
  def render_template(self, filename, **template_args):
    self.response.write(self.jinja2.render_template(filename, **template_args))
  @webapp2.cached_property  
  def jinja2(self):
    return jinja2.get_jinja2(app=self.app)
  
from equip import *
from admin import *
from rooms import *

class LoginHandler(BaseHandler):
  def get(self):
    if users.get_current_user():
      login = LoginRecord()
      logging.warn(login.user)
      login.put()
    self.redirect('/')


class AppsFederationHandler(BaseHandler):
  """Handles openid login for federated Google Apps Marketplace apps."""
  def get(self):
    domain = self.request.get("domain")
    if not domain:
      self.redirect("/login")
    else:
      openid_url = "https://www.google.com/accounts/o8/site-xrds?hd=" + domain
      self.redirect("%s?openid_url=%s" %
                    (users.OPENID_LOGIN_PATH, urllib.quote(openid_url)))


class MainHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logins = LoginRecord.all().order('-timestamp').fetch(20)
    logging.warn([x.user for x in logins])
    template_args = {
      'login_url': users.create_login_url('/login'),
      'logout_url': users.create_logout_url('/'),
      'user': user,
      'logins': logins
    }
    self.render_template("index.html", **template_args)
    
class HelpHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    template_args ={
        'user': user,
    }
    self.render_template("help.html", **template_args)

class MailHandler(BaseHandler):
  def post(self):
    fromaddr = self.request.get('email') #has to be a google email
    subject = self.request.get('subject')
    msg = self.request.get('message')
    toaddr = "Room Scheduling Message <notification@roomscheduler490.appspotmail.com>"
    mail.send_mail(fromaddr, toaddr, subject, msg)
    self.response.write('Sent Message')
    
application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/apps_login', AppsFederationHandler),
    ('/rooms', RoomHandler),
    ('/rsubmit', SelectionHandler),
    ('/help', HelpHandler),
    ('/sendmail', MailHandler),
    ('/equipment', EquipHandler),
    ('/esubmit', EquipSubmitHandler),
    ('/roomlist', RoomListHandler),
    ('/roomsuccess', RoomSuccessHandler),
    ('/roomfailure', RoomFailureHandler),
    ('/equipsuccess', EquipSuccessHandler),
    ('/equipfailure', EquipFailureHandler),
    ('/adminlist', AdminListHandler),
    ('/appreq', AppReqHandler),
], debug=True)
application = middleware.AeoidMiddleware(application)

def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
