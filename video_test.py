from deepface import DeepFace
import cv2, time, os
from PIL import Image
import matplotlib.pyplot as plt

video_path = "example.mov"
video_capture = cv2.VideoCapture(video_path)

face_detection_backends = [
	'opencv',
	'ssd',
	'mtcnn',
	'retinaface',
]
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
emotion_value_dict = {"angry": -3, "disgust": -2, "fear": -4, "sad": -1, "neutral": 0, "surprise": 1, "happy": 2}

backend_emo_dict = {backend: [] for backend in face_detection_backends}

# Read and process each frame until the end of the video
while True:
	# skip 10 frames
	num_frames_to_discard = 10
	for _ in range(num_frames_to_discard):
		ret, _ = video_capture.read()
		if not ret:
			break
	# Read the next frame from the video
	ret, frame = video_capture.read()
	# If there are no more frames, break the loop
	if not ret:
		break
	for backend in face_detection_backends:
		data = DeepFace.analyze(frame, actions=("emotion",), detector_backend=backend, enforce_detection=False)
		backend_emo_dict[backend].append(data[0]["dominant_emotion"])

video_capture.release()

backend_emoValue_dict = {backend: [] for backend in face_detection_backends}
for backend in backend_emo_dict:
	backend_emoValue_dict[backend] = [emotion_value_dict[emo] for emo in backend_emo_dict[backend]]

# plot
x_values = list(range(1, len(backend_emoValue_dict["mtcnn"]) + 1))
for backend in backend_emoValue_dict:
	plt.plot(x_values, backend_emoValue_dict[backend], label=backend)
# Add labels and title
plt.xlabel("frames")
plt.ylabel("emotion value")
plt.title("backend emotion detection eval")
# Add legend
plt.legend()
plt.savefig("backend_emoDetection_eval.png")
