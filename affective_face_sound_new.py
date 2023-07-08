from deepface import DeepFace
import cv2
import mido
import time
import os
import socket

from mido import MidiFile, MidiTrack, Message, MetaMessage
from PIL import Image, ImageDraw

# Set the file name and path
file_name = "emotion_gradient_image.png"
file_path = os.path.join(os.getcwd(), file_name)


def create_image(start_color, end_color):
    # Check if the file already exists
    if os.path.exists(file_path):
        # Rename the existing file
        new_file_name = "new_emotion_gradient_old.png"
        new_file_path = os.path.join(os.getcwd(), new_file_name)
        os.rename(file_path, new_file_path)
        print(f"Renamed existing file: {file_name} to {new_file_name}")

    # Set the size of the image
    width = 500
    height = 500

    # Create a new image with the specified size
    image = Image.new("RGB", (width, height))

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Generate the gradient
    for y in range(height):
        # Calculate the interpolated color for the current row
        r = int(start_color[0] + (end_color[0] - start_color[0]) * y / height)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * y / height)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * y / height)
        color = (r, g, b)

        # Draw a horizontal line with the interpolated color
        draw.line([(0, y), (width, y)], fill=color)

    # Save the image to your computer
    image.save(file_path)
    print(f"Saved new file: {file_name}")


def map_colors(emotion, value):
    value = 1
    if emotion == 'happy':
        return (255*value, 200*value, 0)
    elif emotion == 'neutral':
        return (255*value, 255*value, 130*value)
    elif emotion == 'sad':
        return (0, 0, 255*value)
    elif emotion == 'surprise':
        return (90*value, 160*value, 255*value)
    elif emotion == 'angry':
        return (200*value, 0, 50*value)
    elif emotion == 'disgust':
        return (140*value, 0, 160*value)
    elif emotion == 'fear':
        return (0, 180*value, 90*value)


# Midi setup
midi_messages = []

# Define chord progressions for each emotion
chord_progressions = {
    'happy': ['Cmaj', 'Cmaj','Cmaj'],
    'neutral': ['Fma7', 'Fma7','Fma7'],
    'sad': ['Dmi7', 'Dmi7','Dmi7'],
    'surprise': ['Ema7', 'Ema7','Ema7'],
    'angry': ['Gma7', 'Gma7','Gma7'],
    'disgust': ['Cmi7', 'Cmi7','Cmi7'],
    'fear': ['Fmi7', 'Fmi7','Fmi7']
    
}

# Helper function to convert note names to MIDI note numbers
def note_name_to_number(note_name):
    note_names = ['C', 'C#', 'D', 'D#', 'E','F', 'F#', 'G', 'G#', 'A', 'B', 'H']
    note_number = note_names.index(note_name.upper())
    return note_number


def open_virtual_midi_port(port_name):
    try:
        port = mido.open_output(port_name, virtual=True)
        print(f"Opened virtual MIDI port: {port_name}")
        return port
    except OSError:
        print(f"Failed to open virtual MIDI port: {port_name}")
        return None


def send_chord(port, notes, velocity=64, channel=1):
    global midi_messages
    for note in notes:
        note_on = mido.Message('note_on', note=note,velocity=velocity, channel=channel)
        port.send(note_on)
        midi_messages.append(note_on)
    time.sleep(1)  # Play the chord for 1 second
    for note in notes:
        note_off = mido.Message('note_off', note=note, channel=channel)
        port.send(note_off)
        midi_messages.append(note_off)


def save_midi_file(output_path):
    # Create a new MIDI file and track
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Add the MIDI messages to the track
    for message in midi_messages:
        track.append(message)

    # Save the MIDI file
    filename = os.path.join(output_path, 'output_new.mid')
    mid.save(filename)
    print(f"MIDI file saved: {filename}")

# Helper function to convert chord names to MIDI note numbers
def chord_name_to_notes(chord_name):
    root_note = chord_name[:-3]
    chord_type = chord_name[-3:]

    note_number = note_name_to_number(root_note)

    if chord_type == 'maj':
        note_number += 60
        chord_notes = [note_number, note_number + 4, note_number + 7]
    elif chord_type == 'min':
        note_number += 60
        chord_notes = [note_number, note_number + 3, note_number + 7]
    elif chord_type == 'dim':
        note_number += 60
        chord_notes = [note_number, note_number + 3, note_number + 6]
    elif chord_type == 'aug':
        note_number += 60
        chord_notes = [note_number, note_number + 4, note_number + 8]
    elif chord_type == 'mi7':
        note_number += 60
        chord_notes = [note_number, note_number +3, note_number + 7, note_number + 10]
    elif chord_type == 'ma7':
        note_number += 60
        chord_notes = [note_number, note_number + 4, note_number + 7, note_number + 11]
    else:
        chord_notes = [note_number]

    return chord_notes


def play_chords():
    # Generate chords based on emotions
    for emotion in emotions:
        progression = chord_progressions.get(emotion, [])

        for chord_name in progression:
            # Create MIDI messages for the chord
            chord_notes = chord_name_to_notes(chord_name)
            send_chord(virtual_port, chord_notes)

    # Save the MIDI file
    print("Chords played succesfully")


video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Cannot open camera")
    exit()

virtual_port = open_virtual_midi_port('My Virtual Port')


def draw_emotion_gradient(data):

    # Get the emotions and their values
    emotionsData = data['emotion']

    # Sort the emotions by their values in descending order
    sorted_emotions = sorted(emotionsData.items(),key=lambda x: x[1], reverse=True)

    # Get the top two emotions with the highest values
    top_emotions = sorted_emotions[:2]

    # Access the first emotion and its value separately
    first_emotion = top_emotions[0]
    first_emotion_name = first_emotion[0]
    first_emotion_value = first_emotion[1]

    # Access the second emotion and its value separately
    second_emotion = top_emotions[1]
    second_emotion_name = second_emotion[0]
    second_emotion_value = second_emotion[1]

    first_color = map_colors(first_emotion_name, first_emotion_value)
    second_color = map_colors(second_emotion_name, second_emotion_value)

    create_image(first_color, second_color)

# Create a list to store the last five emotion data records
emotion_data_records = []

import random

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Perform facial emotion analysis
    result = DeepFace.analyze(frame, actions=("emotion", "age"), enforce_detection=False)

    # Add the current emotion data to the list of records
    emotion_data_records.append(result[0]['emotion'])

    # If there are more than 5 records, remove the oldest one
    if len(emotion_data_records) > 5:
        emotion_data_records.pop(0)

    # Compute the average percentage of each emotion over the last five seconds
    average_emotions = {}
    for record in emotion_data_records:
        for emotion, value in record.items():
            if emotion not in average_emotions:
                average_emotions[emotion] = value
            else:
                average_emotions[emotion] += value

    for emotion in average_emotions.keys():
        average_emotions[emotion] /= len(emotion_data_records)

    print("Average emotion")
    print(average_emotions)

    # Replace the current emotion data with the averaged data
    data = result[0]
    data['emotion'] = average_emotions

    # Sort the averaged emotions
    sorted_emotions = sorted(average_emotions.items(), key=lambda x: x[1], reverse=True)
    
    # Check if neutral is the dominant emotion
    if sorted_emotions[0][0] == 'neutral':
        # 25% chance to keep neutral as dominant emotion
        if random.random() < 0.25:
            dominant_emotion = 'neutral'
        else:
            sorted_emotions = [e for e in sorted_emotions if e[0] != 'neutral']
            dominant_emotion = sorted_emotions[0][0] if sorted_emotions else 'neutral'
    else:
        dominant_emotion = sorted_emotions[0][0]

    emotion_message = f"/emotion {dominant_emotion}"
    emotions = [dominant_emotion]

    # Display the emotion on the frame
    cv2.putText(frame, dominant_emotion, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    print(result[0])

    print("New emotions")
    print(data)

    # Display the resulting frame
    cv2.imshow('Real-Time Emotion Analysis', frame)

    # Draw emotions gradient
    draw_emotion_gradient(data)

    # Use the averaged emotions for playing chords
    play_chords()

    time.sleep(1)


# Release the video capture and close the window
video_capture.release()
cv2.destroyAllWindows()
virtual_port.close()
sock.close()
# save_midi_file(output_path)
