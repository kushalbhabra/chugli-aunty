from google.appengine.ext import ndb
from google.appengine.api import users

class Emaildb(ndb.Model):
	subject = ndb.StringProperty(indexed=True)
	emailer = ndb.StringProperty() 
	date = ndb.DateTimeProperty(auto_now_add=True)
