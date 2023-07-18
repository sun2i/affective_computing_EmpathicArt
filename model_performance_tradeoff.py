from deepface import DeepFace
import cv2, time,os
from PIL import Image

"""
This script test the accuracy and runtime of different backend provided by deepface:  
  'opencv',
  'ssd',
  'mtcnn',
  'retinaface'

Results:
mtcnn has overall shorter runtime, and good performance
opencv takes the shortest runtime
retinaface takes the longest runtime, the recall is not high enough

'happy' emotion has the highest recall,
negative emotion like 'disgust'/ 'angry' has low recall
  
"""

video_capture = cv2.VideoCapture(0)
# Discard the first 10 frames after opened the camera
num_frames_to_discard = 10
for _ in range(num_frames_to_discard):
    _, _ = video_capture.read()
# Capture frame-by-frame
ret, frame = video_capture.read()
video_capture.release()
# Perform facial emotion analysis
# result = DeepFace.analyze(frame, actions=("emotion",), enforce_detection=False )

# save current frame and all its test result in one subdirectory
timestamp = time.time()
subdirectory = "backend_eval" +os.sep+ str(timestamp)
if not os.path.exists(subdirectory):
    os.makedirs(subdirectory)
# Convert color channel ordering from BGR to RGB
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame_image = Image.fromarray(frame)
frame_image.save(subdirectory+os.sep+"original_frame.jpg")

# test combination between face detection model backend and attribute analysis backend
face_detection_backends = [
  'opencv',
  'ssd',
  'mtcnn',
  'retinaface',
]
for fd_backend in face_detection_backends:
    start_time = time.time()
    # facial analysis
    data = DeepFace.analyze(frame,actions=("emotion",),detector_backend=fd_backend)
    end_time = time.time()
    execution_time = end_time - start_time
    # Get the emotions and their values
    emotionsData = data[0]['emotion']
    dominant_emotion = data[0]["dominant_emotion"]
    log_outpath = subdirectory +os.sep+"logfile.txt"
    # if not os.path.exists(log_outpath):
    #     os.makedirs(log_outpath)
    with open(log_outpath, 'a') as log_file:
        # Write text to the log file
        log_file.write(f"{fd_backend} runntime: {execution_time}. Dominant Emotion: {dominant_emotion} GOT following emotion data: \n{emotionsData}\n\n")



