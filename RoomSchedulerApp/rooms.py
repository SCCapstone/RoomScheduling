from google.appengine.ext import db
import webapp2
from google.appengine.api import users
import datetime
import re


from main import BaseHandler
from models import *

class RoomHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      nums = RoomInfo.all().order("roomnum")
      template_args = {
        'logout_url': users.create_logout_url('/'),
        'user': user,
        'nums': nums
      }
      self.render_template("rooms.html", **template_args)
      
  def post(self):
    user = users.get_current_user().nickname()
    try:
      timestamp = datetime.datetime.now()
      uid = self.request.get('name')
      uemail = self.request.get('email')
      if not (re.match(r"[^@]+@[^@]+\.[^@]+", uemail) and uemail.split('@')[1].endswith('sc.edu')):
        template_args = {
          'reason': "Valid sc.edu email address needed.",
          'timestamp': timestamp,
          'user': user,
        }
        self.render_template("roomfailure.html", **template_args)
        return
      sdate = self.request.get('sdate')
      edate = self.request.get('edate')
      rnum = self.request.get('roomtoselect')
      stime = self.request.get('stime')
      etime = self.request.get('etime')
      mystarttimet = datetime.datetime.strptime(stime,'%I:%M %p').timetuple()
      myendtimet = datetime.datetime.strptime(etime,'%I:%M %p').timetuple()
      rss = ScheduleRequest(roomnum=rnum,userid=uid,useremail=uemail,role="admin",
      startdate = datetime.datetime.strptime(sdate.strip(" "), '%d-%m-%Y').date(),
      enddate = datetime.datetime.strptime(edate.strip(" "), '%d-%m-%Y').date(),
      starttime = datetime.time(mystarttimet[3],mystarttimet[4]), 
      endtime = datetime.time(myendtimet[3],myendtimet[4]), reserved=True)
      rss.put()
    except ValueError:
      template_args = {
        'reason': "Invalid format given.",
        'timestamp': timestamp,
        'user': user,
      }
      self.render_template("roomfailure.html", **template_args)
    else:
      template_args = {
        'user': user,
        'roomnum': rnum,
        'sdate': sdate,
        'edate': edate,
        'stime': stime,
        'etime': etime,
        'timestamp': timestamp,
      }
      self.render_template("roomsuccess.html", **template_args)

class RoomListHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      rms = RoomSchedule.all()
      template_args = {
	'logout_url': users.create_logout_url('/'),
        'user': user,
        'rms': rms
      }
      self.render_template("roomlist.html", **template_args)

class RoomSuccessHandler(BaseHandler):  
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    template_args = {
        'user': user,
        'timestamp': timestamp,
    }
    self.render_template("roomsuccess.html", **template_args)
    
class RoomFailureHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    template_args = {
        'user': user,
        'timestamp': timestamp,
    }
    self.render_template("roomfailure.html", **template_args)
