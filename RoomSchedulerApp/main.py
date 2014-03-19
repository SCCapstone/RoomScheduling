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
from google.appengine.api import mail, users
#from aeoid import middleware, users
from webapp2_extras import jinja2
import datetime

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



class MainHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      q = db.GqlQuery("SELECT * FROM UserInfo WHERE userid = :1", user.user_id())
      if not q.get():
        uinfo = UserInfo(userid=user.user_id(),email=user.email(), nickname=user.nickname(), role="admin")
        uinfo.put()
    uisAdmin = False if not user else UserInfo.isAdmin(user.user_id())
    template_args = {
      'login_url': users.create_login_url('/'),
      'logout_url': users.create_logout_url('/'),
      'user': user,
      'isadmin': uisAdmin,
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

class CalendarHandler(BaseHandler):
  def get(self):
    events = RoomSchedule.all()
    response = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//roomscheduling/eventcal//EN\n"
    for event in events:
      dtstart=datetime.datetime(event.startdate.year, event.startdate.month, event.startdate.day,event.starttime+8).strftime("%Y%m%dT%H%M%S")
      dtend=datetime.datetime(event.startdate.year, event.startdate.month, event.startdate.day,event.endtime+8).strftime("%Y%m%dT%H%M%S")
      response += "BEGIN:VEVENT\nDTSTART:%s\nDTEND:%s\nSUMMARY:%s\nEND:VEVENT\n" % (dtstart,dtend,event.roomnum)
    response += "END:VCALENDAR"
    self.response.headers['Content-Type'] = 'text/calendar'
    self.response.out.write(response)
                      
    
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainHandler, name='home'),
    webapp2.Route(r'/rooms', handler=RoomHandler, name='room-list'),
    webapp2.Route(r'/rooms/<roomnum>', handler=RoomDetailHandler, name='room-detail'),
    webapp2.Route(r'/help', handler=HelpHandler, name='help'),
    webapp2.Route(r'/sendmail', handler=MailHandler, name='contact'),
    webapp2.Route(r'/equipment', handler=EquipHandler, name='equip'),
    webapp2.Route(r'/roomlist', handler=RoomListHandler, name='scheduledrooms'),
    webapp2.Route(r'/admin', handler=AdminListHandler, name='admin'),
    webapp2.Route(r'/delete', handler=DeletionHandler, name='delete'),
    webapp2.Route(r'/calendar', handler=CalendarHandler, name='cal'),
], debug=True)

def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
