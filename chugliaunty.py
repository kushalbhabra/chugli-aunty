#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

# BLOB STORE
import os
import urllib
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

	
class Reply(webapp2.RequestHandler):
  def get(self):
    self.response.write('Checking new mails')
    
class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write('<html><body>')
    self.response.out.write('<center><h2>Chugli Aunty ; )</h2>')
    self.response.out.write('<p>get and email here: <strong>help@chugliaunty.appspotmail.com</strong></p></center>')
    
    # Somebody write this using template
    self.response.out.write("<h2>FAQ Section</h2> <br><h3> Who's/What's Chugli Aunty?</h3>  \
    Chugli Aunty is an auto-responding email bot for all people who renew their friendship with Maggus in their class \
    <b>just before</b> the exam time so that they get access to all past papers.<br> \
    Now no more doing that torturous stuff, get instant access to all uploaded past papers delievered \
    directly to your email-account. Just write a relevant SCL query in your email subject, hit send,\
    and curse your maggu friend (for now you have neatly arranged emails containing past-papers!).<br><br<br>\
													\
    <h3>SQL suna hai, what the fk is SCL?</h3>\
    Good question; Chugli aunty requires chugli to process information and send you relevant papers. So, if SQL stands\
    for Structured Query Language, SCL stands for <b>Structured Chugli Language</b>. Just write SCL query in your email-subject, and that's it!<br> \
    An example of SCL to get 2013 Design Lab CL455 endsem paper of chemical dept:<br>\
    <i> get cl 455 endsem 13</i> <br><br>\
						\
    you can use asterisks to get papers of all years and all exam of a particular course<br>\
    <i> get cl455 * * </i> \
    				<br>\
    Similary you can use <b>list</b> command in place \"get\" to get a list of relevant papers.\
    <br><br>\
					\
    <h3>Nice! Who made this? Why?</h3>\
    Do you have time to read this section? Maggna shuru karo.. <br><br><br>\
    There is good probability that a <b>neckless fatty</b> called Aditya Patil will claim that he wrote/co-wrote this software.<br>\
    That IS 101.73% false! <br> IF he could code, then you wouldn't have seen this.\
	<br><br>\
	\"Software is like sex: it's better when it's free\"-Linus Torvalds<br>\
	<i>we completely agree:</i> <a href='https://github.com/kushalbhabra/chugli-aunty'>source</a> ")


    self.response.out.write('</body></html>')
    '''
    self.response.out.write('<html><body>')
    self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")
    '''

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)
    
app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/upload', UploadHandler),
  ('/serve/([^/]+)?', ServeHandler)
], debug=True)
