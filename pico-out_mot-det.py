### imports
from picamera.array import PiRGBArray # to make an iterable of video
from picamera import PiCamera
import time
import cv2
import numpy as np

### defining functions
import RPi.GPIO as GPIO

# helper for movement detection
def get_avg(f_bw, avg):
	if avg is None: # take first frame as background
		avg = f_bw.copy().astype('float')
		rawCapture.truncate(0) 
	else:
		avg = (avg + f_bw) / 2
	return avg

# movement detection function
def get_contours_avg(f_raw, avg):

	f_bw = cv2.cvtColor(f_raw.copy(), cv2.COLOR_BGR2GRAY) # we dont care about colors
	f_bw = cv2.blur(f_bw, (10,10), 0)
	
	avg = get_avg(f_bw, avg)		
	diff = cv2.absdiff(f_bw, cv2.convertScaleAbs(avg))
	
	thr = 20 # setting manually

	(_, diff_bin) = cv2.threshold(diff.copy(), thr, 255, cv2.THRESH_BINARY)

	contours, _ = cv2.findContours(diff_bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	return contours, avg

# draw contours to image and display in stream
def show_vid_contours(f_raw, contours):
	if len(contours) > 0:
		x, y, w, h = cv2.boundingRect(np.vstack(contours))
		cv2.rectangle(f_raw,(x,y), (x+w, y+h), (0,255,0),2)
		cv2.putText(f_raw, 'Moving object', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		print('1 - (object detected)')
	else:
		print('0 - (no object detected)')
	
	cv2.imshow('Frame', f_raw)
	cv2.waitKey(1) # time in ms to show the image for (uless a key is pressed)

	return f_raw

# GPIO setup
def setup(out_pin):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(out_pin, GPIO.OUT)
	GPIO.output(out_pin, False)
	print(f'using pin index: {out_pin}')


### start of script

# initialising camera
camera = PiCamera()
camera.resolution = (512,512)
camera.rotation = 0
camera.hflip = False
n_frames = 10000
time.sleep(1) # warm up

# initialising GPIO
out_pin = 17
setup(out_pin)

# preparing saving objects
rawCapture = PiRGBArray(camera, size = camera.resolution)
fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')
imgs = []

# preparing timing (to get frame rates etc.)
loop_durs = []
start_t_loop = time.time()

# running main loop
avg = None # to handle first frame
count = 0

for f in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
	start_t = time.time()
	f_raw = f.array

	# computing
	contours, avg = get_contours_avg(f_raw, avg)

	#outputting via pin
	out_bool = len(contours) > 0 # defining output if contours are detected
	GPIO.output(out_pin, out_bool)

	# displaying
	f_raw_contours = show_vid_contours(f_raw, contours)
	imgs.append(f_raw_contours)

	rawCapture.truncate(0) # stream related

	# computing loop durations to get frame rate
	loop_dur = (time.time() - start_t)
	loop_durs.append(loop_dur)

	count += 1
	if count == n_frames:
		break

# getting frame rate
time_whole_loop = time.time()-start_t_loop
fps_one = 1/np.mean(loop_durs)	
fps_all = n_frames/time_whole_loop

print('FPS based on average loop duration: ', fps_one)
print('FPS based on all loops duration: ', fps_all)
print('There\'s a discrepancy...')

# saving video
video = cv2.VideoWriter('video.avi', fourcc, fps_all, (camera.resolution[0], camera.resolution[1]))
	
for img in imgs:
	video.write(img)
		
cv2.destroyAllWindows()
video.release()