from google.appengine.ext import db
import webapp2
from google.appengine.api import users, mail
import datetime
from datetime import date
import re
from hashlib import sha1
from random import random
import logging


from main import BaseHandler
from models import *

def genblocktable(room):
  todayblocks=["Free"]*12
  tomorrowblocks=["Free"]*12
  dayafterblocks=["Free"]*12
  today = date.today()
  tomorrow = today+datetime.timedelta(days=1)
  dayafter = today+datetime.timedelta(days=2)
  todayschedule = db.GqlQuery("SELECT starttime, endtime FROM RoomSchedule WHERE roomnum = :1 AND startdate = :2", room, today).run()
  #RoomSchedule.all().filter("roomnum =", room).filter("startdate =", today)
  tomorrowschedule = db.GqlQuery("SELECT starttime, endtime FROM RoomSchedule WHERE roomnum = :1 AND startdate = :2", room, tomorrow).run()
  dayafterschedule = db.GqlQuery("SELECT starttime, endtime FROM RoomSchedule WHERE roomnum = :1 AND startdate = :2", room, dayafter).run()
  if todayschedule is not None:
    for sched in todayschedule:
      for i in range(sched.starttime, sched.endtime):
        todayblocks[i] = "Reserved"
  if tomorrowschedule is not None:
    for sched in tomorrowschedule:
      for i in range(sched.starttime, sched.endtime):
        tomorrowblocks[i] = "Reserved"
  if dayafterschedule is not None:
    for sched in dayafterschedule:
      for i in range(sched.starttime, sched.endtime):
        dayafterblocks[i] = "Reserved"
  return [todayblocks,tomorrowblocks,dayafterblocks]

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

class RoomDetailHandler(BaseHandler):
  def get(self, roomnum):
    q = db.GqlQuery("SELECT * FROM RoomInfo WHERE roomnum= :1", roomnum)
    if q.get() is None:
      self.response.write('Error: invalid room number selected')
    else:
      template_args = {
        'roomnum': roomnum,
        'timetable': timetable,
        'blocktable': genblocktable(roomnum)
      }
      self.render_template("roomdetail.html", **template_args)

  def post(self, roomnum):
    try:
      failflag = False
      reason = ""
      timestamp = datetime.datetime.now()
      uid = self.request.get('name')
      if not uid:
        failflag = True
        reason = "You forgot your name."
      uemail = self.request.get('email')
      if (not failflag) and (not (re.match(r"[^@]+@[^@]+\.[^@]+", uemail) and uemail.split('@')[1].endswith('sc.edu'))):
        failflag = True
        reason="Valid sc.edu email address needed."
      sdate = self.request.get('sdate')
      
      if not failflag and not sdate:
        failflag = True
        reason = "You forgot the date."
      elif not failflag:
        startdatetime = datetime.datetime.strptime(sdate.strip(" "), '%m/%d/%Y')
        delta = startdatetime - timestamp
        if delta.days < -1:
          failflag = True
          reason = "You entered a date in the past."
      rnum = roomnum
      stime = self.request.get('stime')
      etime = self.request.get('etime')
      if not failflag and int(etime)-int(stime) <= 0:
        failflag = True
        reason = "Your end time was before the start time."
      if failflag:
        template_args = {
          'reason': reason,
          'timestamp': timestamp,
        }
        self.render_template("roomfailure.html", **template_args)
        return
      dkey = sha1(str(random())).hexdigest()
      rss = ScheduleRequest(roomnum=rnum,userid=uid,useremail=uemail,role="admin",timestamp=timestamp,
      deletekey=dkey,
      startdate = startdatetime.date(),
      starttime = int(stime), 
      endtime = int(etime), reserved=True)
      rss.put()
      sender_address = "Room Scheduling Notification <notification@roomscheduler490.appspotmail.com>"
      subject = "Schedule Request deletion URL"
      body = """
      Your request of room %s from %s to %s on %s has been submitted. If you need to delete this request, use the link below.
      http://roomscheduler490.appspot.com/delete?dkey=%s
      """ % (rnum,timetable[int(stime)],timetable[int(etime)],sdate, dkey)
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
        'stime': timetable[int(stime)],
        'etime': timetable[int(etime)],
        'timestamp': timestamp,
      }
      self.render_template("roomsuccess.html", **template_args)


class RoomListHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    rms = RoomSchedule.all()
    uisAdmin = False if not user else UserInfo.isAdmin(user.user_id())
    template_args = {
      'user': user,
      'rms': rms,
      'timetable': timetable,
      'isadmin': uisAdmin,
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
      



  
