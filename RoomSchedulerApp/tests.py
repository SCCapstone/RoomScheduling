import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
import webtest
import main

class AppTest(unittest.TestCase):
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_user_stub()
    self.testapp = webtest.TestApp(main.application)
	
  def tearDown(self):
    self.testbed.deactivate()
	
  def login(self):
    self.testbed.setup_env( USER_EMAIL = 'test@example.com', USER_ID = '123' )
	
  def logout(self):
    self.testbed.setup_env( USER_EMAIL = '', USER_ID = '' )
	
  def testAnonymousUser(self):
    self.logout()
    response = self.testapp.get('/')
    self.assertEqual(response.status_int, 200)
    self.assertTrue("Login" in response, "No login message")
	
  def testScheduleRequest(self):
    self.login()
    response = self.testapp.get('/rooms')
    self.assertEqual(response.status_int, 200)
    self.assertTrue("Scheduled Rooms" in response, "Scheduled rooms not displayed")
    self.testapp.post('rsubmit', {'sdate': "14-2-2014", 'edate':"15-2-2014", 'roomtoselect':"029", 'stime':"8:00 AM", 'etime':"9:00 AM"})
    self.assertEqual(response.status_int, 200)
