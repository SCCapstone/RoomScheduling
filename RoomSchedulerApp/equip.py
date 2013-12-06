from google.appengine.ext import db
import webapp2
from aeoid import users

from main import BaseHandler
from models import *

class EquipHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect("/login")
    else:
      types = EquipmentInfo.all().order("equipmenttype")	
      template_args = {
        'logout_url': users.create_logout_url('/'),
        'user': user,
	'etypes': types
      }
      self.render_template("equipment.html", **template_args)
      
class EquipSubmitHandler(BaseHandler):
  def post(self):
    user = users.get_current_user().nickname()
    equip = self.request.get('equiptoselect')
    iclick = self.request.get('iclickamt')
    laptop = self.request.get('laptoselect')
    timestamp = datetime.datetime.now()
    eus = EquipmentUsage(userid=user, equipment=equip, iclickeramt=iclick, laptopsel=laptop)
    eus.put()
    
    template_args = {
      'user': user,
      'equipment': equip,
      'iclicker': iclick,
      'laptops': laptop,
      'timestamp': timestamp,
    }
    self.render_template("equipsuccess.html", **template_args)

class EquipSuccessHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    
    template_args = {
        'user': user,
    }
    self.render_template("equipsuccess.html", **template_args)

class EquipFailureHandler(BaseHandler):  
  def get(self):
    user = users.get_current_user()
    timestamp = datetime.datetime.now()
    
    template_args = {
        'user': user,
    }
    self.render_template("equipfailure.html", **template_args)
