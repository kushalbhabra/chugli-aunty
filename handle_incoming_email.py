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
from auntymodel import Paper
from SCL import *

class LookUp(db.Model):
	FileName = db.StringProperty()
	BlobKey = blobstore.BlobReferenceProperty()


class LogSenderHandler(InboundMailHandler):
    

    def construct_name(self, query):
        self.name = query["subject"]+"_"+query["number"]+"_"+query["exam"]+"_"+query["year"]
        return self.name
	
    def receive(self, mail_message):
        logging.info("================================")
        logging.info("Received a mail_message from: " + mail_message.sender)
        logging.info("my email subject " + mail_message.subject)
        
        #logging.info("PREPROCESSED DATA: " + str(preprocessing(mail_message.subject)))
        
        self.Query = preprocessing(mail_message.subject)
        
        if self.Query["method"] == "get":
                logging.info("using get method")
                self.get(self.Query, mail_message)

        elif self.Query["method"] == "put":
                logging.info("using put method")
                self.put(self.Query, mail_message)

        else:
                logging.info("something chutiya method")
        
    def put(self, query, mail_message):
    
        self.look_up = LookUp()
        
        if not hasattr(mail_message, 'attachments'):
            return
        else:
            logging.info("Number of Attachment(s) %i " % len(mail_message.attachments))
        
        filename = ''
        for attach in mail_message.attachments:
            filename = attach[0]
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
        self.look_up.put()

    
    def get(self, query, mail_message):
	
	self.name = self.construct_name(query)
	logging.info("FILE NAME "+self.name)

        self.lookup = LookUp.all()
        self.files_list = self.lookup.filter("FileName =", self.name)
	
	logging.info("Query "+ str(dir(self.files_list)))
	
	##  TO Add if files_list is empty then email "FILE NOT FOUND" message

	for  self.pdf_file in self.files_list.run():
		logging.info("Got PDF FILE_named " + str(self.pdf_file.FileName))
		logging.info("PDF dir" + str(dir(self.pdf_file.BlobKey)))
	
		self.blob_info = blobstore.BlobInfo.get(self.pdf_file.BlobKey.key())
        	self.blob_reader = blobstore.BlobReader(self.pdf_file.BlobKey.key())
        
	        self.value = self.blob_reader.read()
                    
		mail.send_mail(sender="chugliaunty@gmail.com",
                	to=mail_message.sender,
                	subject=mail_message.subject,
                	body="Hi, I hope that you got what you were looking for, Regards, Aunty",
                	attachments=[(self.blob_info.filename, self.value)]
		)
         
		
'''
 	self.database = db.Query(LookUp)
	self.database.filter("FileName=", self.name)
	
	for pdf_file in self.database.filter

   
        if not hasattr(mail_message, 'attachments'):
            return
            #raise ProcessingFailedError('Email had no attached documents')
        else:
            
            logging.info("Email has %i attachment(s) " % len(mail_message.attachments))
            
        filname=''

        for attach in mail_message.attachments:
            filename = attach[0]
            contents = attach[1]


        # Create the file
        file_name = files.blobstore.create(mime_type = "application/pdf", _blobinfo_uploaded_filename='filename.pdf')

        # Open the file and write to it
        with files.open(file_name, 'a') as f:
            f.write(contents.decode())

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)

        # Get the file's blob key
        blob_key = files.blobstore.get_blob_key(file_name)

        paper = Paper()
        paper.subject = mail_message.subject
        paper.uploaded_by = mail_message.sender
        paper.blob_key = blob_key
        paper.put()
        
        try:
            logging.info( "BLOB KEY:" )
            logging.info( blob_key )
        except:
            logging.info("ERROR LOGGING BLOB KEY")

        blob_info = blobstore.BlobInfo.get(blob_key)
        blob_reader = blobstore.BlobReader(blob_key)
    
        value = blob_reader.read()
                
        mail.send_mail(sender="chugliaunty@gmail.com",
              to=mail_message.sender,
              subject=mail_message.subject,
              body="",
              attachments=[(blob_info.filename, value)]
        )
        
        papers = Paper.query(Paper.subject == mail_message.subject)
        for p in papers:                
            try:
                logging.info( "BLOB KEY:" )
                logging.info( p.blob_key )
            except:
                logging.info("ERROR LOGGING BLOB KEY")

            blob_info = blobstore.BlobInfo.get(p.blob_key)
            blob_reader = blobstore.BlobReader(p.blob_key)
        
            value = blob_reader.read()
                    
            mail.send_mail(sender="chugliaunty@gmail.com",
                  to=mail_message.sender,
                  subject=mail_message.subject,
                  body="Hi, <br />PFA. <br /><br /> Regards, Aunty",
                  attachments=[(p.subject, value)]
            )
           '''                                                

app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
wsgiref.handlers.CGIHandler().run(app)
