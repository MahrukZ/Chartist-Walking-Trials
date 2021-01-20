from flask_wtf import Form,

from wtforms import TextField, TextAreaField, SubmitField

class ContactForm(Form):
  name = TextField("name")  #text field is a class
  subject = TextField("subject")
  email = TextField("email")
  message = TextAreaField("message") # text field area creates multiple line input
  submit = SubmitField("send") #button

# instead of writting input type="text">Name</input>
