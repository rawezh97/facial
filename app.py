from flask_login import login_user , login_required , logout_user , current_user ,LoginManager
from flask import Flask, render_template, redirect, request, flash , Response ,abort
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import face_recognition
import urllib.request
import numpy as np
import sqlite3
import time
import cv2
import os
from flask_mail import Mail # for smtp (sending mail)
from flask_mail import Message
import random
import pyqrcode
import png
from pyzbar import pyzbar



app = Flask(__name__)
connection = sqlite3.connect("dbs.db" , check_same_thread=False)
data = connection.cursor()
app.config['SECRET_KEY'] = 'jgjawrgawdsldgasdf'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'login.html'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) # in here the get means prrimary key in the data base (looacking fr primary key )



#@app.errorhandler(404)
#def page_not_found(e):
#    # note that we set the 404 status explicitly
#    return render_template('404 .html'), 404
#


@app.route('/',methods=["POST","GET"])
def index():
   return render_template('home.html')

@app.route('/login' , methods=['GET' , 'POST'])
def login():
    username = request.form.get('user')
    password = request.form.get('passwd')

    if username == "" or password == "":
        flash("The filds can not be empty" , category="error")
    elif password =="'" :
        flash("username or password incorrect" , category="error")

    else :
        sql = "select username,passwd from users"
        result = data.execute(sql)
        for usr in result :
            if username == usr[0] and password == usr[1]:
                flash("successfully loged in" , category="success")
                return render_template("home.html")
    return render_template("login.html")
@app.route("/logout")
def logout():
    return render_template("login.html")
@app.route('/add_target' , methods=['GET' , 'POST'])
def add_target():
    return render_template("add_target.html")
@app.route('/target_info' , methods=['GET' , 'POST'])
def target_info():
    sql = "select * from gg"
    userdata = data.execute(sql)
    admin = False
    return render_template("target_info.html" , users=userdata ,admin = admin)
@app.route("/admin_list" , methods=['GET' , 'POST'])
def admin_list():
    query = "select * from users"
    admindata = data.execute(query)
    admin = "True"
    return render_template("target_info.html" , users = admindata ,admin = admin)

@app.route('/target_modify' , methods=['GET' , 'POST'])
def target_modify():
    sql = "select * from gg"
    userdata = data.execute(sql)
    return render_template("target_modify.html" , users=userdata)


@app.route("/search" , methods=['GET' , 'POST'])
def search():
    search_item = request.form.get('search')
    if search_item == "":
        flash("Search is empty!" , category="error")


    item = []
    try:
        x = search_item.isdigit()
        if x == True :
            if len(search_item) == 4 :
                query = "select * from gg where code=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)
            elif len(search_item) < 11 :
                query = "select * from gg where id=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)
            elif len(search_item) == 11 :
                query = "select * from gg where phone=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)
        else :
            if search_item == "Wanted":
                query = "select * from gg where info=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)

            elif search_item == "Normal":
                query = "select * from gg where info=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)

            else :
                query = "select * from gg where username=?"
                item.append(search_item)
                search_result = data.execute(query , item)
                return render_template("target_info.html" , users=search_result)

    except:
        return render_template("target_info.html" )


@app.route('/add_author' , methods=['GET' , 'POST'])
def add_author():
    if request.method=="POST":
        username = request.form.get('username')
        email = request.form.get('email')
        passwd = request.form.get('password')
        verify_passwd = request.form.get('password2')

        if username == "" or email == "" or passwd == "":
            flash("The filds can not be empty" , category="error")
        elif passwd != verify_passwd :
            flash("Password Dosen't match" , category="error")
        elif len(username) < 3 or len(passwd)< 4 :
            flash("Username or Password to short" , category="error")
        elif username[0] == "'" or passwd[0] == "'" or email[0] == "'" :
            flash("what is up mr.roboot" , category="error")
        else :
            last_id = "select max(id) from users"
            last_id = data.execute(last_id)
            for i in last_id:
                id = i[0]
                print (id)
            id += 1
            sql = "insert into users values(?,?,?,?)"
            source = [id,username,email,passwd]
            query_data = data.execute(sql,source)
            connection.commit()
            flash("User acount successfully added" , category="success")
            return render_template("home.html")



    return render_template("add_author.html")
#@app.route("/delete_author" , methods=['GET' , 'POST'])
#def delete_author():
#    id_row = request.form.get('author_id')
#    query = "DELETE from users where id=?"
#    print (id_row)
#    print (type(id_row))
#
#    data.execute(query,id_row)
#    connection.commit()
#    flash("Author deleted")
#    return render_template("target_modify.html")
#

@app.route("/delete_author" , methods=['GET' , 'POST'])
def delete_author():
    row_id = request.form.get("row_id")
    max_id = "select max(id) from users"
    max_id = data.execute(max_id)
    for id in max_id:
        last_id = id[0]
    if not row_id.isdigit():
        flash("TheID Must Be Number!" ,category="error")
    elif int(row_id) > int(last_id) :
        flash("This ID Dos not exists!" ,category="error")
    else :
        sql = "DELETE from users where id=?"
        data.execute(sql,row_id)
        connection.commit()
        flash("successfully deleted")
    return render_template("add_author.html")


@app.route("/delete_row" , methods=['GET' , 'POST'])
def delete_row():
    row_id = request.form.get("row_id")
    max_id = "select max(id) from gg"
    for id in max_id:
        last_id = id[0]
    if not row_id.isdigit():
        flash("TheID Must Be Number!" ,category="error")
    elif row_id > last_id :
        flash("This ID Dos not exists!" ,category="error")
    else :
        sql = "DELETE from gg where id=?"
        data.execute(sql,row_id)
        connection.commit()
        flash("successfully deleted")
    return render_template("target_modify.html")

@app.route("/update" , methods=['GET' , 'POST'])
def update():
    if request.method == 'POST':
        id = request.form.get('id')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        info = request.form.get('info')

        files = request.files.getlist('files')

        if id =="" and username=="" and email == "" and phone == "" and age == "" and info == "" and files == "":
            flash("One or More Fild Empty please try again" , category="error")
        #elif not id.isdigit():
        #    flash("the id must be a numer",category="error")
        #elif not phone.isdigit():
        #    flash("The phone must be a number" , category = "error")
        #elif not len(phone)==11 :
        #    flash("The number must ebt 11 charecters" , category = "error")

        else :
            for file in files:
                filename = secure_filename(file.filename)
                if not os.path.exists(f"static/uploads/{filename}"):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sql = "select * from gg where id=?"
            result = data.execute(sql,id)
            for i in result:
                if i[8] == "":
                    print (i[1])
                    code = random.randint(5555,8888)
                    user_info = f'''
co:{code}
un:{i[1]}
em:{i[2]}
ph:{i[3]}
ag:{i[4]}
in:{i[5]}
'''
                    QR_generator = pyqrcode.create(user_info)
                    QR_generator.svg("static/barcode/svg/"+i[1]+".svg" , scale = 3)
                    QR_generator.png("static/barcode/png/"+i[1]+".png", scale = 3)
                    qr_filename = i[1]+".svg"
                    qr = "static/barcode/png/"+i[1]+".png"
                    qr_file = open(qr,"rb")
                    qr_content = qr_file.read()
                elif i[10] =="":
                    user_info = f'''
co:{i[8]}
un:{i[1]}
em:{i[2]}
ph:{i[3]}
ag:{i[4]}
in:{i[5]}
'''
                    QR_generator = pyqrcode.create(user_info)
                    QR_generator.svg("static/barcode/svg/"+i[1]+".svg" , scale = 3)
                    QR_generator.png("static/barcode/png/"+i[1]+".png", scale = 3)
                    qr_filename = i[1]+".svg"
                    qr = "static/barcode/png/"+i[1]+".png"
                    qr_file = open(qr,"rb")
                    qr_content = qr_file.read()
                else :
                    code = i[8]
                    qr_filename = i[10]
                if not i[8] == "":
                    code = i[8]
                if username == "":
                    username = i[1]
                if email=="":
                    email = i[2]
                if phone == "":
                    phone = i[3]
                if age =="":
                    age = i[4]
                if info == "":
                    info =i[5]
                if filename=='' :
                    image_name = i[6]
                else :
                    image_name = filename

            update_sql = f"update gg SET username='{username}',email='{email}',phone='{phone}',age='{age}',info='{info}',image_name='{image_name}' , code='{code}' , qr_filename='{qr_filename}'  where id=?"
            gg = data.execute(update_sql,id)
            connection.commit()
            flash("Updated" , category="success")
    return render_template("target_modify.html")


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

uniqe_code = []
@app.route("/target_upload",methods=["POST","GET"])
def target_upload():
    sql = "select max(id) from gg"
    max_id = data.execute(sql)
    for id in max_id:
        r = id[0]
        if r == None:
            r = 0
    now = datetime.now()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        info = request.form.get('info')
        files = request.files.getlist('files')

        code = random.randint(1000,5555)
        uniqe_code.append(code)

        if username=="" or email == "" or phone == "" or age == "" or info == "" or files == "":
            flash("One or More Fild Empty please try again" , category="error")
        elif not phone.isdigit():
            flash("The phone must be a number" , category = "error")
        elif not len(phone)==11 :
            flash("The number must ebt 11 charecters" , category = "error")

        else:
            user_info = f'''
co:{code}
un:{username}
em:{email}
ph:{phone}
ag:{age}
in:{info}
'''
            QR_generator = pyqrcode.create(user_info)
            QR_generator.svg("static/barcode/svg/"+username +".svg" , scale = 3)
            QR_generator.png("static/barcode/png/"+username  +".png", scale = 3)
            qr_code_filename = username+".svg"
            qr = "static/barcode/png/"+username+".png"
            qr_file = open(qr,"rb")
            qr_content = qr_file.read()

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if not os.path.exists(f"static/uploads/{filename}"):
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    sql = "INSERT INTO gg VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                    dir = os.listdir("static/uploads")
                    if os.path.exists(f"static/uploads/{filename}"):
                        r +=1
                        image = filename
                        file = open(f"static/uploads/{image}" , "rb")
                        image_content = file.read()
                        #image_name = image.split(".")[0]
                        image_name = image
                        data.execute(sql , [r,username,email,phone,age,info, image_name , image_content , code ,qr_content , qr_code_filename])
                        connection.commit()
                        flash('File(s) successfully uploaded')
                        #os.remove(f"static/uploads/{image}")
                    else :
                        flash("Can not process the file!" , category="error")
    return render_template('add_target.html')


def facial_recignation():
#    def connection():
#        global connection
#        global data
#        try:
#            connection = sqlite3.connect("dbs.db")
#            data = connection.cursor()
#        except Exception as e:
#            print ("connection faild")
#    connection()
#
#       To open cctv camera
#
##print("Before URL")
#cap = cv2.VideoCapture('rtsp://admin:123456@192.168.1.216/H264?ch=1&subtype=0')
##print("After URL")
#
#while True:
#
#    #print('About to start the Read command')
#    ret, frame = cap.read()
#    #print('About to show frame of Video.')
#


#           open phone camera
#
#
#capture = cv2.VideoCapture(“http://192.168.1.67:8080/video")
#while(True):
#   ret, frame = capture.read()
#   cv2.imshow(‘livestream’, frame)
#
#
    def image_initialicer(path):
        try:
            file = face_recognition.load_image_file('static/uploads/'+ path)
            file_encoding = face_recognition.face_encodings(file)[0]
        except Exception as e:
            print ("this image is incrupted")
        return file_encoding

    def check_file(img):
        try:
            file = face_recognition.load_image_file('static/uploads/'+ img)
            file_encoding = face_recognition.face_encodings(file)[0]
            return True
        except Exception as e:
            return False

    #connection()
    capture_vedio = cv2.VideoCapture(0)

    simler_encoding_face = []
    simler_name_face = []
    face_location = []
    face_encoding = []


    photo_info = data.execute("select username,image_name,image from gg")
    for username,imgname,image in photo_info:
        if not os.path.exists("static/uploads"):
            os.mkdir("static/uploads")
        if not os.path.exists(f"static/uploads/{imgname}"):
            autocompile = open(f"static/uploads/{imgname}" , "wb")
            autocompile.write(image)
            print ("seccess!")
            autocompile.close()

    direct = os.listdir("/home/world/Desktop/test_web/static/uploads")
    for file_name in direct:
        sql_name = data.execute(f"select username from gg where image_name='{file_name}'")
        for username in sql_name:
            check_for_face =check_file(file_name)

            if check_for_face==True:
                img_encoded = image_initialicer(file_name)
                simler_name_face.append(username[0])
                simler_encoding_face.append(img_encoded)

        #img_name = file_name.split(".")[0]
    process = True
    while True:
        wanted_name=[]
        wanted_id=[]
        term = data.execute("select id,info from gg")
        for id,ter in term:
            if ter=="Wanted":
                wanted_id.append(id)
        for w_id in wanted_id:
            sql = f"select username from gg where id='{w_id}'"
            execute = data.execute(sql)
            for i in execute:
                wanted_name.append(i[0])
        bolleean , frame = capture_vedio.read()
        if bolleean =="False":
            print ("somthing went wrong")
            continue
        try:
            smaller_frame = cv2.resize(frame , (0,0) , fx=0.25 , fy=0.25)
        except Exception as e:
            continue
        rgb_frame = smaller_frame[ : , :, ::-1]

        if process :
            face_location = face_recognition.face_locations(rgb_frame)
            face_encoding = face_recognition.face_encodings(rgb_frame , face_location)

            face_names = []
            for face_encod in face_encoding :
                matches = face_recognition.compare_faces(simler_encoding_face , face_encod)
                name = "None"

                face_distance = face_recognition.face_distance(simler_encoding_face , face_encod)
                print (face_distance)
                best_matches_index = np.argmin(face_distance)
                if matches[best_matches_index]:
                    name = simler_name_face[best_matches_index]

                face_names.append(name)

        #process = not process

        for (top, right, bottom, left) , name in zip(face_location , face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            if not any(name in i for i in wanted_name):
                cv2.rectangle(frame , (left,top) , (right,bottom) , (0,255,0) , 2)
                cv2.rectangle(frame, (left, bottom - 35), ( right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame ,name ,(left + 3 , bottom - 8 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (0,255,0) , 2)
            else :
                cv2.rectangle(frame , (left,top) , (right,bottom) , (0,0,255) , 2)
                cv2.rectangle(frame, (left, bottom - 35), ( right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame ,name ,(left + 3 , bottom - 8 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (0,0,0) , 1)

        ret , buffer = cv2.imencode('.jpg',frame)
        frame = buffer.tobytes()
        for name in face_names:
            print(name)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



def qr_code_reader():
    count_frame = 0
    capture = cv2.VideoCapture(0)

    while True:
        bol , img = capture.read()
        barcodes = pyzbar.decode(img)
        for barcode in barcodes:
            x,y,w,h = barcode.rect
            bar_text = barcode.data.decode('utf-8')
            cv2.rectangle(img , (x,y) , ( x+w , y+h ) , (0,250,0) , cv2.FILLED)
            count_frame +=1
            if count_frame == 5 :
                time_start = time.time()
                time.sleep(1)
                end_time = time.time()
                print (round(end_time - time_start))
                for key in bar_text.splitlines():
                    if key[:3] == "co:":
                        print (key[3:])
                        code = key[3:]
                    if key[:3] == "un:":
                        print (key[3:])
                        username = key[3:]
                    if key[:3] == "em:":
                        print (key[3:])
                        email = key[3:]
                    if key[:3] == "ph:":
                        print (key[3:])
                        phone = key[3:]
                    if key[:3] == "ag:":
                        print (key[3:])
                        age = key[3:]
                    if key[:3] == "in:":
                        print (key[3:])
                        info = key[3:]
                #take_shot = frame[y-54:y+h+84 , x-100:x+w+84]
                #saving = cv2.imwrite("gg.jpg" , take_shot)
                time.sleep(2)
                print (round(time.time() - time_start))
        ret , buffer = cv2.imencode('.jpg',img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@app.route("/qr_code" , methods=['GET' , 'POST'])
def qr_code_template():
    func = request.form.get("submit")
    if func == "start":
        return render_template("qr_code.html" , founction = "start")
    return render_template("qr_code.html")


@app.route("/camera" , methods=['GET' , 'POST'])
def camera():
    func = request.form.get("submit")
    if func == "start":
        return render_template("camera.html" , founction = "start")
    return render_template("camera.html")

def generate_frames():
    capture = cv2.VideoCapture(-1)
    while True:
        bollean , frame = capture.read()
        ret , buffer = cv2.imencode('.jpg',frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/qr_codeer")
def qr_codeer():
    return Response(qr_code_reader(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return  Response(facial_recignation(),mimetype='multipart/x-mixed-replace; boundary=frame')







if __name__ == "__main__":
    app.run(debug=True)
