import cv2
from datetime import datetime
import signal
import pandas

first_frame = None
# status for each of the frame (None value is a trick to work [-2] at the first time)
status_list = [None, None]
# for storing enter time and exist time of a object
times = []
df = pandas.DataFrame(columns=['Start', 'End'])
video = cv2.VideoCapture(0)

# temp code haldling ctrl + c
#############################################


def sigint_handler(signum, frame):
    print('Stop pressing the CTRL+C!')
    # if programm terminate without object exists
    if status == 1:
        times.append(datetime.now())

    print(status_list)
    print(times)

    for i in range(0, len(times), 2):
        global df
        df = df.append({"Start": times[i], "End": times[i + 1]}, ignore_index=True)

    df.to_csv("Times.csv")
    # release camera
    video.release()

    # close all windows
    cv2.destroyAllWindows()


signal.signal(signal.SIGINT, sigint_handler)
###############################################
# end here

while True:
    global status
    check, frame = video.read()                                                 # frame0 : Raw
    status = 0  # for time recording

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                              # frame1 : Gray
    gray = cv2.GaussianBlur(gray, (21, 21), 0)                                  # frame2 : Blur

    # only be true in the first iteration
    if first_frame is None:
        first_frame = gray
        continue  # we only want the first frame so we need to capture another frame/image by going to the next iteration

    delta_frame = cv2.absdiff(first_frame, gray)                                # frame3 : Delta
    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]    # frame4 : Threshold , threshold value = 30 if pixel>30 assgn value of 255, which is white)
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)                 # frame5 : Dilation

    # find contours store in cnts
    (_, cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue  # go and check the next contour without drawing it
        status = 1
        (x, y, w, h) = cv2.boundingRect(contour)  # create rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # draw it on the color frame

    status_list.append(status)

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())   # record object enter time 0 ---> 1

    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())   # record object exit time 1 ---> 0

    cv2.imshow("Threshold Frame", frame)

    key = cv2.waitKey(1) & 0xFF  # wait for 1 ms
    print(key)

    if key == ord('q'):         # if user press q terminate
        break
    elif key != 255:
        print('key:', [chr(key)])
