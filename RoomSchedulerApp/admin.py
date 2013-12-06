from google.appengine.ext import db
import webapp2
from aeoid import users


from main import BaseHandler
from models import *


class AdminListHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    elif not user.isadmin():
      self.redirect("/")
    else:
      rqs = ScheduleRequest.all()
      template_args ={
        'user': user,
        'rqs': rqs,  
      }
      self.render_template("adminlist.html", **template_args)

class AppReqHandler(BaseHandler):   
  def post(self):
    arqs = self.request.get_all("approve")
    drqs = self.request.get_all("deny")
    parqs = []
    pdrqs = []
    for rq in arqs:
      if rq in drqs: drqs.remove(rq)
      rq = db.get(rq)
      parqs.append(rq)
      accepted = RoomSchedule(roomnum=rq.roomnum, userid=rq.userid,role=rq.role,
                              startdate=rq.startdate,enddate=rq.enddate,
                              starttime=rq.starttime,endtime=rq.endtime,
                              reserved=True)
      accepted.put()
      sender_address = "Room Scheduling Notification <notification@roomscheduler490.appspotmail.com>"
      subject = "Your request has been approved"
      body = """
      Your request of room %s has been approved.
      """ % rq.roomnum
      user_address = rq.useremail
      mail.send_mail(sender_address, user_address, subject, body)
      rq.delete()
