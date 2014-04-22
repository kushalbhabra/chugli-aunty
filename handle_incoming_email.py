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
from google.appengine.runtime import apiproxy_errors
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
            
        #Logging email details in datastore
 	self.email_db = Emaildb()
    	try: 
		self.email_db.subject = mail_message.subject
		self.email_db.emailer = mail_message.sender
		self.email_db.put()
		logging.info("================================")
		logging.info("Received a mail_message from: " + mail_message.sender)
		logging.info("my email subject " + mail_message.subject)

        #Calling get(), put() or get_list() depending on method of query
		if preprocessing(mail_message.subject):

			self.Query = preprocessing(mail_message.subject)
			if self.Query["method"] == "get":
				logging.info("Method: get")
				self.get(self.Query, mail_message)

			elif self.Query["method"] == "put":
				logging.info("Method: put")
				"""
					Check for put privilege here
				"""
				self.put(self.Query, mail_message)
				
			elif self.Query["method"] == "list":
				logging.info("Method: get_list")
				self.get_list(self.Query, mail_message)

			else:
				logging.info("some chutiya method")
		else:
			## preprocessing returns False on garbage query
			self.failed_query(mail_message, self.Query)
	except:
		logging.info(" Caught exception, farting it out")
		self.failed_query(mail_message, self.Query)
		# Handles blank subject email
		pass
        
			
    def search(self,query,mail_message):
        self.name = self.construct_name(query)
	logging.info("FILE NAME "+self.name)

        self.lookup = LookUp.all()
	self.files_list = self.lookup.filter("Subject =", query["subject"]).filter("Number =", query["number"])

	# Can somebody write an one-liner elegant GQL query for this?
	if query["year"] != "*":
		self.files_list = self.files_list.filter("Year =", query["year"])
	if query["exam"] != "*":
		self.files_list = self.files_list.filter("Exam =", query["exam"])

	## Check for somebody attempting to do a lame wildcard-search
	if query["subject"] == "*" or query["number"] == "*":
		self.lame_wildcard_search(mail_message)
       	
        return self.files_list

    def put(self, query, mail_message):
    	
        self.look_up = LookUp()
	
        if not hasattr(mail_message, 'attachments'):
            return
        else:
            logging.info("Number of Attachment(s) %i " % len(mail_message.attachments))
        
        attachment_filename = ''
        for attach in mail_message.attachments:
            attachment_filename = str(attach[0])
	    contents = attach[1]
        

	self.pdf_name = self.construct_name(query)
	
	if attachment_filename.split(".")[-1] == 'pdf':
	        file_name = files.blobstore.create(mime_type = "application/pdf", _blobinfo_uploaded_filename= self.pdf_name+".pdf")
	else :
	        file_name = files.blobstore.create(mime_type = "application/octet-stream", _blobinfo_uploaded_filename= self.pdf_name+"."+ attachment_filename.split(".")[-1] )


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

    def get(self, query, mail_message):

	#Get relevant files  by searching datastore using query
	self.files_list = self.search(query,mail_message)

        #No files found
	if self.files_list.count()==0:
		self.mail_searchIsEmpty(query,mail_message)
		
	#One or more files found
	else:
                self.attachedPapers = []
                for  self.pdf_file in self.files_list.run():

                        logging.info("Got PDF FILE_named " + str(self.pdf_file.FileName))
                
                        self.blob_info = blobstore.BlobInfo.get(self.pdf_file.BlobKey.key())
                        self.blob_reader = blobstore.BlobReader(self.pdf_file.BlobKey.key())
                        self.value = self.blob_reader.read()
                        self.attachedPapers.append((self.blob_info.filename, self.value))
                try:
                        mail.send_mail(sender="chugliaunty@gmail.com",
                                        to=mail_message.sender,
                                        subject=mail_message.subject,
                                        body="Hi Maggu, check attachments. I hope you got what you were looking for...    \
                                        Regards, Aunty",
                                        html="Hi Maggu, <b>check attachments</b>.<br> I hope you got what you were looking for...    \
					<br><br>Regards,<br> Aunty",
                                        attachments=self.attachedPapers
                                )
                except apiproxy_errors.OverQuotaError, message:
                        mail.send_mail(sender="chugliaunty@gmail.com",
                                                to=mail_message.sender,
                                                subject=mail_message.subject,
                                                body="Hi Maggu, Unfortunately my qouta for attachments for today is over. I am telling aditya idiot to extend  my qouta as soon as possible. \n \n Regards,Aunty "
                                        )
    
    def get_list(self, query, mail_message):

	#Get relevant files by searching datastore using query
	self.files_list = self.search(query,mail_message)
	
        #No files found
	if self.files_list.count()==0:
		self.mail_searchIsEmpty(query,mail_message)
		
	#One or more files found
        else:
                plain_body = "I found %d paper(s) \n" % (self.files_list.count())

                #Show details for each file found such as subject,number,exam,year in Message Body.
                for  self.pdf_file in self.files_list.run():
                        plain_body+= "\n%s \t %s \t %s \t %s"  % (self.pdf_file.Subject,self.pdf_file.Number,self.pdf_file.Exam,self.pdf_file.Year)
                        plain_body+= "\n"
                
                plain_body += "\nRegards,\n Aunty"
                mail.send_mail(sender="chugliaunty@gmail.com",
                                to=mail_message.sender,
                                subject=mail_message.subject,
                                body=plain_body
                        ) 
 
        #### PUT the values in EmailDB datastore
    	self.email_db.subject = mail_message.subject
	self.email_db.emailer = mail_message.sender
	self.email_db.put()
 
    ## When query parsing fails
    def failed_query(self, mail_message, query):

	mail.send_mail(sender="chugliaunty@gmail.com",
		to=mail_message.sender,
		subject="Nahi Chamka!",
		body="Sorry! could'nt understand Chuglimail with *Subject*: %s. You can ALSO use asterisks in your chugli, keep SPACES inbetween,  [BETA Auto-suggestion Feature]: Copy-paste this as your subject: %s                              CHECK http://chugliaunty.appspot.com on how to construct query,              Regards, Aunty"  %(str(mail_message.subject), str("get "+ query['subject']+' '+query['number']+' '+"*"+' '+"*" )),
		html="Sorry! could'nt understand Chuglimail with <b>Subject</b>: %s. <br><br>You can ALSO use asterisks in your chugli, keep SPACES inbetween, <br><br>[BETA Auto-correction Feature]: <b>Copy-paste this as your subject: %s </b> <br><br> CHECK http://chugliaunty.appspot.com on how to construct query, <br><br> Regards, Aunty"  %(str(mail_message.subject), str("get "+ query['subject']+' '+query['number']+' '+"*"+' '+"*" ))
	)
	
    # When no files are found, mail relevant message.
    def mail_searchIsEmpty(self,query,mail_message):
            mail.send_mail(sender="chugliaunty@gmail.com",
                	to=mail_message.sender,
                	subject=mail_message.subject,
                 	html="Sorry, couldn't find any papers by <b>Subject/Code: %s-%s for %s year 20%s </b>     \
				<br><br>Regards,<br> Aunty" %(query["subject"], query["number"], query["exam"], query["year"]),
		       	body="Sorry, couldn't find any papers by Subject/Code: %s-%s for %s year 20%s      \
				Regards, Aunty" %(query["subject"], query["number"], query["exam"], query["year"])
		)

    def lame_wildcard_search(self, mail_message):
    	    mail.send_mail(sender="chugliaunty@gmail.com",
                	to=mail_message.sender,
                	subject="LAME!",
                	body="Either you were trying to access all records/papers in database or you have difficulty writing in SCL. If it's later, why not check http://chugliaunty.appspot.com ?     \
				Regards, Aunty"
		)



app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
wsgiref.handlers.CGIHandler().run(app)
