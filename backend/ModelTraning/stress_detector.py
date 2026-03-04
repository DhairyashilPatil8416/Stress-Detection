#!/usr/bin/env python3
"""
Stress Detection Executable - Real-time Version
Uses OpenCV for real-time webcam stress detection from facial expressions.

Usage:
    python stress_detector.py --realtime                    # Real-time webcam detection
    python stress_detector.py image.jpg                     # Single image analysis
    python stress_detector.py /path/to/images/ --output results.csv  # Batch processing

Real-time Controls:
    - Press 'q' to quit
    - Press 's' to pause/resume stress detection
    - High stress detection triggers 10-second sleep period
"""

import sys
import os
import argparse
import numpy as np
import cv2
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
import warnings
warnings.filterwarnings('ignore')

class StressDetector:
    def __init__(self, model_path='stress_cnn_model.h5'):
        """Initialize the stress detector with the trained model."""
        self.model_path = model_path
        self.model = None
        self.class_names = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        self.emotion_to_stress = {
            "happy": ("Normal", 0.2),
            "neutral": ("Normal", 0.3),
            "surprised": ("Medium", 0.55),
            "angry": ("High", 0.8),
            "fearful": ("High", 0.85),
            "sad": ("High", 0.75),
            "disgusted": ("High", 0.9),
        }

        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Stress detection state
        self.last_detection_time = 0
        self.sleep_duration = 10  # seconds

        self.load_model()

    def load_model(self):
        """Load the trained model."""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                print(f"✅ Model loaded successfully from {self.model_path}")
            else:
                print(f"❌ Model file not found: {self.model_path}")
                print("Please ensure the model file exists in the same directory.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)

    def preprocess_image(self, image_path):
        """Preprocess the image for model prediction."""
        try:
            # Load and resize image
            img = load_img(image_path, target_size=(64, 64))
            # Convert to array and normalize
            img_array = img_to_array(img) / 255.0
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"❌ Error preprocessing image {image_path}: {e}")
            return None

    def predict_stress(self, image_path):
        """Predict stress level from an image."""
        if self.model is None:
            print("❌ Model not loaded!")
            return None

        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        if processed_image is None:
            return None

        try:
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = self.class_names[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])

            # Map to stress level
            stress_level, base_score = self.emotion_to_stress[predicted_class]
            stress_score = round(base_score * confidence, 2)

            return {
                'emotion': predicted_class,
                'confidence': confidence,
                'stress_level': stress_level,
                'stress_score': stress_score
            }

        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return None

    def predict_from_directory(self, directory_path, output_file=None):
        """Predict stress for all images in a directory."""
        if not os.path.exists(directory_path):
            print(f"❌ Directory not found: {directory_path}")
            return

        results = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

        print(f"🔍 Scanning directory: {directory_path}")

        for filename in os.listdir(directory_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(directory_path, filename)
                print(f"📸 Processing: {filename}")

                result = self.predict_stress(image_path)
                if result:
                    result['filename'] = filename
                    results.append(result)
                    print(f"   Emotion: {result['emotion']} ({result['confidence']*100:.1f}%)")
                    print(f"   Stress: {result['stress_level']} (Score: {result['stress_score']})")
                else:
                    print(f"   ❌ Failed to process {filename}")

        # Save results if requested
        if output_file and results:
            try:
                with open(output_file, 'w') as f:
                    f.write("Filename,Emotion,Confidence,Stress_Level,Stress_Score\n")
                    for result in results:
                        f.write(f"{result['filename']},{result['emotion']},{result['confidence']:.4f},{result['stress_level']},{result['stress_score']}\n")
                print(f"✅ Results saved to {output_file}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")

        return results

    def detect_faces(self, frame):
        """Detect faces in a frame using OpenCV."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces

    def preprocess_face(self, frame, face_coords):
        """Extract and preprocess face from frame."""
        x, y, w, h = face_coords
        face = frame[y:y+h, x:x+w]

        # Resize to model input size
        face_resized = cv2.resize(face, (64, 64))

        # Convert to RGB if needed
        if face_resized.shape[2] == 3:
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        else:
            face_rgb = face_resized

        # Normalize and add batch dimension
        face_array = face_rgb.astype(np.float32) / 255.0
        face_array = np.expand_dims(face_array, axis=0)

        return face_array, face_resized

    def predict_stress_from_frame(self, frame):
        """Predict stress from a video frame."""
        if self.model is None:
            return None

        # Detect faces
        faces = self.detect_faces(frame)
        results = []

        for (x, y, w, h) in faces:
            try:
                # Preprocess face
                face_array, face_resized = self.preprocess_face(frame, (x, y, w, h))

                # Make prediction
                predictions = self.model.predict(face_array, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = self.class_names[predicted_class_idx]
                confidence = float(predictions[0][predicted_class_idx])

                # Map to stress level
                stress_level, base_score = self.emotion_to_stress[predicted_class]
                stress_score = round(base_score * confidence, 2)

                results.append({
                    'bbox': (x, y, w, h),
                    'emotion': predicted_class,
                    'confidence': confidence,
                    'stress_level': stress_level,
                    'stress_score': stress_score
                })

            except Exception as e:
                print(f"Error processing face: {e}")
                continue

        return results

    def should_detect_stress(self):
        """Check if enough time has passed since last detection."""
        current_time = time.time()
        if current_time - self.last_detection_time > self.sleep_duration:
            return True
        return False

    def update_detection_time(self):
        """Update the last detection timestamp."""
        self.last_detection_time = time.time()

    def draw_results(self, frame, results):
        """Draw detection results on frame."""
        for result in results:
            x, y, w, h = result['bbox']

            # Choose color based on stress level
            if result['stress_level'] == 'High':
                color = (0, 0, 255)  # Red
            elif result['stress_level'] == 'Medium':
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 255, 0)  # Green

            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            # Draw text
            text = f"{result['emotion']} ({result['stress_score']})"
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame

    def run_realtime_detection(self, camera_index=0):
        """Run real-time stress detection using webcam."""
        print("🎥 Starting real-time stress detection...")
        print("Press 'q' to quit, 's' to toggle stress detection pause")

        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"❌ Cannot open camera {camera_index}")
            return

        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        paused = False
        stress_detected = False

        print("✅ Camera opened successfully. Starting detection...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            current_time = time.time()

            if not paused and self.should_detect_stress():
                # Detect stress in current frame
                results = self.predict_stress_from_frame(frame)

                if results:
                    # Check if any face shows high stress
                    high_stress_faces = [r for r in results if r['stress_level'] == 'High']

                    if high_stress_faces and not stress_detected:
                        print(f"🚨 HIGH STRESS DETECTED! Sleeping for {self.sleep_duration} seconds...")
                        stress_detected = True
                        self.update_detection_time()

                        # Flash red overlay for alert
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
                        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

                        cv2.putText(frame, "HIGH STRESS ALERT!", (50, 50),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

                    elif not high_stress_faces:
                        stress_detected = False

                    # Draw results on frame
                    frame = self.draw_results(frame, results)

            # Display status
            status_text = "PAUSED" if paused else ("SLEEPING" if not self.should_detect_stress() else "ACTIVE")
            color = (0, 0, 255) if status_text == "SLEEPING" else (0, 255, 0) if status_text == "ACTIVE" else (255, 0, 0)

            cv2.putText(frame, f"Status: {status_text}", (10, frame.shape[0] - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            time_until_active = max(0, self.sleep_duration - (current_time - self.last_detection_time))
            if time_until_active > 0:
                cv2.putText(frame, f"Next check: {time_until_active:.1f}s", (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Show frame
            cv2.imshow('Stress Detection', frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                paused = not paused
                print(f"{'Paused' if paused else 'Resumed'} stress detection")

        cap.release()
        cv2.destroyAllWindows()
        print("✅ Real-time detection stopped")

def main():
    parser = argparse.ArgumentParser(description='Stress Detection from Facial Images')
    parser.add_argument('input', nargs='?', help='Path to image file or directory (not needed for --realtime)')
    parser.add_argument('--model', '-m', default='stress_cnn_model.h5',
                       help='Path to the trained model file (default: stress_cnn_model.h5)')
    parser.add_argument('--output', '-o', help='Output CSV file for directory predictions')
    parser.add_argument('--realtime', '-r', action='store_true',
                       help='Run real-time stress detection using webcam')
    parser.add_argument('--camera', '-c', type=int, default=0,
                       help='Camera index for real-time detection (default: 0)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (less output)')

    args = parser.parse_args()

    # Initialize detector
    detector = StressDetector(args.model)

    if args.realtime:
        # Real-time detection mode
        detector.run_realtime_detection(args.camera)
        return

    # Check if input is provided
    if not args.input:
        print("❌ Please provide an input path or use --realtime for webcam detection")
        print("Usage examples:")
        print("  python stress_detector.py image.jpg")
        print("  python stress_detector.py /path/to/images/ --output results.csv")
        print("  python stress_detector.py --realtime")
        sys.exit(1)

    # Check if input is a file or directory
    if os.path.isfile(args.input):
        # Single image prediction
        print(f"🔍 Analyzing image: {args.input}")
        result = detector.predict_stress(args.input)

        if result:
            print("\n" + "="*50)
            print("STRESS DETECTION RESULT")
            print("="*50)
            print(f"Image: {args.input}")
            print(f"Detected Emotion: {result['emotion']}")
            print(f"Confidence: {result['confidence']*100:.2f}%")
            print(f"Stress Level: {result['stress_level']}")
            print(f"Stress Score: {result['stress_score']}")
            print("="*50)

            # Provide interpretation
            if result['stress_score'] < 0.4:
                print("🟢 LOW STRESS: Person appears relaxed and positive")
            elif result['stress_score'] < 0.7:
                print("🟡 MEDIUM STRESS: Person shows moderate stress indicators")
            else:
                print("🔴 HIGH STRESS: Person shows significant stress indicators")

        else:
            print("❌ Failed to analyze image")
            sys.exit(1)

    elif os.path.isdir(args.input):
        # Directory prediction
        results = detector.predict_from_directory(args.input, args.output)

        if results:
            print(f"\n✅ Processed {len(results)} images successfully")

            # Summary statistics
            stress_levels = [r['stress_level'] for r in results]
            stress_scores = [r['stress_score'] for r in results]

            print("\n📊 SUMMARY STATISTICS:")
            print(f"Average Stress Score: {np.mean(stress_scores):.3f}")
            print(f"Stress Level Distribution:")
            for level in ['Normal', 'Medium', 'High']:
                count = stress_levels.count(level)
                percentage = (count / len(stress_levels)) * 100
                print(f"  {level}: {count} images ({percentage:.1f}%)")
        else:
            print("❌ No images processed")
            sys.exit(1)

    else:
        print(f"❌ Input path not found: {args.input}")
        sys.exit(1)

if __name__ == "__main__":
    main()