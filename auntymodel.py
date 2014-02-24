from google.appengine.ext import ndb
from google.appengine.api import users

class Paper(ndb.Model):
  subject = ndb.TextProperty(indexed=True)
  uploaded_by = ndb.TextProperty() 
  blob_key = ndb.BlobKeyProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
