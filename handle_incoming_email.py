import logging, email
import wsgiref.handlers
import exceptions



from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from EmailModel import *
from auntymodel import Paper
from SCL import *

class LookUp(db.Model):
	FileName = db.StringProperty()
	BlobKey = blobstore.BlobReferenceProperty()
	
	# Paper Properties
	Subject = db.StringProperty()
	Number = db.StringProperty()
	Exam = db.StringProperty()
	Year = db.StringProperty()
	

class LogSenderHandler(InboundMailHandler):
    

    def construct_name(self, query):
        self.name = query["subject"]+"_"+query["number"]+"_"+query["exam"]+"_"+query["year"]
        return self.name
	
    def receive(self, mail_message):
 	self.email_db = Emaildb()
        logging.info("================================")
        logging.info("Received a mail_message from: " + mail_message.sender)
        logging.info("my email subject " + mail_message.subject)
        
        #logging.info("PREPROCESSED DATA: " + str(preprocessing(mail_message.subject)))
        if preprocessing(mail_message.subject):

        	self.Query = preprocessing(mail_message.subject)
		if self.Query["method"] == "get":
			logging.info("using get method")
			self.get(self.Query, mail_message)

		elif self.Query["method"] == "put":
			logging.info("using put method")
			self.put(self.Query, mail_message)

		else:
			logging.info("some chutiya method")
	else:
		## preprocessing returns False on garbage query
		self.failed_query(mail_message)
		
    def put(self, query, mail_message):
    
        self.look_up = LookUp()

        if not hasattr(mail_message, 'attachments'):
            return
        else:
            logging.info("Number of Attachment(s) %i " % len(mail_message.attachments))
        
        attachment_filename = ''
        for attach in mail_message.attachments:
            attachment_filename = attach[0]
            contents = attach[1]
        

	self.pdf_name = self.construct_name(query)

        file_name = files.blobstore.create(mime_type = "application/pdf", _blobinfo_uploaded_filename= self.pdf_name+".pdf")
           
        logging.info("PDF FILE name"+ self.pdf_name)
        logging.info("written" + str(file_name))

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
            f.write(contents.decode())

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)
 
        # Get the file's blob key
        blob_key = files.blobstore.get_blob_key(file_name)
        
        #### PUT the values in LookUp datastore
        self.look_up.FileName = self.pdf_name
        self.look_up.BlobKey = blob_key

	## Add Paper-properties
	self.look_up.Subject = self.Query["subject"]
	self.look_up.Number = self.Query["number"]
	self.look_up.Exam = self.Query["exam"]
	self.look_up.Year = self.Query["year"]

        self.look_up.put()
	
        #### PUT the values in EmailDB datastore
    	self.email_db.subject = mail_message.subject
	self.email_db.emailer = mail_message.sender
	self.email_db.put()


    def get(self, query, mail_message):
	
	self.name = self.construct_name(query)
	logging.info("FILE NAME "+self.name)

        self.lookup = LookUp.all()
	
	logging.info(query["year"])
	

	## Querying
	if query["year"] == "*":
		self.files_list = self.lookup.filter("Subject =", query["subject"]).filter("Number =", query["number"]).filter("Exam =", query["exam"])
	else:
        	self.files_list = self.lookup.filter("FileName =", self.name)
	
	##  TO Add if files_list is empty then email "FILE NOT FOUND" message
	for  self.pdf_file in self.files_list.run():
		logging.info("Got PDF FILE_named " + str(self.pdf_file.FileName))
	
		self.blob_info = blobstore.BlobInfo.get(self.pdf_file.BlobKey.key())
        	self.blob_reader = blobstore.BlobReader(self.pdf_file.BlobKey.key())
       		
	        self.value = self.blob_reader.read()
                    
		mail.send_mail(sender="chugliaunty@gmail.com",
                	to=mail_message.sender,
                	subject=mail_message.subject,
                	body="Hi, I hope you got what you were looking for, Regards, Aunty",
                	attachments=[(self.blob_info.filename, self.value)]
		)
 
        #### PUT the values in EmailDB datastore
    	self.email_db.subject = mail_message.subject
	self.email_db.emailer = mail_message.sender
	self.email_db.put()
 
    ## WHEN Query fails
    def failed_query(self, mail_message):

	mail.send_mail(sender="chugliaunty@gmail.com",
		to=mail_message.sender,
		subject="Nahi Chamka!",
		body="Sorry! could'nt understand Chuglimail with *Subject*: %s. Try something like this: get AI688 midsem 09 to AI688 2009 paper."  %str(mail_message.subject)
	)


app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
wsgiref.handlers.CGIHandler().run(app)
