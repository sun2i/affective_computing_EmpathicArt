from deepface import DeepFace
import cv2
import mido
import time
import os

from mido import MidiFile, MidiTrack, Message, MetaMessage
from pythonosc import udp_client, osc_message, osc_message_builder
import random

from mido import MidiFile, MidiTrack, Message, MetaMessage

client = udp_client.SimpleUDPClient('192.168.2.107', 7000)

# Midi setup
midi_messages = []




# Define chord progressions for each emotion
chord_progressions = {
    'happy': ['Cmaj'],
    'neutral': ['Dmaj'],
    'surprise': ['Emij'],
    'sad': ['Fmaj'],
    'angry': ['Gmaj'],
    'disgust': ['Amaj'],
    'fear': ['Hmaj'],
}

# Helper function to convert note names to MIDI note numbers


def note_name_to_number(note_name):
    note_names = ['C', 'C#', 'D', 'D#', 'E',
                  'F', 'F#', 'G', 'G#', 'A', 'B', 'H']
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
#port2 = mido.open_output()


def send_modulation(value):
    channel = 0  # Channel number (0-15)
    controller = 1  # Controller number for Modulation MSB
    message = mido.Message('control_change', channel=channel, control=controller, value = value)
    virtual_port.send(message)

def send_chord(port, notes, velocity=64, channel=1):
    global midi_messages
    for note in notes:
        note_on = mido.Message('note_on', note=note,
                               velocity=velocity, channel=channel)
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
        chord_notes = [note_number]
    
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
    lastplayed = emotion
    # Save the MIDI file
    print("Chords played succesfully")


video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Cannot open camera")
    exit()

virtual_port = open_virtual_midi_port('My Virtual Port')

def send_osc_message(address, value):
    osc_msg = osc_message_builder.OscMessageBuilder(address=address)
    osc_msg.add_arg(value)
    try:
        client.send(osc_msg.build())
    except Exception as e:
        print(f"Error sending OSC message: {e}")

def send_all_osc_data(data):
    # Get the emotions and their values
    emotionsData = data['emotion']

    # Sort the emotions by their values in descending order
    sorted_emotions = sorted(emotionsData.items(), key=lambda x: x[1], reverse=True)

    # Iterate over the emotions and their values
    for emotion, value in sorted_emotions:
        osc_address = f"/emotion/{emotion}"
        send_osc_message(osc_address, value)


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

    # Send emotion osc
    send_all_osc_data(data)

    # Use the averaged emotions for playing chords
    play_chords()

    # time.sleep(4)

    # Break the loop if 'q' is pressed


# Release the video capture and close the window
video_capture.release()
cv2.destroyAllWindows()
virtual_port.close()
sock.close()
# save_midi_file(output_path)
