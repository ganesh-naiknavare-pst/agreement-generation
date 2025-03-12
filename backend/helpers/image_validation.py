import face_recognition
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

def detect_faces(image_path):
    """Detect the number of faces in an image using face_recognition."""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return len(face_locations)

def extract_face_encoding(image_path):
    """Extract facial encoding from an image using face_recognition."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None

def are_faces_different(image_paths, threshold=0.5):
    """Checks if images contain different people."""
    encodings = []

    for path in image_paths:
        encoding = extract_face_encoding(path)
        if encoding is None:
            return False, "Invalid Image: No face detected"
        encodings.append(encoding)
    for i in range(len(encodings)):
        for j in range(i + 1, len(encodings)):
            distance = np.linalg.norm(encodings[i] - encodings[j])
            if distance < threshold:
                return False, "Invalid Image: Duplicate face detected"
    
    return True, "Valid Image"

def validate_uploaded_image(image_path):
    """Validate image based on face count and uniqueness."""
    num_faces = detect_faces(image_path)

    if num_faces == 0:
        return False, "Invalid Image: No face detected."
    elif num_faces > 1:
        return False, "Invalid Image: More than one person detected."
    
    return True, "Valid Image"
