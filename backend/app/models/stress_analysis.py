import cv2
import numpy as np
# from deepface import DeepFace  # Removed - using custom CNN model instead
import logging
from app.core.config import settings
import base64
from typing import Dict, Tuple, Any, Optional
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.layers import InputLayer
import tensorflow as tf

logger = logging.getLogger(__name__)

# Custom InputLayer for compatibility with older Keras models
class CustomInputLayer(InputLayer):
    def __init__(self, batch_shape=None, input_shape=None, dtype=None, sparse=False, name=None, ragged=False, **kwargs):
        # Handle batch_shape parameter that might be present in older models
        if batch_shape is not None:
            if input_shape is None:
                input_shape = batch_shape[1:]  # Remove batch dimension
            kwargs.pop('batch_shape', None)  # Remove batch_shape from kwargs
        
        super().__init__(input_shape=input_shape, dtype=dtype, sparse=sparse, name=name, ragged=ragged, **kwargs)

# Custom DTypePolicy for compatibility with newer Keras models
class CustomDTypePolicy:
    def __init__(self, name='float32'):
        self.name = name
        self.compute_dtype = name
        self.variable_dtype = name
    
    def __eq__(self, other):
        return isinstance(other, CustomDTypePolicy) and self.name == other.name
    
    def __repr__(self):
        return f"DTypePolicy({self.name})"

# Register the custom objects
tf.keras.utils.get_custom_objects()['InputLayer'] = CustomInputLayer
tf.keras.utils.get_custom_objects()['DTypePolicy'] = CustomDTypePolicy

# Custom CNN model configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'stress_cnn_model.h5')
CLASS_NAMES = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
EMOTION_TO_STRESS = {
    "happy": ("Low", 0.2),
    "neutral": ("Low", 0.3),
    "surprised": ("Medium", 0.55),
    "angry": ("High", 0.8),
    "fearful": ("High", 0.85),
    "sad": ("High", 0.75),
    "disgusted": ("High", 0.9),
}

# Global model variable
_custom_model = None

def detect_face(img):
    """Detect if a face is present in the image and return face location"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load the face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            logger.error("Failed to load face cascade classifier")
            return False, None

        # Very lenient face detection parameters for laptop cameras
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.02,  # More lenient scale factor
            minNeighbors=2,    # Reduced minimum neighbors
            minSize=(15, 15),  # Smaller minimum face size
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        logger.info(f"Face detection found {len(faces)} faces")
        return len(faces) > 0, faces
    except Exception as e:
        logger.error(f"Error in face detection: {str(e)}")
        return False, None

def check_face_quality(img, face_location):
    """Check if the face is well-lit and properly positioned"""
    try:
        x, y, w, h = face_location[0]
        face_roi = img[y:y+h, x:x+w]
        
        # Check brightness
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray_face)
        
        # Check face size relative to image
        img_area = img.shape[0] * img.shape[1]
        face_area = w * h
        face_ratio = face_area / img_area
        
        # Check face position (should be roughly centered)
        center_x = x + w/2
        center_y = y + h/2
        img_center_x = img.shape[1]/2
        img_center_y = img.shape[0]/2
        
        # Calculate distance from center (normalized)
        center_distance = np.sqrt(
            ((center_x - img_center_x) / img.shape[1])**2 +
            ((center_y - img_center_y) / img.shape[0])**2
        )
        
        # Very lenient quality checks for laptop cameras
        quality = {
            "is_bright": brightness > 20,  # Much lower brightness threshold
            "is_proper_size": 0.01 < face_ratio < 0.8,  # More lenient size range
            "is_centered": center_distance < 0.5,  # More lenient centering
            "brightness": float(brightness),
            "face_ratio": float(face_ratio),
            "center_distance": float(center_distance)
        }
        
        logger.info(f"Face quality metrics: {quality}")
        return quality
    except Exception as e:
        logger.error(f"Error in face quality check: {str(e)}")
        return {
            "is_bright": False,
            "is_proper_size": False,
            "is_centered": False,
            "brightness": 0,
            "face_ratio": 0,
            "center_distance": 1
        }

def load_custom_model():
    """Load the custom CNN model."""
    global _custom_model
    if _custom_model is None:
        try:
            if os.path.exists(MODEL_PATH):
                # Load model without compiling to avoid optimizer compatibility issues
                _custom_model = load_model(MODEL_PATH, compile=False)
                # Recompile with compatible optimizer
                _custom_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                logger.info(f"✅ Custom CNN model loaded successfully from {MODEL_PATH}")
            else:
                logger.error(f"❌ Custom model file not found: {MODEL_PATH}")
                return False
        except Exception as e:
            logger.error(f"❌ Error loading custom model: {e}")
            return False
    return True

def preprocess_face_for_model(face_img):
    """Preprocess face image for custom model prediction."""
    try:
        # Resize to model input size (64x64)
        face_resized = cv2.resize(face_img, (64, 64))
        
        # Convert BGR to RGB if needed
        if face_resized.shape[2] == 3:
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        else:
            face_rgb = face_resized
        
        # Normalize and add batch dimension
        face_array = face_rgb.astype(np.float32) / 255.0
        face_array = np.expand_dims(face_array, axis=0)
        
        return face_array
    except Exception as e:
        logger.error(f"Error preprocessing face for model: {e}")
        return None

def predict_emotion_with_custom_model(face_img):
    """Predict emotion using custom CNN model."""
    if not load_custom_model():
        return None
    
    try:
        # Preprocess the face
        processed_face = preprocess_face_for_model(face_img)
        if processed_face is None:
            return None
        
        # Make prediction
        predictions = _custom_model.predict(processed_face, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx])
        
        # Map to stress level
        stress_level, base_score = EMOTION_TO_STRESS[predicted_class]
        stress_score = round(base_score * confidence, 2)
        
        return {
            'emotion': predicted_class,
            'confidence': confidence,
            'stress_level': stress_level,
            'stress_score': stress_score
        }
        
    except Exception as e:
        logger.error(f"Error making prediction with custom model: {e}")
        return None

def analyze_image(image_data: str) -> Dict[str, Any]:
    """
    Analyze an image for emotion detection and stress analysis
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        logger.info(f"Image decoded successfully. Shape: {img.shape}")
        
        if img is None:
            return {"error": "Failed to process image data"}

        # Check if face is present
        face_detected, face_locations = detect_face(img)
        if not face_detected:
            logger.warning("No face detected in the image")
            return {"error": "No face detected. Please ensure your face is visible in the camera."}

        # Check face quality
        quality = check_face_quality(img, face_locations)
        
        # Provide specific feedback based on quality issues
        if not quality["is_bright"]:
            logger.warning(f"Poor lighting detected. Brightness: {quality['brightness']}")
            return {"error": "Poor lighting detected. Please ensure your face is well-lit."}
            
        if not quality["is_proper_size"]:
            if quality["face_ratio"] <= 0.01:
                logger.warning(f"Face too far. Ratio: {quality['face_ratio']}")
                return {"error": "Face is too far from the camera. Please move closer."}
            else:
                logger.warning(f"Face too close. Ratio: {quality['face_ratio']}")
                return {"error": "Face is too close to the camera. Please move back."}
                
        if not quality["is_centered"]:
            logger.warning(f"Face not centered. Distance: {quality['center_distance']}")
            return {"error": "Please center your face in the frame."}

        # Extract face for custom model
        x, y, w, h = face_locations[0]
        face_img = img[y:y+h, x:x+w]
        
        # Analyze emotion using custom CNN model
        try:
            logger.info("Starting emotion analysis with custom CNN model.")
            result = predict_emotion_with_custom_model(face_img)
            if result is None:
                logger.error("Custom model prediction failed")
                return {"error": "Unable to analyze emotions. Please ensure your face is clearly visible and try again."}
            
            logger.info(f"Custom CNN emotion analysis successful. Result: {result}")
        except Exception as e:
            logger.error(f"Error in custom CNN emotion analysis: {str(e)}", exc_info=True)
            return {"error": "Unable to analyze emotions. Please ensure your face is clearly visible and try again."}
        
        # Get emotion data from custom model result
        emotion = result['emotion']
        confidence = result['confidence']
        stress_level = result['stress_level']
        stress_score = result['stress_score']
        
        logger.info(f"Detected emotion: {emotion} with confidence: {confidence}")
        
        # Check if confidence meets minimum threshold (using same logic as before)
        emotion_config = settings.EMOTION_STRESS_MAP.get(emotion, {"level": "Medium", "min_confidence": 25})
        confidence_percent = confidence * 100  # Convert to percentage
        if confidence_percent < emotion_config["min_confidence"]:
            logger.warning(f"Low confidence in emotion detection: {confidence_percent:.1f}% < {emotion_config['min_confidence']}%. Emotion: {emotion}")
            return {"error": f"Low confidence in emotion detection ({confidence_percent:.1f}%). Please ensure your face is clearly visible and try again."}
        
        # Get suggestions for the stress level
        suggestions = settings.STRESS_SUGGESTIONS.get(stress_level, [])
        
        # Safely determine face_coords
        detected_face_coords = None
        if face_detected and isinstance(face_locations, np.ndarray) and face_locations.shape[0] > 0:
            # Ensure the first detected face has 4 coordinates (x, y, w, h)
            if len(face_locations[0]) == 4:
                detected_face_coords = face_locations[0].tolist()
        
        # Create result
        result = {
            "emotion": emotion,
            "stress_level": stress_level,
            "confidence": float(confidence),
            "stress_score": float(stress_score),
            "suggestions": suggestions,
            "face_quality": {
                "is_bright": bool(quality["is_bright"]),
                "is_proper_size": bool(quality["is_proper_size"]),
                "is_centered": bool(quality["is_centered"]),
                "brightness": float(quality["brightness"]),
                "face_ratio": float(quality["face_ratio"]),
                "center_distance": float(quality["center_distance"])
            },
            "face_coords": detected_face_coords
        }
        
        logger.info(f"Successfully processed image. Stress level: {stress_level}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred analyzing the image."}
