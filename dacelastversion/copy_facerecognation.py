import face_recognition
import numpy as np
import time
import sqlite3
import cv2
import os
import requests



def connection():
    global connection
    global data
    try:
        connection = sqlite3.connect("dbs.db")
        data = connection.cursor()
    except Exception as e:
        print ("connection faild")
        connection()

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

connection()
capture_vedio = cv2.VideoCapture(0)

simler_encoding_face = []
simler_name_face = []
face_location = []
face_encoding = []

#print (wanted_id)
#print (wanted_name)
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

#for insert data to the sqlite_database
'''
x = os.listdir("/home/world/Desktop/dace_recognation/images/")
last_id = "SELECT MAX(id) FROM gg"
id = data.execute(last_id)
for i in id:
    count = int(i[0])
    print (count +1)

for dict in x :
    count +=1
    print (count)
    file = open(f"images/{dict}" , "rb")
    content = file.read()
    empty_list = []
    empty_list.append(count)
    empty_list.append(str(dict))
    empty_list.append(content)
    try:
        sql = "INSERT INTO gg values(?,?,?)"
        data.execute(sql,empty_list)
        connection.commit()
        time.sleep(3)
    except Exception as e:
        print (e)
        continue
    img_name = dict.split(".")[0]
    simler_name_face.append(img_name)
    g = image_initialicer(dict)
    simler_encoding_face.append(g)
'''
info = []
process = True
while True:
    bolleean , frame = capture_vedio.read()
    blank_image = np.zeros(shape=[350, 650, 3], dtype=np.uint8)
    if bolleean =="False":
        print ("somthing went wrong")
        continue
    try:
        smaller_frame = cv2.resize(frame , (0,0) , fx=0.25 , fy=0.25)
    except Exception as e:
        continue
    rgb_frame = smaller_frame[ : , :, ::-1]

    wanted_name=[]
    wanted_id=[]
    term = data.execute("select id,info from gg")
    for id,ter in term:
        #print (id,ter)
        if ter=="Wanted":
            wanted_id.append(id)
    for w_id in wanted_id:
        sql = f"select username from gg where id='{w_id}'"
        execute = data.execute(sql)
        for i in execute:
            wanted_name.append(i[0])

    if process :
        face_location = face_recognition.face_locations(rgb_frame)
        face_encoding = face_recognition.face_encodings(rgb_frame , face_location)

        face_names = []
        for face_encod in face_encoding :
            matches = face_recognition.compare_faces(simler_encoding_face , face_encod)
            name = "None"

            face_distance = face_recognition.face_distance(simler_encoding_face , face_encod)
            best_matches_index = np.argmin(face_distance)
            if matches[best_matches_index]:
                #print (best_matches_index)
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
            #cv2.rectangle(frame, (left, bottom - 35), ( right, bottom), (0, 0, 255), cv2.FILLED)
            #cv2.putText(frame ,name ,(left + 3 , bottom - 8 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (0,255,0) , 2)
        else :
            lqs = f"select username , email , phone , age , info from gg where username='{name}'"
            g_test = data.execute(lqs)
            for i in g_test:
                uname = i[0]
                email = i[1]
                phone = i[2]
                age = i[3]
                inf = i[4]
            u = "name :" + uname
            e = "email :"+ email
            p = "phone :"+phone
            ag = "age :"+ age
            ing = "info :"+inf
            cv2.putText(blank_image ,u ,(29  , 80 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (255,255,255) , 1)
            cv2.putText(blank_image ,e ,(29  , 120), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (255,255,255) , 1)
            cv2.putText(blank_image ,p ,(29  , 180 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (255,255,255) , 1)
            cv2.putText(blank_image ,ag ,(29  , 220 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (255,255,255) , 1)
            cv2.putText(blank_image ,ing ,(29  , 260 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (0,0,255) , 3)
            cv2.rectangle(frame , (left,top) , (right,bottom) , (0,0,255) , 2)
            cv2.rectangle(frame, (left, bottom - 35), ( right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame ,name ,(left + 3 , bottom - 8 ), cv2.FONT_HERSHEY_DUPLEX, 1.0 , (0,0,0) , 1)
            #resp = requests.post('https://textbelt.com/text', {
            #'phone': '07511090582',
            #'message': 'unwanted person detected ',
            #'key': 'textbelt',
            #})
            #print(resp.json())

    cv2.imshow("frame" , frame)
    cv2.imshow("gray" , blank_image)
    #cv2.imshow("resize_frame" , smaller_frame)
    #cv2.imshow("rgb_frame" , rgb_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture_vedio.release()
cv2.destroyAllWindows()
