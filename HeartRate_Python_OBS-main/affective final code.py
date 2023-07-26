from deepface import DeepFace
import cv2
import mido
import time
import os
from mido import MidiFile, MidiTrack
from pythonosc import udp_client, osc_message, osc_message_builder
import random
import asyncio
import json
import websockets


# Global variables to store the current heartbeat value and time of the polar-device
current_hr_bpm = 70
current_time = None

# Background task for receiving heartbeat from websockets server
async def connect_and_fetch_data():
    global current_hr_bpm
    global current_time
    async with websockets.connect('ws://[2a02:3033:608:9785:3fff:cc38:f41e:d205]:8919/ws/hr_json') as ws:
        try:
            message = await ws.recv()
            data = json.loads(message)
            current_hr_bpm = data.get('hr')
            current_time = data.get('time')

        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"Error: {str(e)}")


async def main():
    
    client = udp_client.SimpleUDPClient('172.20.10.2', 7000)
    midi_messages = []
    emotion_data_records = []
    training_started = 0  # Variable to track training status



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
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'B', 'H']
        note_number = note_names.index(note_name.upper())
        return note_number

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

    # Open virtual MIDI port
    def open_virtual_midi_port(port_name):
        try:
            port = mido.open_output(port_name, virtual=True)
            print(f"Opened virtual MIDI port: {port_name}")
            return port
        except OSError:
            print(f"Failed to open virtual MIDI port: {port_name}")
            return None

    # Send modulation MIDI message
    def send_modulation(value):
        channel = 0  # Channel number (0-15)
        controller = 1  # Controller number for Modulation MSB
        message = mido.Message('control_change', channel=channel, control=controller, value=value)
        virtual_port.send(message)

    # Send chord as MIDI messages
    def send_chord(port, notes, velocity=64, channel=1):
        global midi_messages
        for note in notes:
            note_on = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
            port.send(note_on)
            midi_messages.append(note_on)
        time.sleep(1)  # Play the chord for 1 second
        for note in notes:
            note_off = mido.Message('note_off', note=note, channel=channel)
            port.send(note_off)
            midi_messages.append(note_off)

    # Save MIDI messages to a MIDI file
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

    # Send OSC message
    def send_osc_message(address, value):
        osc_msg = osc_message_builder.OscMessageBuilder(address=address)
        osc_msg.add_arg(value)
        try:
            client.send(osc_msg.build())
        except Exception as e:
            print(f"Error sending OSC message: {e}")

    # Send OSC data for all emotions
    def send_all_osc_data(data):
        emotionsData = data['emotion']  # Get the emotions and their values
        sorted_emotions = sorted(emotionsData.items(), key=lambda x: x[1], reverse=True)  # Sort emotions by values

        # Iterate over the emotions and their values
        for emotion, value in sorted_emotions:
            osc_address = f"/emotion/{emotion}"
            send_osc_message(osc_address, value)

    # Play chords based on emotions
    def play_chords():
        for emotion in emotions:
            progression = chord_progressions.get(emotion, [])
            for chord_name in progression:
                # Create MIDI messages for the chord
                chord_notes = chord_name_to_notes(chord_name)
                send_chord(virtual_port, chord_notes)
        lastplayed = emotion
        print("Chords played successfully")

    # Initialize video capture
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Cannot open camera")
        exit()

    # Open virtual MIDI port
    virtual_port = open_virtual_midi_port('My Virtual Port')

    while True:
        #receive heart rate
        await connect_and_fetch_data()
        print("Current heartbeat:", current_hr_bpm, "at:", current_time)
        
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Perform facial emotion analysis
        result = DeepFace.analyze(frame, actions=("emotion", "age"), enforce_detection=False)
        emotion = result[0]["dominant_emotion"]  # Get the dominant emotion
        emotion_message = f"/emotion {emotion}"
        emotions = [emotion]

        # Display the emotion on the frame
        cv2.putText(frame, emotion, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print(result[0])

        data = result[0]

        # Display the resulting frame
        cv2.imshow('Real-Time Emotion Analysis', frame)

        # Send emotion OSC and heart rate OSC
        send_all_osc_data(data)
        #heart_rate = random.randint(0, 127)
        send_osc_message(f"/heart_rate", current_hr_bpm)
        send_osc_message(f"/started", training_started)


        # Use the averaged emotions for playing chords
        send_modulation(current_hr_bpm)
        play_chords()

        time.sleep(3)  # Wait for 1 seconds

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):  # 'r' key is pressed to start training
            training_started = 1
        elif key == ord('f'):  # 'f' key is pressed to stop training
            training_started = 0

        # Break the loop if 'q' is pressed
        if key == ord('q'):
                break

    # Release the video capture and close the window
    video_capture.release()
    cv2.destroyAllWindows()
    virtual_port.close()


if __name__ == "__main__":
    asyncio.run(main())