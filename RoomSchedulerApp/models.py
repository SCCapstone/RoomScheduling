from google.appengine.ext import db
from google.appengine.api import users

class UserInfo(db.Model):
  userid = db.StringProperty()
  email = db.StringProperty()
  nickname = db.StringProperty()
  role = db.StringProperty(required=True, choices=set(["student","faculty","admin"]))
  
  @staticmethod
  def isAdmin(userid):
    q = db.GqlQuery("SELECT * FROM UserInfo WHERE userid = :1", userid)
    if q.get():
      return q.get().role == 'admin'
    else:
      return False
      
 
class RoomSchedule(db.Model):
  roomnum = db.StringProperty(required=True)
#   userid = users.UserProperty(required=True)
  userid = db.StringProperty(required=True)
  role = db.StringProperty(required=True, choices=set(["student","faculty","admin"]))
  startdate = db.DateProperty(required=True)
  enddate = db.DateProperty(required=True)
  starttime = db.TimeProperty(required=True)
  endtime = db.TimeProperty(required=True)
  reserved = db.BooleanProperty(indexed=False)

class ScheduleRequest(db.Model):
  roomnum = db.StringProperty(required=True)
  userid = db.StringProperty(required=True)
  useremail = db.StringProperty(required=True)
  role = db.StringProperty(required=True, choices=set(["student","faculty","admin"]))
  startdate = db.DateProperty(required=True)
  enddate = db.DateProperty(required=True)
  starttime = db.TimeProperty(required=True)
  endtime = db.TimeProperty(required=True)
  reserved = db.BooleanProperty(indexed=False)
  timestamp = db.DateTimeProperty(required=True)
  
class EquipmentUsage(db.Model):
  userid = db.StringProperty(required=True)
  equipment = db.StringProperty()
  iclickeramt = db.StringProperty()
  laptopsel = db.StringProperty() 

class RoomInfo(db.Model):
  roomnum = db.StringProperty(required=True)
 
class EquipmentInfo(db.Model):
  equipmenttype = db.StringProperty(required=True)

class AdminName(db.Model):
  email = db.StringProperty(required=True)
