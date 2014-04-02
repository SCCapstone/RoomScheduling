from google.appengine.ext import db
import webapp2
from google.appengine.api import users

import datetime

from main import BaseHandler
from models import *
import re
from datetime import date
import datetime

class EquipHandler(BaseHandler):
  def get(self):
    types = EquipmentInfo.all().order("equipmenttype")	
    template_args = {
      'etypes': types
    }
    self.render_template("equipment.html", **template_args)

  def post(self):
    failflag=False
    reason=""
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
    if failflag:
        template_args = {
          'reason': reason,
          'timestamp': timestamp,
        }
        self.render_template("roomfailure.html", **template_args)
        return
    equip = self.request.get('equiptoselect')
    iclick = self.request.get('iclickamt')
    laptop = self.request.get('laptoselect')
    timestamp = datetime.datetime.now()
    eus = EquipmentUsage(userid=uid,useremail=uemail, equipment=equip, iclickeramt=iclick, laptopsel=laptop,startdate=startdatetime.date(),)
    eus.put()
    
    template_args = {
      'equipment': equip,
      'iclicker': iclick,
      'laptops': laptop,
      'timestamp': timestamp,
    }
    self.render_template("equipsuccess.html", **template_args)
