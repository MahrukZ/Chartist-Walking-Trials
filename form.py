from wtforms import Form, TextField, TextAreaField, SubmitField, validators, ValidationError
from flask_wtf import FlaskForm, Form



class ContactForm(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])  #text field is a class
  subject = TextField("Subject")
  email = TextField("Email")
  message = TextAreaField("Message") # text field area creates multiple line input
  submit = SubmitField("Send") #button

# instead of writting input type="text">Name</input>
