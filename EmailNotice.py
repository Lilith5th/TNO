import smtplib 
  
class EmailError()	 :

	def __init__(self):
		pass

	def emailMe(self, notice):
		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
  
		# start TLS for security 
		s.starttls() 
  
		# Authentication 
		s.login("knxtestbox@gmail.com", "sifra123") 
  
		# message to be sent 
		message = ("Message_you_need_to_send \n{}".format(notice))
  
		# sending the mail 
		s.sendmail("knxtestbox@gmail.com", "l.deskovic@permasteelisagroup.com", message) 
  
		# terminating the session 
		s.quit() 
