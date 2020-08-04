#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,render_template, url_for, redirect, request, session, flash, jsonify
import os
import mysql.connector
from mysql.connector import errorcode
from flask_socketio import SocketIO
import csv
from datetime import datetime
import json
from random import randrange
import time
from werkzeug.utils import secure_filename
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re 
import hashlib

def db_select_one(sql):
    conn = mysql.connector.connect(
        host=options["database_address"],
        user=options["database_user"],
        password=options["database_password"],
        database=options["database_name"],
        auth_plugin='mysql_native_password'
    )

    cursor = conn.cursor(buffered=True)
    cursor.execute(sql)
    ret = cursor.fetchone()
    conn.close()
    return ret

def db_select_all(sql):
    conn = mysql.connector.connect(
        host=options["database_address"],
        user=options["database_user"],
        password=options["database_password"],
        database=options["database_name"],
        auth_plugin='mysql_native_password'
    )

    cursor = conn.cursor(buffered=True)
    cursor.execute(sql)
    conn.close()
    return cursor.fetchall()

def db_insert(sql):
    conn = mysql.connector.connect(host=options["database_address"],
    user=options["database_user"],password=options["database_password"],database=options["database_name"],auth_plugin='mysql_native_password')
    cursor = conn.cursor(buffered=True)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return True

def send_mail(user,password,mailTo,message):
    
    server = smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.ehlo()
    server.login(user,password)
    server.sendmail(user,mailTo,message.as_string())
    server.close()

def time_now():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
    
def logs(cmd_type,text):
    f = open("logs.txt","a")
    wrt = time_now() + ":" + cmd_type + ":" +text + "\n"
    f.write(wrt)
    print(wrt)
    f.close()

def get_avatar(av_id):
    basepath = "static/avatars/{}".format(av_id)
    extensions = [".jpg",".jpeg",".png",".bmp"]
    for extension in extensions:
        path = basepath + extension
        if os.path.exists(path):
            ret = path
            break
        else:
            ret = "static/avatars/default.jpg"
    return ret

try:
    with open("options.json","r") as opt:
        options = json.load(opt)
except:
    exit("Can not load options file")

app = Flask(__name__) 
socketio = SocketIO(app)
clients = {}
rooms = {}

@socketio.on('message')
def get_message(json, methods=['GET', 'POST']):
    global rooms
    friend_name = json['friend_chat']
    try:
        username = session["logged_in"]
    except:
        return redirect(url_for('home'))
    sql = "SELECT contact_name FROM contacts WHERE user_id IN (SELECT user_id FROM users WHERE login='%s' AND friend_id=(SELECT user_id FROM users WHERE token='%s'))" % (username,friend_name)
    chat_id = db_select_all(sql)

    if chat_id:
        chat_path = "chats/%s.csv" % chat_id[0][0]
        rooms[session["logged_in"]] = [request.sid,chat_path]

        print(session["logged_in"])

        user = session["logged_in"]
        if os.path.exists(chat_path):
            with open(chat_path,"a",encoding="utf-8") as f:
                fieldnames = ['date','user','user_message']
                back = []
                back.append(dict(json))
                if json["message"] != "":
                    wrt = csv.DictWriter(f,fieldnames=fieldnames)
                    try:
                        wrt.writerow({"date":time_now(),"user":user,"user_message":json["message"]})
                    except:
                        pass
        else:
            with open(chat_path,"w",encoding="utf-8") as f:
                fieldnames = ['date','user','user_message']
                back = []
                back.append(dict(json))
                if json["message"] != "":
                    wrt = csv.DictWriter(f,fieldnames=fieldnames)
                    
                    try:
                        wrt.writerow({"date":time_now(),"user":user,"user_message":json["message"]})
                    except:
                        pass
        with open(chat_path, "r",encoding="utf-8") as readed:
            back = []
            i = 300
            lines = list(csv.reader(readed, delimiter=","))
            if len(lines) < 1:
                back.append({"user_name":" ","message":" "})
            else:
                for row in reversed(lines):
                    try:
                        back.append({"user_name":row[1],"message":row[2]})
                        i -= 1
                    except:
                        pass
                    if i < 0:
                        break    
                back.reverse()
        
        socketio.emit('my response', back, room=request.sid)

@socketio.on('chat_update')
def chat_update(json, methods=['GET', 'POST']):
    global rooms
    friend_name = json['friend_chat']
    username = session["logged_in"]
    sql = "SELECT contact_name FROM contacts WHERE user_id IN (SELECT user_id FROM users WHERE login='%s' AND friend_id=(SELECT user_id FROM users WHERE token='%s'))" % (username,friend_name)
    chat_id = db_select_all(sql)
    sql2 = "SELECT login FROM users WHERE token='%s';" % friend_name
    friend_name = db_select_all(sql2)
    try:
        chat_path = "chats/%s.csv" % chat_id[0][0]    
    except:
        return redirect(url_for('home'))
    
    with open(chat_path,"r",encoding="utf-8") as readed:
        back = []
        i = 300
        lines = list(csv.reader(readed, delimiter=","))
        print(len(lines))
        if len(lines) < 1:
             back.append({"user_name":" ","message":" "})
        else:
            for row in reversed(lines):
                try:
                    back.append({"user_name":row[1],"message":row[2]})
                    i -= 1
                except:
                    pass
                if i < 0:
                    break    
            back.reverse()
    print("rooms  " + str(rooms))
    logs("USER","Received message from %s to %s." % (session['logged_in'],json['friend_chat']))
    if friend_name[0][0] in rooms and  rooms[friend_name[0][0]][1] == chat_path:
        print(rooms[friend_name[0][0]])
        socketio.emit('my response', back,room=rooms[friend_name[0][0]][0])
    else:
        print("nie zalogowany lub w innym czacie")

@app.route('/')
def home(methods=['GET', 'POST']):
    if session.get('logged_in'):
        login = session["logged_in"]
        sql=  "SELECT login, token FROM contacts JOIN users ON(contacts.friend_id=users.user_id) WHERE contacts.user_id IN (SELECT users.user_id FROM users WHERE users.login='%s');" % login
        ret = db_select_all(sql)
        return render_template('main_user.html', segments=ret)
    else:
        return render_template('main_anonymous.html')

@app.route('/about')
def about(methods=['GET', 'POST']):
    if session.get('logged_in'):
        login = session["logged_in"]
        sql=  "SELECT login, token FROM contacts JOIN users ON(contacts.friend_id=users.user_id) WHERE contacts.user_id IN (SELECT users.user_id FROM users WHERE users.login='%s');" % login
        ret = db_select_all(sql)
        return render_template('main_user.html', segments=ret)
    else:
        return render_template('about.html')

@app.route('/rules')
def rules(methods=['GET', 'POST']):
    if session.get('logged_in'):
        login = session["logged_in"]
        sql=  "SELECT login, token FROM contacts JOIN users ON(contacts.friend_id=users.user_id) WHERE contacts.user_id IN (SELECT users.user_id FROM users WHERE users.login='%s');" % login
        ret = db_select_all(sql)
        return render_template('main_user.html', segments=ret)
    else:
        return render_template('rules.html')

@app.route('/help')
def help(methods=['GET', 'POST']):
    if session.get('logged_in'):
        login = session["logged_in"]
        sql=  "SELECT login, token FROM contacts JOIN users ON(contacts.friend_id=users.user_id) WHERE contacts.user_id IN (SELECT users.user_id FROM users WHERE users.login='%s');" % login
        ret = db_select_all(sql)
        return render_template('main_user.html', segments=ret)
    else:
        return render_template('help.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login = request.form['username']
        passwd = hashlib.sha256(request.form['password'].encode()).hexdigest()
        sql = "SELECT login FROM users WHERE (login = '%s' OR email = '%s') AND password = '%s' AND active = 1;" % (login,login,passwd)
        username = db_select_all(sql)
        if len(username) > 0: # Logged in                                             
            session['logged_in'] = username[0][0]
            logs("USER","User %s logged in." % username[0][0]) 
            return redirect(url_for('home'))
        else: 
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logs("USER","User %s logged out." % session['logged_in'])
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/forgotten_password')
def forgotten_password():
    return render_template("remind_password.html")

@app.route('/send_forgotten_pass_email', methods=['POST','GET'])
def send_forgotten_pass_email():
    if request.method == "POST":
        data = request.form['identification']

        def create_pass_change_id(user_id):
            chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
            ret = ""
            for i in range(24):
                ret += chars[randrange(62)]
            
            check_sql = "SELECT token FROM users WHERE token='%s'" % ret
            if len(db_select_all(check_sql)) > 0:
                create_pass_change_id(user_id)
            else:
                return ret    
            
        def send_change_email(user_mail, change_id):
                link = "{}:{}/forgotten_password_site/{}".format(options["ip_address"],options["port"],change_id)

                message = MIMEMultipart("alternative")
                message["Subject"] = "Przypomnienie hasła"
                message["From"] = "Messenger"
                message["To"] = user_mail

                text = """\
                Zmiana hasła dla adresu {},
                żeby w zmienić hasło kliknij w poniższy link, jeśli to nie ty zignoruj tą wiadomość.
                {}
                """.format(user_mail, link)
                html = """\
                <html>
                <body>
                    <p>
                        Zmiana hasła dla adresu {},<br>
                        żeby w zmienić hasło kliknij w poniższy link, jeśli to nie ty zignoruj tą wiadomość.
                        <a href="{}">KLIKNIJ TUTAJ</a> <br>
                        lub wklej link w przeglądarkę: {}
                    </p><br>
                </body>
                </html>
                """.format(user_mail, link, link)

                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")

                message.attach(part1)
                message.attach(part2)

                send_mail(options["email_address"],options["email_password"],data,message)

        if "@" in data:
            sql = "SELECT user_id FROM users WHERE email = '%s'" % data
            user_id = db_select_one(sql)
            if len(user_id) > 0:                
                change_id = create_pass_change_id(user_id[0])
                print(change_id)

                sql = "INSERT INTO password_change  VALUES('{}','{}',0)".format(change_id,user_id[0])
                db_insert(sql)

                send_change_email(data, change_id)

        else:
            sql = "SELECT user_id, email FROM users WHERE login = '%s'" % data
            user_data = db_select_one(sql)
            if len(user_data[0]) > 0:
                change_id = create_pass_change_id(user_data[0])
                email = user_data[1]
                print(change_id)

                sql = "INSERT INTO password_change  VALUES('{}','{}',0)".format(change_id,user_data[0])
                db_insert(sql)

                send_change_email(email, change_id)
                
    return redirect(url_for('home'))

@app.route('/forgotten_password_site/<code>', methods=['POST','GET'])
def forgotten_password_site(code):
    if code:
        sql = "SELECT status FROM password_change WHERE change_id='{}'".format(code)
        value = db_select_one(sql)

        if value[0] == 1:
            return redirect(url_for('home'))
        elif value[0] == 0:
            return render_template('forgotten_password_site.html',code=code)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

        
@app.route('/forgotten_password_confirm', methods=['POST','GET'])
def forgotten_password_confirm():
    if request.method == "POST":
        change_id = request.form['code']
        print(request.form['code'])
        new_password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        sql = "UPDATE password_change SET status = 1 WHERE change_id = '{}'".format(change_id) 
        db_insert(sql)
        sql2 = "UPDATE users SET password='{}' WHERE user_id = (SELECT user_id FROM password_change WHERE change_id = '{}')".format(new_password, change_id)
        db_insert(sql2)
        return redirect(url_for('home'))
    else:
        return ('', 204)

@app.route('/register', methods=['POST','GET'])
def register():
    def token_generator():
        chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
        ret = ""
        for i in range(24):
            ret += chars[randrange(62)]
        
        check_sql = "SELECT token FROM users WHERE token='%s'" % ret
        if len(db_select_all(check_sql)) > 0:
            ret = token_generator()
        return ret    
    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        password_repeat = request.form['password_repeat']
        email = request.form['email']
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        birth_date = request.form['birth_date']

        try:
            agreed = request.form['agreed']
        except:
            return redirect(url_for('home'))

        if len(username) < 3 or len(username) > 32:
            return redirect(url_for('home'))

        if len(password) < 8 or len(password) > 64 or password != password_repeat:
            return redirect(url_for('home'))

        if "@" in username:
            return redirect(url_for('home'))
            
        if not re.match("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$",email,re.IGNORECASE):
            return redirect(url_for('home'))

        if len(first_name) < 3 or len(first_name) > 32:
            return redirect(url_for('home'))

        if len(last_name) < 2 or len(last_name) > 48:
            return redirect(url_for('home'))

        if len(phone_number) < 9 or len(phone_number) > 11:
            return redirect(url_for('home'))

        if birth_date == "":
            return redirect(url_for('home'))

        if agreed != "on":
            return redirect(url_for('home'))

        if second_name is None:
            second_name = ""

        try:
            sql1 = "SELECT login FROM users WHERE login='%s'" % username

            if len(db_select_all(sql1)) > 0:
                print("ta1")
                return redirect(url_for('home'))

            sql2 = "SELECT email FROM users WHERE email='%s'" % email

            if len(db_select_all(sql2)) > 0:
                print("ta2")
                return redirect(url_for('home'))
            
            # zrobic aktywacje konta na razie 1 
            token = token_generator()

            password = hashlib.sha256(password.encode()).hexdigest()

            sql3 = "INSERT INTO users VALUES(null,'%s','%s','%s','%s','%s','%s','%s','user',0,'%s',now(),'%s','');" % (username,password,email,phone_number,first_name,second_name,last_name,birth_date,token)
            db_insert(sql3)

            def send_activation_mail(token,user_mail,user_name):

                link = "{}:{}/activate/{}".format(options["ip_address"],options["port"],token)

                message = MIMEMultipart("alternative")
                message["Subject"] = "Messenger - aktywacja konta"
                message["From"] = "Messenger"
                message["To"] = user_mail

                text = """\
                Witaj {},
                żeby w pełni korzystać z serwisu musisz aktywować konto:
                {}
                """.format(user_name, link)
                html = """\
                <html>
                <body>
                    <p>
                        Witaj {},<br>
                        żeby w pełni korzystać z serwisu musisz aktywować konto: <br>
                        <a href="{}">KLIKNIJ TUTAJ</a> <br>
                        lub wklej link w przeglądarkę: {}
                    </p><br>
                </body>
                </html>
                """.format(user_name, link, link)

                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")

                message.attach(part1)
                message.attach(part2)

                send_mail(options["email_address"],options["email_password"],[user_mail],message)

   
            send_activation_mail(token,email,username)
        except Exception as e:
            print(e)

        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/activate/<code>', methods=['POST','GET'])
def activate(code):
    if code:
        return render_template('activate.html',code=code)
    else:
        return ('', 204)

@app.route('/activation_confirm', methods=['POST','GET'])
def activation_confirm():
    if request.method == "POST":
        code = request.form['code']
        sql = "UPDATE users SET active = 1 WHERE token = '{}'".format(code) 
        db_insert(sql)
        return redirect(url_for('home'))
    else:
        return ('', 204)

@app.route('/info', methods=['POST','GET'])
def info():
    try:
        if request.method == "POST":

            friend_token = request.form['friend_name']
            username = session['logged_in']

            sql = "SELECT users.user_id, login, email, phone_number, first_name, second_name, last_name, date_of_birth, date_of_create FROM users JOIN contacts ON(users.user_id=contacts.friend_id) WHERE contacts.user_id=(SELECT user_id FROM users WHERE login='{}') AND contacts.friend_id=(SELECT user_id FROM users WHERE token='{}');".format(username,friend_token)
            res = list(db_select_one(sql))
            if len(res) <0:
                return ('', 204) 

            res[0] = get_avatar(res[0])

            return render_template('info.html',data=res)
            
        else:
            return ('', 204) 
    except:
        return ('', 204) 

@app.route('/invites', methods=['POST','GET'])
def invites():
    
    sql = "SELECT login FROM invites JOIN users ON(invites.user_id=users.user_id) WHERE invited_user_id=(SELECT user_id FROM users WHERE login='%s') AND status=0;" % session['logged_in']

    res = db_select_all(sql)
    return render_template("invites.html",invites=res)

@app.route('/accept/<name>', methods=['POST','GET'])
def accept_invite(name):
    if name:
        username = session['logged_in']
        sql = "SELECT user_id FROM users WHERE login='%s';" % username

        user_id = db_select_all(sql)
        sql2 = "SELECT user_id FROM users WHERE login='%s';" % name

        friend_id = db_select_all(sql2)
        sql3 = "SELECT MAX(contact_name) FROM contacts;"

        contact_name = db_select_all(sql3)
        sql4 = "INSERT INTO contacts VALUES(null,'%s','%s','%s');" % (user_id[0][0],friend_id[0][0],contact_name[0][0]+1)
        sql5 = "INSERT INTO contacts VALUES(null,'%s','%s','%s');" % (friend_id[0][0],user_id[0][0],contact_name[0][0]+1)
        sql6 = "UPDATE invites SET status=1 WHERE invited_user_id='%s' AND user_id='%s';" % (user_id[0][0],friend_id[0][0])
        db_insert(sql4)
        db_insert(sql5)
        db_insert(sql6)

    return ('', 204)

@app.route('/ignore/<name>', methods=['POST','GET'])
def ignore_invite(name):
    if name:
        username = session['logged_in']
        sql = "SELECT user_id FROM users WHERE login='%s';" % username

        user_id = db_select_all(sql)
        sql2 = "SELECT user_id FROM users WHERE login='%s';" % name

        friend_id = db_select_all(sql2)
        sql3 = "UPDATE invites SET status=2 WHERE invited_user_id='%s' AND user_id='%s';" % (user_id[0][0],friend_id[0][0])
        db_insert(sql3)
    return ('', 204)

@app.route('/search_user', methods=['POST','GET'])
def search_user():
    return render_template('search_user.html')

@app.route('/display_users', methods=['POST','GET'])
def display_users():
    if request.method == "POST":
        user_input = request.form['user_input']
        if len(user_input) >= 3:
            #naprawić dodawanie wiele razy
            sql = "SELECT login FROM users WHERE login LIKE '{}%' AND user_id NOT IN(SELECT contacts.friend_id FROM users JOIN contacts ON(users.user_id=contacts.user_id) WHERE users.login='{}') AND user_id NOT IN (SELECT DISTINCT invites.invited_user_id FROM invites JOIN users ON(invites.user_id=users.user_id) WHERE login LIKE '{}%') AND login!='{}' LIMIT 10;".format(user_input,session['logged_in'],user_input,session['logged_in']) 
            print(sql)
            results = db_select_all(sql)
            print(results)
    else:
        return ('', 204)
    return render_template("invites_users_list.html",users_list=results)

@app.route('/send_invite/<name>', methods=['POST','GET'])
def send_invite(name):
    sql = "SELECT user_id FROM users WHERE login='%s'" % session['logged_in']
    username = db_select_all(sql)
    print(username)

    sql2 = "SELECT user_id FROM users WHERE login='%s'" % name
    friend_name = db_select_all(sql2)
    print(friend_name)

    sql3 = "INSERT INTO invites VALUES(null,%s,'%s',now(),0);" % (username[0][0],friend_name[0][0])
    print(sql3)
    db_insert(sql3)
    return ('', 204) #,datetime.now().strftime("%Y-%m-%d")[:-3]

@app.route('/profile', methods=['POST','GET'])
def profile():
    if session.get('logged_in'):
        if request.method == "POST":
            email = request.form['email']
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            last_name = request.form['last_name']
            phone_number = request.form['phone_number']
            birth_date = request.form['birth_date']
        
        sql = "SELECT user_id FROM users WHERE login='{}'".format(session['logged_in'])
        result = db_select_one(sql)
        path = get_avatar(result[0])
        return render_template("profile.html",avatar_path=path)
    else:
        return render_template('main_anonymous.html')
        
@app.route('/upload_image', methods=['POST','GET'])
def upload_image():
    if session.get('logged_in'):
        if request.method == "POST":
            file = request.files['image-file']
            file.seek(0, os.SEEK_END)

            if len(file.filename) <= 0 or file.tell() > 3145728:  #3MB
                return redirect(url_for('profile'))
            file.seek(0)
            sql = "SELECT user_id FROM users WHERE login='{}'".format(session['logged_in'])
            user_id = db_select_one(sql)

            split = file.filename.split(".")

            if split[1] not in("jpg","jpg","bmp"):
                return redirect(url_for('profile'))
            else:    
                path = "static/avatars/" + str(user_id[0]) + "." + split[1]
                file.save(path)
                return redirect(url_for('profile'))
        else:

            return redirect(url_for('profile'))
    else:
        return render_template('main_anonymous.html')

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/change_user_data', methods=['POST','GET'])
def change_user_data():
    if request.method == "POST":

        first_name = request.form["first_name"]
        second_name = request.form["second_name"]
        last_name = request.form["last_name"]
        phone_number = request.form["phone_number"]
        birth_date = request.form["birth_date"]
        description = request.form["description"]
        
        breaking = True

        sql = "UPDATE users SET"

        if len(first_name) >= 3 and len(first_name) <= 32:
            sql += " first_name='{}',".format(first_name)
            breaking = False

        if len(second_name) >= 3 and len(first_name) <= 32:
            sql += " second_name='{}',".format(second_name)
            breaking = False

        if len(last_name) >= 3 and len(first_name) <= 32:
            sql += " last_name='{}',".format(last_name)
            breaking = False

        if len(phone_number) >= 7 and len(first_name) <= 32:
            sql += " phone_number='{}',".format(phone_number)
            breaking = False

        if len(birth_date) > 0:
            sql += " date_of_birth='{}',".format(birth_date)
            breaking = False

        if len(description) > 0:
            sql += " description='{}',".format(description)
            breaking = False

        if breaking == True:
            return redirect(url_for('profile')) 

        id_sql = "SELECT user_id FROM users WHERE login='{}';".format(session["logged_in"])

        user_id = db_select_one(id_sql)

        sql = sql[:-1]
        sql += " WHERE user_id={};".format(user_id[0])

        db_insert(sql)

    return redirect(url_for('profile'))


app.secret_key = os.urandom(12)

if __name__ == "__main__": 
    logs("SERVER","Server started...") 
    app.run(host=options["ip_address"],port=options["port"])
    socketio.run(app, debug=True)
    
