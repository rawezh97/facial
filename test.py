import sqlite3
import time
import os




def x():
    x=1
    y=2
    yield x
    yield y
    yield (x+y)

result = list(x())
print (result[0])

































#for insert data to the sqlite_database
#def connection():
#    global connection
#    global data
#    try:
#        connection = sqlite3.connect("database.db")
#        data = connection.cursor()
#        print ("connected")
#    except Exception as e:
#        print ("connection faild")
#        connection()
#
#connection()
#
#
#x = os.listdir("/home/world/Desktop/test_web/static/uploads/")
#i = 1
#for dict in x :
#    i +=1
#    file = open(f"static/uploads/{dict}" , "rb")
#    content = file.read()
#    empty_list = []
#    empty_list.append(i)
#    empty_list.append(str(dict))
#    empty_list.append(content)
#    try:
#        sql = "INSERT INTO gg values(?,?,?)"
#        data.execute(sql,empty_list)
#        connection.commit()
#        time.sleep(3)
#        print ("seccess")
#    except Exception as e:
#        print ("NOT Inserted!")
#        continue
#    #img_name = dict.split(".")[0]
#    #simler_name_face.append(img_name)
#    #g = image_initialicer(dict)
#    #simler_encoding_face.append(g)
#
