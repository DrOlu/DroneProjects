# from drone_config import Drone
from facemask_detection import get_facenet_masknet
from facemask_detection import detect_and_predict_mask
from imutils.video import VideoStream
from web_stream import app
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import time
import threading
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template

if __name__ == '__main__':

    app.run(host='0.0.0.0', port='5000', debug=True,
            threaded=True, use_reloader=False)

    faceNet, maskNet, args = get_facenet_masknet()
    # initialize a flask object

    # # Instatiating the Drone and setup operation
    # drone_test = Drone(0, 640, 480, 0, 0, 0, 0, 0)
    # status = drone_test.get_status()
    # drone_test.get_stream()
    # time.sleep(2.0)

    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        # frame = drone_test.get_frame()
        frame = imutils.resize(frame, width=400)

        # detect faces in the frame and determine if they are wearing a
        # face mask or not
        (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet, args)

        # loop over the detected face locations and their corresponding
        # locations
        count = 0
        for (box, pred) in zip(locs, preds):
            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            # determine the class label and color we'll use to draw
            # the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
            print(label)

            # display the label and bounding box rectangle on the output
            # frame
            cv2.putText(frame, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

            # if label.split(':')[0] == 'No Mask':
            #     file_name = './no mask ' + str(count) + '.jpg'
            #     print(file_name)
            #     cv2.imwrite(file_name, frame)
            #     count += 1
            #     time.sleep(2)

        # show the output frame
        cv2.imshow("Frame", frame)
        out_frame = frame.copy()

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
