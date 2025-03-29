import os
import cv2
import numpy as np
import face_recognition
from collections import Counter
import time

class FaceIdentifier:
    def __init__(self, known_faces_folder='known_faces'):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_faces_folder = known_faces_folder
        self.load_known_faces()

    def load_known_faces(self):
        # Load known faces from the folder
        for filename in os.listdir(self.known_faces_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(self.known_faces_folder, filename)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)
                
                if len(encoding) > 0:
                    self.known_face_encodings.append(encoding[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])
                else:
                    print(f"No face found in {filename}")

        print(f"Loaded {len(self.known_face_names)} known faces")

    def run_recognition(self):
        """Runs face recognition for 10 seconds and returns the most frequent match"""
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()
        detected_names = []

        while time.time() - start_time < 10:  # Run for 10 seconds
            ret, frame = video_capture.read()
            if not ret:
                break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all faces in current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    detected_names.append(name)

                # Draw bounding box and label
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Face Identification', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

        # Return the most common detected name
        if detected_names:
            return Counter(detected_names).most_common(1)[0][0]
        return "Unknown"