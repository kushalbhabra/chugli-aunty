import logging, email
import wsgiref.handlers
import exceptions

from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from auntymodel import Paper



class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("================================")
        logging.info("Received a mail_message from: " + mail_message.sender)
        logging.info("The email subject: " + mail_message.subject)

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
        '''
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
        '''
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
                                                           

app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
wsgiref.handlers.CGIHandler().run(app)
