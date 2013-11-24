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

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.api import mail
from aeoid import middleware, users


class LoginRecord(db.Model):
  user = users.UserProperty(auto_current_user_add=True, required=True)
  timestamp = db.DateTimeProperty(auto_now_add=True)
  
class RoomSchedule(db.Model):
  roomnum = db.StringProperty(required=True)
#   userid = users.UserProperty(required=True)
  userid = db.StringProperty(required=True)
  role = db.StringProperty(required=True, choices=set(["student","faculty","admin"]))
  startdate = db.DateProperty(required=True)
  enddate = db.DateProperty(required=True)
  starttime = db.DateTimeProperty(required=True)
  endtime = db.DateTimeProperty(required=True)
  reserved = db.BooleanProperty(indexed=False)
  
class EquipmentUsage(db.Model):
  userid = db.StringProperty(required=True)
  equipment = db.StringProperty()
  iclickeramt = db.StringProperty()
  laptopsel = db.StringProperty() 

class LoginHandler(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
      login = LoginRecord()
      logging.warn(login.user)
      login.put()
    self.redirect('/')


class AppsFederationHandler(webapp.RequestHandler):
  """Handles openid login for federated Google Apps Marketplace apps."""
  def get(self):
    domain = self.request.get("domain")
    if not domain:
      self.redirect("/login")
    else:
      openid_url = "https://www.google.com/accounts/o8/site-xrds?hd=" + domain
      self.redirect("%s?openid_url=%s" %
                    (users.OPENID_LOGIN_PATH, urllib.quote(openid_url)))


class MainHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    logins = LoginRecord.all().order('-timestamp').fetch(20)
    logging.warn([x.user for x in logins])
    self.render_template("index.html", {
        'login_url': users.create_login_url('/login'),
        'logout_url': users.create_logout_url('/'),
        'user': user,
        'logins': logins,
    })
    
class RoomHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      self.render_template("rooms.html", {
          'user': user,
      })

class SelectionHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
      path = os.path.join(os.path.dirname(__file__), 'templates', file)
      self.response.out.write(template.render(path, template_vals))
      
  def post(self):
    user = users.get_current_user().nickname()
    sdate = self.request.get('sdate')
    edate = self.request.get('edate')
    rnum = self.request.get('roomtoselect')
    stime = self.request.get('stime')
    etime = self.request.get('etime')
    timestamp = datetime.datetime.now()
    rss = RoomSchedule(roomnum=rnum,userid=user,role="admin",
    startdate = datetime.datetime.strptime(sdate.strip(" "), '%d-%m-%Y').date(),
    enddate = datetime.datetime.strptime(edate.strip(" "), '%d-%m-%Y').date(),
    starttime = datetime.datetime.strptime(stime, '%I:%M %p'), 
    endtime = datetime.datetime.strptime(etime, '%I:%M %p'), reserved=True)
    rss.put()
#     if()
#    self.redirect('/roomsuccess')
#     else
#     self.redirect('/roomfailure')

    self.render_template("roomsuccess.html", {
        'user': user,
        'roomnum': rnum,
        'sdate': sdate,
        'edate': edate,
        'stime': stime,
        'etime': etime,
        'timestamp': timestamp,
    })

class HelpHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    self.render_template("help.html", {
        'user': user,
    })

class MailHandler(webapp.RequestHandler):
  def post(self):
    fromaddr = self.request.get('email') #has to be a google email
    subject = self.request.get('subject')
    msg = self.request.get('message')
    toaddr = ''
    #correct so user sends to google mail address
    mail.send_mail(toaddr, fromaddr, subject, msg)
    self.response.write('Sent Message')
    
class EquipHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      self.render_template("equipment.html", {
          'user': user,
      })
      
class EquipSubmitHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def post(self):
    user = users.get_current_user().nickname()
    equip = self.request.get('equiptoselect')
    iclick = self.request.get('iclickamt')
    laptop = self.request.get('laptoselect')
    timestamp = datetime.datetime.now()
    eus = EquipmentUsage(userid=user, equipment=equip, iclickeramt=iclick, laptopsel=laptop)
    eus.put()
    
    self.render_template("equipsuccess.html", {
        'user': user,
        'equipment': equip,
        'iclicker': iclick,
        'laptops': laptop,
        'timestamp': timestamp,
    })

class RoomListHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))

  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      rms = db.GqlQuery("SELECT * FROM RoomSchedule")
      self.render_template("roomlist.html", {
        'user': user,
        'rms': rms
      })
        

class RoomSuccessHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    #RS = db.GqlQuery("SELECT * FROM RoomSchedule")
    #for rs in RS:
    #  self.response.out.write('<b>%s</b>' % rs.roomnum)
    self.render_template("roomsuccess.html", {
        'user': user,
        'timestamp': timestamp,
    #    'RS': RS
    })
    
class RoomFailureHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
#     RS = db.GqlQuery("SELECT * FROM RoomSchedule WHERE userid="user"")
#       for rs in RS:
#         self.response.out.write('<b>%s</b>' % rs.roomnum)
    self.render_template("roomfailure.html", {
        'user': user,
        'timestamp': timestamp,
    })
    
class EquipSuccessHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    
    self.render_template("equipsuccess.html", {
        'user': user,
    })

class EquipFailureHandler(webapp.RequestHandler):
  def render_template(self, file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    self.response.out.write(template.render(path, template_vals))
    
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    
    self.render_template("equipfailure.html", {
        'user': user,
    })

application = webapp.WSGIApplication([
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
], debug=True)
application = middleware.AeoidMiddleware(application)

def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
