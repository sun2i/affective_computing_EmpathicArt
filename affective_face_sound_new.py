from deepface import DeepFace
import cv2
import mido
import time
import os

from mido import MidiFile, MidiTrack, Message, MetaMessage
from pythonosc import udp_client, osc_message, osc_message_builder

client = udp_client.SimpleUDPClient('192.168.2.107', 7000)

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

    # Get the dominant emotion
    emotion = result[0]["dominant_emotion"]
    emotion_message = f"/emotion {emotion}"
    emotions = [emotion]

    # Display the emotion on the frame
    cv2.putText(frame, emotion, (10, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    print(result[0])

    data = result[0]

    # Display the resulting frame
    cv2.imshow('Real-Time Emotion Analysis', frame)

    # Send emotion osc
    send_all_osc_data(data)

    play_chords()
    time.sleep(2)

# Release the video capture and close the window
video_capture.release()
cv2.destroyAllWindows()
virtual_port.close()
sock.close()
# save_midi_file(output_path)
