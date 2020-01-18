import os
from flask import Flask, render_template,request,redirect, url_for,send_file,send_from_directory,current_app,make_response
from flask_mysqldb import MySQL
import textract, re
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rainbow@1995'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

UPLOAD_DIRECTORY = 'static/resumes/'
#globalfn = ''

@app.route('/', methods=['GET', 'POST'])
def login_page():
  if request.method == "POST":
        email =  request.form['uname']
        password =  request.form['pwd']
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM UserDetails where mailid = %s",[email])
	row = cur.fetchone()
	if row != None:
	  pwd = row[5];
	  if password == pwd:
	    disp = url_for('display_page', email = email)
	    return redirect(disp)	
	  else:	
	    return render_template('login.html', pwd = 'false')
        else:
	  return render_template('login.html', uname = 'false')
	cur.close()
	return render_template('login.html') 		
  return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
  if request.method == "POST":
	fname =  request.form['fname']
	lname = request.form['lname']
	mail =  request.form['email']
	pwd = request.form['pwd']
	file=request.files['file']
	fileName=mail.replace(".","_")
	targetDir="/var/www/html/flaskapp/static/resumes/"+fileName+".pdf"
	file.save(targetDir)
	file_ext = file.filename
	if file_ext.endswith('.pdf'):
	  text = textract.process(targetDir)
          words = re.findall(r"[^\W_]+", text, re.MULTILINE)
	  wordCount = len(words)
	  cur = mysql.connection.cursor()
	  cur.execute("SELECT * FROM UserDetails where mailid = %s",[mail])
          row = cur.fetchone()
          if row == None:
	    cur.execute("insert into UserDetails values (%s,%s,%s,%s,%s,%s)", (fname, lname,mail,fileName,wordCount,pwd))
            mysql.connection.commit()
            cur.close()
	    disp = url_for('login_page', success = 'true')
            return redirect(disp)	
	  else:
	    return render_template('register.html', exist = 'true')
 	else:
	  return render_template('register.html', ext = 'false')
  return render_template('register.html')

@app.route('/display', methods=['GET'])
def display_page():
	email = request.args.get('email')
	cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM UserDetails where mailid = %s",[email])
        row = cur.fetchone()
        if row != None:
	  firstName = row[0]
	  lastName = row[1]	
	  mail = row[2]
	  fileName=row[3]
	  count = row[4]	
	return render_template('display.html', firstName = firstName, lastName = lastName, mail = mail, count = count, fileName=fileName )  

@app.route('/files/<file_name>')
def get_file(file_name):
	directory = os.path.join(current_app.root_path, UPLOAD_DIRECTORY)
	return send_from_directory(directory, file_name+".pdf", as_attachment=True)
if __name__ == '__main__':
  app.run()
