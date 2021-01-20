import json
import sqlite3
import os
from datetime import datetime, timedelta
from os.path import join, dirname, realpath
from flask import Flask, flash, redirect, request, render_template, jsonify, url_for, Markup, escape, session, make_response, app
from form import ContactForm
from typing import Any
from werkzeug.utils import secure_filename
from flask_babel import Babel, gettext, ngettext, _
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import hashlib
DATABASE = 'Database.db'
UPLOAD_FOLDER = '/static/uploads/'
UPLOAD_PATH = join(dirname(realpath(__file__)), UPLOAD_FOLDER[1:]) # Adapted from https://stackoverflow.com/a/37901802
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'gif', 'jpeg', 'gif', 'css', 'js'])
LANGUAGES = ['en', 'cy']

app = Flask(__name__)
app.secret_key = 'development'

# Localisation
babel = Babel(app)

#Password Hashing
bcrypt = Bcrypt(app)

# Code adapted from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
@babel.localeselector
def get_locale():
    if session.get('lang'):
        return session.get('lang');
    else:
        return request.accept_languages.best_match(LANGUAGES)

app.jinja_env.globals['get_locale'] = get_locale

@app.route("/cy")
def welsh():
    session['lang'] = 'cy'
    return redirect(request.referrer or "/")

@app.route("/en")
def english():
    session['lang'] = 'en'
    return redirect(request.referrer or "/")

# session['Email']=request.form['newportrisingserver@gmail.com']
# username = escape(session['newportrisingserver@gmail.com'])

# Inject current time object into every page
# Adapted from code example at https://stackoverflow.com/a/41231621
@app.context_processor
def current_time():
    return {
        'now': datetime.utcnow()
    }

# Generates a random inspirational quote to display on the header

def random_quote():

    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT quote,cite FROM quotes ORDER BY RANDOM() LIMIT 1")
        data = cur.fetchall()
        return data[0]
    except:
        conn.rollback()
        return [
            "Inspirational quote goes here.",
            f("Author, {current_time()['now'].year}")
        ]
    finally:
        conn.close()

@app.route("/admin/Quotes" , methods = ['POST', 'GET'])
def addquote():

    if request.method == 'POST':

        if "id" in request.form:
            id = request.form['id']

        if request.form['submit'] == 'Remove':

            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("DELETE FROM quotes WHERE id=?", [id])
                conn.commit()

                flash('This quote has been removed.', 'success')
            except:
                conn.rollback()
            finally:
                conn.close()

        if request.form['submit'] == 'Edit':

            quote = request.form['quote']
            cite = request.form['cite']

            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("UPDATE quotes SET quote=?, cite=? WHERE id=?", [quote, cite, id])
                conn.commit()

                flash('This quote has been edited.', 'success')
            except:
                conn.rollback()
            finally:
                conn.close()

        if request.form['submit'] == 'Add':
            # adding quotes
            inputquote = request.form.get('quote', default="Error")
            inputcite = request.form.get('cite' , default="Error")
            print("inserting quote ")
            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("INSERT INTO quotes ('quote','cite') VALUES(?,?)",(inputquote, inputcite) )
                conn.commit()
                msg = "Record successfully added"

            except:
                conn.rollback()
                msg = "error in insert operation"
            finally:
                conn.close()

    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM quotes")
        quotes = cur.fetchall()
    except:
        conn.rollback()
    finally:
        conn.close()

    return render_template('/admin/Quotes.html', data=quotes)

@app.context_processor
def current_time():
    return {
        'now': datetime.utcnow()
    }

@app.route("/")
def homepage():
    return render_template('homepage.html', data=random_quote())

@app.route("/example")
def example():
    return render_template('example.html', data=random_quote())

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html', data=random_quote())


@app.route("/quiz" , methods = ['POST' , 'GET'])
def quiz():
    if request.method == 'GET':
        return render_template('quiz.html', data=random_quote())
    if request.method == 'POST' :
        # answers = [request.form.get('exampleRadios1',default="Option 1 not there"),request.form.get('exampleRadios2',default="Option 2 not there"),request.form.get('exampleRadios3',
        # default="Option 3 not there"), request.form.get('exampleRadios4',default="Option 4 not there"),request.form.get('exampleRadios5',default="Option 5 not there"),
        # request.form.get('exampleRadios6',default="Option 6 not there")]
        # insertquote = request.form.get('exampleRadios1', default="Error")
        # cite = request.form.get('exampleRadios2', default="Error")
        score = 0

        if "q1" in request.form:
            if request.form['q1'] == "b":
                score += 1
        else:
            flash("Answer q1", "warning")

        if "q2" in request.form:
            if request.form['q2'] == "a":
                score += 1
        else:
            flash("Answer q2", "warning")


        if "q3" in request.form:
            if request.form['q3'] == "c":
                score += 1
        else:
            flash("Answer q3", "warning")


        if "q4" in request.form:
            if request.form['q4'] == "a":
                score += 1
        else:
            flash("Answer q4", "warning")


        if "q5" in request.form:
            if request.form['q5'] == "b":
                score += 1
        else:
            flash("Answer q5", "warning")


        if "q6" in request.form:
            if request.form['q6'] == "a":
                score += 1
        else:
            flash("Answer q6", "warning")


        if "q7" in request.form:
            if request.form['q7'] == "b":
                score += 1
        else:
            flash("Answer q7", "warning")


        if "q8" in request.form:
            if request.form['q8'] == "a":
                score += 1
        else:
            flash("Answer q8", "warning")



        #return score

        flash("Your score is " + str(score), 'success')
        return render_template('quiz.html', data=random_quote())



        #print("insert quote "+insertquote)
        #return "Hi from quiz"



@app.route("/contact", methods=["GET","POST"])
def contact():

    return render_template('contact.html', data=random_quote(), )
# if request.method == 'POST':
#     firstname = request.form.get('firstname', default="Error")
#     message = request.form.get('message', default="Error")
#     print("insert student "+ firstname)


@app.route("/feedback", methods = ['POST','GET'])
def feedback():
    if request.method =='GET':
        return render_template('feedback.html',data=random_quote())
    if request.method == 'POST':
        firstname = request.form.get('firstname', default="Error")
        message = request.form.get('message', default="Error")
        question1 = request.form.get('question1', default=1 )
        question2 = request.form.get('question2', default=1)
        question3 = request.form.get('question3', default= 1)

        print(question1)
        print(question2)
        print(question3)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO feedback ('firstname', 'Message','question_1','question_2','question_3') VALUES(?,?,?,?,?)", (firstname, message,question1,question2,question3))
            conn.commit()
            print ("record added successfully")

        except:
            conn.rollback()
            print("error in insert operation")
        finally:
            conn.close()
            flash("record added successfully",'success')
            return render_template('feedback.html',data=random_quote())





@app.route("/api/locations")
def locations():

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row # Copied from code example at https://stackoverflow.com/a/20042292
        cur = conn.cursor()
        cur.execute("SELECT * FROM locations")
        data = cur.fetchall()

        locations = []
        for row in data:

            # Get name and description with preference for selected language
            if session.get('lang') == 'cy':
                # Ternary operator code adapted from https://stackoverflow.com/questions/2802726/putting-a-simple-if-then-else-statement-on-one-line
                chosen_name = row['welsh_name'] if row['welsh_name'] else row['name']
                chosen_description = row['welsh_description'] if row['welsh_description'] else row['description']
            else:
                chosen_name = row['name']
                chosen_description = row['description']

            locations.append({
                'id': row['id'],
                'route': row['route'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'name': chosen_name,
                'image': row['image'],
                'description': chosen_description
            })

        return(jsonify(locations))

    except:
        conn.rollback()
        return {}
    finally:
        conn.close()

@app.route("/api/location/<lat>/<lng>")
def location(lat=None, lng=None):

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row # Copied from code example at https://stackoverflow.com/a/20042292
        cur = conn.cursor()
        cur.execute("SELECT * FROM locations WHERE latitude=? AND longitude=? LIMIT 1", [lat, lng])
        data = cur.fetchall()

        for row in data:
            return {
                'id': row['id'],
                'route': row['route'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'name': row['name'],
                'image': row['image'],
                'description': row['description'],
                'welsh_name': row['welsh_name'],
                'welsh_description': row['welsh_description']
            }

    except:
        conn.rollback()
        return {}
    finally:
        conn.close()


labels = [
    0,1,2,3,4,5,6
]

values = [
    5,5,6,10,15,6
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]




@app.route("/admin")
def admin():
    if session.get('admin') is not True:
        return redirect("/", code=302)
    line_labels=labels
    line_values=values
    return render_template('admin/admin.html', max=20, labels=line_labels, values=line_values)



@app.route("/admin/feedbackReview", methods = ['POST','GET'])
def feedbackReview():
    if session.get('admin') is not True:
            return redirect("/", code=302)
    if request.method =='POST':
        return render_template('/admin/feedbackReview.html')
    if request.method == 'GET':
        data = "empty"
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT * FROM feedback ")
            data = cur.fetchall()
            msg = "Record successfully RECIEVED"
            conn.close()
            return render_template('/admin/feedbackReview.html', data = data)

        except:
            conn.rollback()
            msg = "error in SELECT operation"

        return render_template('/admin/feedbackReview.html', data = data)



def checkCredentials(User, pw):
    return pw == '101Genius' and User == 'Admin'


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        User = request.form.get('User', default="Error")
        pw = request.form.get('Password', default="Error")
        # password= hashPassword(pw)
        if checkCredentials(User, pw):
            session['admin'] = True
            flash('You were successfully logged in', 'success')
            return redirect("/admin", code=302)
        else:
            flash('Incorrect Username/Password')
    return render_template("login.html")

# def hashPassword(password):
#     hashed = hashlib.sha512(password.encode('utf-8'))
#     return hashed.hexdigest()


    # def insertLogin(User,password):
    #     con = sqlite3.connect("database.db")
    #     cur = con.cursor()
    #     cur.execute("INSERT INTO login (User,password) VALUES ('Admin','101Genius')", (User,password))
    #     con.commit()
    #     con.close()
    #
    # def retrieveLogin():
    #     con = sql.connect("database.db")
    #     cur = con.cursor()
    #     cur.execute("SELECT User, password FROM login")
    #     users = cur.fetchall()
    #     con.close()
    #     return login
    #
    # if request.method=='POST':
   	# 	User = request.form['User']
   	# 	password = request.form['password']
   	# 	dbHandler.insertLogin(User, password)
   	# 	login = dbHandler.retrieveLogin()
	# 	return render_template('admin.html', users=users)
	# else:
   	# 	return render_template('login.html')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    SESSION_REFRESH_EACH_REQUEST = True


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/", code=302)

@app.route("/admin/add_waypoint", methods=["GET", "POST"])
def add_waypoint():
    if session.get('admin') is not True:
        return redirect("/", code=302)

    if request.method == 'POST':

        # Code adapted from https://www.tutorialspoint.com/flask/flask_file_uploading.htm
        route = int(request.form['route'])
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        name = request.form['name']
        description = request.form['description']
        welsh_name = request.form['welsh-name']
        welsh_description = request.form['welsh-description']
        file = request.files['file']

        if file and not allowed_file(file.filename):
            flash(Markup('This file type is not allowed. Please upload a <strong>JPG, PNG, or GIF</strong> file.'))
        else:  # File type is OK

            if file:  # File exists
                file_location = UPLOAD_FOLDER + secure_filename(file.filename)
                file.save(UPLOAD_PATH + secure_filename(file.filename))
            else:
                file_location = None

            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("INSERT INTO locations (route, latitude, longitude, name, image, description, welsh_name, welsh_description) VALUES (?,?,?,?,?,?,?,?)",
                [
                    route,
                    latitude,
                    longitude,
                    name,
                    file_location,
                    description,
                    welsh_name,
                    welsh_description
                ])
                conn.commit()

                flash('Waypoint added successfully!', 'success')
            except:
                conn.rollback()
                flash(Markup('Something went wrong. <strong>Please try again.</strong>'))
            finally:
                conn.close()

    return render_template("admin/add_waypoint.html")

@app.route("/admin/edit_waypoint", methods=["GET", "POST"])
def edit_waypoint():
    if session.get('admin') is not True:
        return redirect("/", code=302)

    if request.method == 'POST':

        id = int(request.form['id'])
        current_image = None

        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT image FROM locations WHERE id=?", [id])
            data = cur.fetchall()
            # If location has an image
            if data[0][0]:
                current_image = UPLOAD_PATH + data[0][0].split('/')[-1]
        except:
            conn.rollback()
        finally:
            conn.close()

        if request.form['submit'] == 'remove':

            try:
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("DELETE FROM locations WHERE id=?", [id])
                conn.commit()

                if current_image is not None:

                    try:
                        if os.path.exists(current_image):
                            os.remove(current_image)
                    except:
                        flash(Markup('We could not remove the associated image from the filesystem.'))

                flash('This waypoint has been removed.', 'success')
            except:
                conn.rollback()
            finally:
                conn.close()

        elif request.form['submit'] == 'update':

            route = int(request.form['route'])
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            name = request.form['name']
            description = request.form['description']
            welsh_name = request.form['welsh-name']
            welsh_description = request.form['welsh-description']
            file = request.files['file']
            remove_image = bool(request.form['remove-image'])

            # Remove current image if requested
            if remove_image and current_image is not None:

                try:
                    conn = sqlite3.connect(DATABASE)
                    cur = conn.cursor()
                    cur.execute("UPDATE locations SET image=NULL WHERE id=?", [id])
                    conn.commit()

                    if os.path.exists(current_image):
                        os.remove(current_image)

                except:
                    conn.rollback()
                    flash(Markup('Something went wrong. <strong>Please try again.</strong>'))
                finally:
                    conn.close()

            # Code adapted from https://www.tutorialspoint.com/flask/flask_file_uploading.htm
            elif file and not allowed_file(file.filename):
                flash(Markup('This file type is not allowed. Please upload a <strong>JPG, PNG, or GIF</strong> file.'))
            else:  # File type is OK

                if file:  # File exists

                    # Remove current image
                    if current_image is not None and os.path.exists(current_image):
                        os.remove(current_image)

                    file_location = UPLOAD_FOLDER + secure_filename(file.filename)
                    file.save(UPLOAD_PATH + secure_filename(file.filename))

                    try:
                        conn = sqlite3.connect(DATABASE)
                        cur = conn.cursor()
                        cur.execute("UPDATE locations SET image=? WHERE id=?",
                        [
                            file_location,
                            id
                        ])
                        conn.commit()
                    except:
                        conn.rollback()
                        flash(Markup('Something went wrong. <strong>Please try again.</strong>'))
                    finally:
                        conn.close()

                else:
                    file_location = None

                try:
                    conn = sqlite3.connect(DATABASE)
                    cur = conn.cursor()
                    cur.execute("UPDATE locations SET route=?, latitude=?, longitude=?, name=?, description=?, welsh_name=?, welsh_description=? WHERE id=?",
                    [
                        route,
                        latitude,
                        longitude,
                        name,
                        description,
                        welsh_name,
                        welsh_description,
                        id
                    ])
                    conn.commit()

                    flash('Waypoint updated successfully!', 'success')
                except:
                    conn.rollback()
                    flash(Markup('Something went wrong. <strong>Please try again.</strong>'))
                finally:
                    conn.close()

    return render_template("admin/edit_waypoint.html")

# Code adapted from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Code adapted from https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True)
