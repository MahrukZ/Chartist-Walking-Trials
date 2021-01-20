//needs to be edited
// used https://www.w3resource.com/javascript/form/all-letters-field.php
// This website helped me to come with the idea for fname_validation.

var validation = {
  fname_validation : function(){
    var number = ["1","2","3","4","5","6","7","8","9","0"];
    var fname=document.forms["myform"]["firstname"].value;
    for(var i in number) {
      if (fname.includes(i) == false) {
        i++;
        if (i == number.length) {
            return true;
        }
      }
      else if (fname.includes(i)){
        alert("Please input only letters for the first name and second");
        return false;
      }
    }
  },
  lname_validation : function(){
    var number = ["1","2","3","4","5","6","7","8","9","0"];
    var lname=document.forms["myform"]["lastname"].value;
    for(var i in number) {
      if (lname.includes(i) == false) {
        i++;
        if (i == number.length) {
            return true;
        }
      }
      else if (lname.includes(i)){
        alert("Please input only letters");
        return false;
      }
    }
  },
  email : function(){
    var email=document.forms["myform"]["email"].value;
    var mailformat = ["@", ".", "-", "_",]
    //var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    for (var i in mailformat) {
      if (email.includes(i) == false) {
        i++;
        if (i == email.length) {
          alert("Please input a proper email address");
          return false;
        }
      }
      if (email.includes("@") == false) {
        alert("Please input a proper email address");
        return false;
      }
      else if (email.includes(i)) {
        return true
      }
    }
  },
  phonenumber : function(){
    phone=document.forms["myform"]["phonenumber"].value;
    if (phone.length != 11) {
      alert("Please input a proper phone number");
      return false;
    }
    else {
      return true;
    }
  }
}

function validate(){
  validation.fname_validation();
  validation.lname_validation();
  validation.email();
  validation.phonenumber();
}
