from pyzbar import pyzbar
import sqlite3
import cv2
import time

count_frame = 0
#connection = sqlite3.connect("text.dbs")
#data = connection.cursor()

#sql = "create table test (id integer , text String(50));"
#data.execute(sql)
#connection.commit()


capture = cv2.VideoCapture(0)

def read_barcode(frame):
    global count_frame
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
            x,y,w,h = barcode.rect
            bar_text = barcode.data.decode('utf-8')

            cv2.rectangle(frame , (x,y) , ( x+w , y+h ) , (0,250,0) , cv2.FILLED ,4)
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
                exit()
            #sql = f"INSERT INTO test values(1,'{bar_text}')"
            #data.execute(sql)
            #connection.commit()

    return frame



while True:
    bol , img = capture.read()
    frame = read_barcode(img)

    cv2.imshow("frame" , frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
capture.release()
cv2.destroyAllWindows()
