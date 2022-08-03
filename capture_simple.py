from picamera import PiCamera
import time

# take a picture
camera = PiCamera()
camera.start_preview()
time.sleep(2)

camera.capture('first_photo.jpg')

# take a video
camera.start_recording('first_video.h264')
time.sleep(20)
camera.stop_recording()
 
