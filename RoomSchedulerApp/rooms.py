from google.appengine.ext import db
import webapp2
from google.appengine.api import users, mail
import datetime
import re
from hashlib import sha1
from random import random


from main import BaseHandler
from models import *

class RoomHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    nums = RoomInfo.all().order("roomnum")
    template_args = {
      'logout_url': users.create_logout_url('/'),
      'user': user,
      'nums': nums
      }
    self.render_template("rooms.html", **template_args)
      
  def post(self):
    try:
      timestamp = datetime.datetime.now()
      uid = self.request.get('name')
      uemail = self.request.get('email')
      if not (re.match(r"[^@]+@[^@]+\.[^@]+", uemail) and uemail.split('@')[1].endswith('sc.edu')):
        template_args = {
          'reason': "Valid sc.edu email address needed.",
          'timestamp': timestamp,
        }
        self.render_template("roomfailure.html", **template_args)
        return
      sdate = self.request.get('sdate')
      edate = self.request.get('edate')
      rnum = self.request.get('roomtoselect')
      stime = self.request.get('stime')
      etime = self.request.get('etime')
      dkey = sha1(str(random())).hexdigest()
      mystarttimet = datetime.datetime.strptime(stime,'%I:%M %p').timetuple()
      myendtimet = datetime.datetime.strptime(etime,'%I:%M %p').timetuple()
      rss = ScheduleRequest(roomnum=rnum,userid=uid,useremail=uemail,role="admin",timestamp=timestamp,
      deletekey=dkey,
      startdate = datetime.datetime.strptime(sdate.strip(" "), '%d-%m-%Y').date(),
      enddate = datetime.datetime.strptime(edate.strip(" "), '%d-%m-%Y').date(),
      starttime = datetime.time(mystarttimet[3],mystarttimet[4]), 
      endtime = datetime.time(myendtimet[3],myendtimet[4]), reserved=True)
      rss.put()
      sender_address = "Room Scheduling Notification <notification@roomscheduler490.appspotmail.com>"
      subject = "Schedule Request deletion URL"
      body = """
      Your request of room %s has been submitted. If you need to delete this request, use the link below.
      http://roomscheduler490.appspot.com/delete?dkey=%s
      """ % (rnum, dkey)
      user_address = uemail
      mail.send_mail(sender_address, user_address, subject, body)
    except ValueError:
      template_args = {
        'reason': "Invalid format given.",
        'timestamp': timestamp,
      }
      self.render_template("roomfailure.html", **template_args)
    else:
      template_args = {
        'roomnum': rnum,
        'sdate': sdate,
        'edate': edate,
        'stime': stime,
        'etime': etime,
        'timestamp': timestamp,
      }
      self.render_template("roomsuccess.html", **template_args)

class RoomDetailHandler(BaseHandler):
  def get(self, roomnum):
    q = db.GqlQuery("SELECT * FROM RoomInfo WHERE roomnum= :1", roomnum)
    if q.get() is None:
      self.response.write('Error: invalid room number selected')
    else:
      rms = RoomSchedule.all().filter("roomnum =", roomnum)
      template_args = {
        'rms': rms,
        'roomnum': roomnum,
      }
      self.render_template("roomdetail.html", **template_args)

  def post(self, roomnum):
    try:
      timestamp = datetime.datetime.now()
      uid = self.request.get('name')
      uemail = self.request.get('email')
      if not (re.match(r"[^@]+@[^@]+\.[^@]+", uemail) and uemail.split('@')[1].endswith('sc.edu')):
        template_args = {
          'reason': "Valid sc.edu email address needed.",
          'timestamp': timestamp,
        }
        self.render_template("roomfailure.html", **template_args)
        return
      sdate = self.request.get('sdate')
      edate = self.request.get('edate')
      rnum = roomnum
      stime = self.request.get('stime')
      etime = self.request.get('etime')
      dkey = sha1(str(random())).hexdigest()
      mystarttimet = datetime.datetime.strptime(stime,'%I:%M %p').timetuple()
      myendtimet = datetime.datetime.strptime(etime,'%I:%M %p').timetuple()
      rss = ScheduleRequest(roomnum=rnum,userid=uid,useremail=uemail,role="admin",timestamp=timestamp,
      deletekey=dkey,
      startdate = datetime.datetime.strptime(sdate.strip(" "), '%d-%m-%Y').date(),
      enddate = datetime.datetime.strptime(edate.strip(" "), '%d-%m-%Y').date(),
      starttime = datetime.time(mystarttimet[3],mystarttimet[4]), 
      endtime = datetime.time(myendtimet[3],myendtimet[4]), reserved=True)
      rss.put()
      sender_address = "Room Scheduling Notification <notification@roomscheduler490.appspotmail.com>"
      subject = "Schedule Request deletion URL"
      body = """
      Your request of room %s has been submitted. If you need to delete this request, use the link below.
      http://roomscheduler490.appspot.com/delete?dkey=%s
      """ % (rnum, dkey)
      user_address = uemail
      mail.send_mail(sender_address, user_address, subject, body)
    except ValueError:
      template_args = {
        'reason': "Invalid format given.",
        'timestamp': timestamp,
      }
      self.render_template("roomfailure.html", **template_args)
    else:
      template_args = {
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
    rms = RoomSchedule.all()
    template_args = {
      'logout_url': users.create_logout_url('/'),
      'user': user,
      'rms': rms
    }
    self.render_template("roomlist.html", **template_args)

class DeletionHandler(BaseHandler):
  def get(self):
    deletionkey = self.request.get("dkey")
    q = db.GqlQuery("SELECT * FROM ScheduleRequest WHERE deletekey = :1", deletionkey)
    deleterecord = q.get()
    if deleterecord is None:
      q = db.GqlQuery("SELECT * FROM RoomSchedule WHERE deletekey = :1", deletionkey)
      deleterecord = q.get()
      if deleterecord is None:
        self.response.out.write("Invalid deletion URL.")
      else:
        deleterecord.delete()
        self.response.out.write("Scheduled room reservation deleted.")
    else:
      deleterecord.delete()
      self.response.out.write("Room reservation request deleted.")
      
        
