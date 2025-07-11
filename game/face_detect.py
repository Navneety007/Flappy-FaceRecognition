import cv2
import numpy as np
import os

class FaceDetector:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open video stream for camera index {camera_index}")
            self.cap = None
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        xml_path = os.path.join(base_dir, 'haar_face.xml')
        
        self.haar_cascade = cv2.CascadeClassifier(xml_path)
        if self.haar_cascade.empty():
            print(f"Error: Could not load face cascade from {xml_path}")

    def get_frame_and_face_y(self, game_height):
        if self.cap is None or not self.cap.isOpened():
            return None, None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None

        frame = cv2.flip(frame, 1)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.haar_cascade.empty():
            return frame, None, None

        # Use even more lenient parameters to detect faces more easily
        faces_rect = self.haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
        
        if len(faces_rect) > 0:
            # Find the face with the largest area
            largest_face = max(faces_rect, key=lambda rect: rect[2] * rect[3])
            (x, y, w, h) = largest_face
            face_center_y = y + h // 2
            
            frame_height = frame.shape[0]
            game_y = np.interp(face_center_y, [0, frame_height], [0, game_height])
            return frame, int(game_y), largest_face
            
        return frame, None, None

    def release(self):
        if self.cap is not None:
            self.cap.release()