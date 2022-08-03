# imports
from picamera.array import PiRGBArray # to make an iterable of video
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
camera.resolution = (800, 800)
camera.rotation = 270
camera.hflip = True

n_frames = 100

time.sleep(1) # warm up


rawCapture = PiRGBArray(camera, size = camera.resolution)
count = 0
fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')

imgs = []
loop_durs = []

start_t_loop = time.time()

for f in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
	start_t = time.time()
	f_raw = f.array
	f_array = f.array # raw numpy
	f_array = cv2.cvtColor(f_array, cv2.COLOR_BGR2GRAY) # we dont care about colors
	f_array = cv2.blur(f_array, (10,10), 0)
	
	if count == 0: # take first frame as background
		avg = f_array.copy().astype('float')
		rawCapture.truncate(0) 
			
	diff = cv2.absdiff(f_array, cv2.convertScaleAbs(avg))
	
	thr = 20 # setting manually

	(threshold, diff_bin) = cv2.threshold(diff.copy(), thr, 255, cv2.THRESH_BINARY)

	contours, hierarchy = cv2.findContours(diff_bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	if len(contours) > 0:
		x, y, w, h = cv2.boundingRect(np.vstack(contours))
		cv2.rectangle(f_raw,(x,y), (x+w, y+h), (0,255,0),2)
		cv2.putText(f_raw, 'Moving object', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

	
	cv2.imshow('Frame', f_raw)
	imgs.append(f_raw)
	cv2.waitKey(1) # time in ms to show the image for (uless a key is pressed)
	
	rawCapture.truncate(0) # stream related
	
	# prepare for running average of next frame
	avg = (avg + f_array) / 2
	f_prev = f_array # for running average
	count += 1
	
	loop_dur = (time.time() - start_t)
	loop_durs.append(loop_dur)
	print('loop_duration: ', loop_dur)
	if count == n_frames:
		break

time_whole_loop = time.time()-start_t_loop
fps_one = 1/np.mean(loop_durs)	
fps_all = n_frames/time_whole_loop

print('FPS based on average loop duration: ', fps_one)
print('FPS based on all loops duration: ', fps_all)


video = cv2.VideoWriter('video.avi', fourcc, fps_all, (camera.resolution[0], camera.resolution[1]))
	
for img in imgs:
	video.write(img)
		
cv2.destroyAllWindows()
video.release()
