import cv2
import os
import time

# Read the video from specified path
cap = cv2.VideoCapture(r"C:\TMP\_20210313.ts")

try:

    # creating a folder named data
    if not os.path.exists('data'):
        os.makedirs('data')

    # if not created then raise error
except OSError:
    print('Error: Creating directory of data')


#Set frame_no in range 0.0-1.0
#In this example we have a video of 30 seconds having 25 frames per seconds, thus we have 750 frames.
#The examined frame must get a value from 0 to 749.
#For more info about the video flags see here: /questions/124405/setting-camera-parameters-in-opencvpython
#Here we select the last frame as frame sequence=749. In case you want to select other frame change value 749.
#BE CAREFUL! Each video has different time length and frame rate.
#So make sure that you have the right parameters for the right video!
time_length = 3600.0
fps=3
frame_seq = fps*time_length - 1
frame_no = (frame_seq /(time_length*fps))

#The first argument of cap.set(), number 2 defines that parameter for setting the frame selection.
#Number 2 defines flag CV_CAP_PROP_POS_FRAMES which is a 0-based index of the frame to be decoded/captured next.
#The second argument defines the frame number in range 0.0-1.0
cap.set(2,frame_no);

#Read the next frame from the video. If you set frame 749 above then the code will return the last frame.
ret, frame = cap.read()

#Set grayscale colorspace for the frame.
#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


#Display the resulting frame
#cv2.imshow('my_video_name'+' frame '+ str(frame_seq),gray)

#Set waitKey
#cv2.waitKey()

#Store this frame to an image
cv2.imwrite('my_video_name'+'_frame_'+str(frame_seq)+'.jpg',frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()













# # frame
# currentframe = 0
#
# while (True):
#     time.sleep(5) # take schreenshot every 5 seconds
#     # reading from frame
#     ret, frame = cam.read()
#
#     if ret:
#         # if video is still left continue creating images
#         name = './data/frame' + str(currentframe) + '.jpg'
#         print('Creating...' + name)
#         print(type(frame))
#         # writing the extracted images
#         cv2.imwrite(name, frame)
#
#         # increasing counter so that it will
#         # show how many frames are created
#         currentframe += 1
#     else:
#         break
#
# # Release all space and windows once done
# cam.release()
# cv2.destroyAllWindows()