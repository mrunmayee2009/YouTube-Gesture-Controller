
import cv2
import mediapipe as mp
import pyautogui
import pyttsx3
import threading
import time
import json
import logging


class GestureController:

    def __init__(self, config_path="config.json"):

        with open(config_path, "r") as file:
            self.config = json.load(file)

        self.running = False
        self.locked = False
        self.cap = None
        self.callback = None

        self.last_action_time = 0
        self.last_gesture = None

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config["max_hands"],
            min_detection_confidence=self.config["detection_confidence"],
            min_tracking_confidence=self.config["tracking_confidence"]
        )

        self.speech_queue = []
        self.speech_lock = threading.Lock()
        self.speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )
        self.speech_thread.start()

        self.action_callback = None

    def _speech_worker(self):

        try:
            engine = pyttsx3.init()

            while True:
                message = None

                with self.speech_lock:
                    if self.speech_queue:
                        message = self.speech_queue.pop(0)

                if message:
                    engine.say(message)
                    engine.runAndWait()
                else:
                    time.sleep(0.1)

        except Exception as error:
            logging.warning(f"Voice feedback error: {error}")

    def speak(self, message):

        if not self.config.get("voice_feedback", True):
            return

        with self.speech_lock:
            if len(self.speech_queue) < 3:
                self.speech_queue.append(message)

    def count_fingers(self, landmarks, handedness):

        fingers = []

        # Thumb detection
        if handedness == "Right":
            fingers.append(
                landmarks[4].x < landmarks[3].x
            )
        else:
            fingers.append(
                landmarks[4].x > landmarks[3].x
            )

        # Index, middle, ring and little fingers
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]

        for tip, pip in zip(tip_ids, pip_ids):
            fingers.append(
                landmarks[tip].y < landmarks[pip].y
            )

        return sum(fingers)

    def perform_action(self, finger_count):

        if not self.config.get("gestures_enabled", True):
            return

        if self.locked:
            return

        current_time = time.time()

        delay = self.config.get("gesture_delay", 1.0)

        if current_time - self.last_action_time < delay:
            return

        actions = self.config.get("gesture_actions", {})

        action = actions.get(str(finger_count))

        if not action:
            return

        try:
            if action == "mute":
                pyautogui.press("m")

            elif action == "seek_forward":
                pyautogui.press("right")

            elif action == "seek_backward":
                pyautogui.press("left")

            elif action == "volume_up":
                pyautogui.press("up")

            elif action == "volume_down":
                pyautogui.press("down")

            elif action == "play_pause":
                pyautogui.press("space")

            self.last_action_time = current_time

            self.last_gesture = finger_count

            if self.action_callback:
                self.action_callback(
                    finger_count,
                    action
                )

            self.speak(action.replace("_", " "))

        except Exception as error:
            logging.warning(f"Action error: {error}")

    def process_frame(self, frame):

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(frame_rgb)

        action_text = "No Gesture"
        finger_count = 0
        handedness = "Unknown"

        if results.multi_hand_landmarks:

            for index, hand_landmarks in enumerate(
                results.multi_hand_landmarks
            ):

                handedness = results.multi_handedness[
                    index
                ].classification[0].label

                finger_count = self.count_fingers(
                    hand_landmarks.landmark,
                    handedness
                )

                if self.config.get("show_landmarks", True):
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                if not self.locked:
                    self.perform_action(finger_count)
                    action_text = f"{finger_count} Fingers"

                else:
                    action_text = "Gesture Locked"

        return frame, action_text, finger_count, handedness

    def start(self, callback, action_callback=None):

        if self.running:
            return False

        self.callback = callback
        self.action_callback = action_callback

        self.running = True

        self.worker = threading.Thread(
            target=self._camera_worker,
            daemon=True
        )

        self.worker.start()

        return True

    def _camera_worker(self):

        self.cap = cv2.VideoCapture(
            self.config.get("camera_index", 0)
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.config.get("camera_width", 640)
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.config.get("camera_height", 480)
        )

        if not self.cap.isOpened():
            self.running = False
            logging.error("Camera could not be opened.")
            return

        previous_time = time.time()

        while self.running:

            success, frame = self.cap.read()

            if not success:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)

            frame, action, fingers, hand = self.process_frame(frame)

            current_time = time.time()

            fps = 1 / max(
                current_time - previous_time,
                0.001
            )

            previous_time = current_time

            if self.callback:
                self.callback(
                    frame,
                    action,
                    fingers,
                    hand,
                    fps
                )

        if self.cap:
            self.cap.release()
            self.cap = None

    def toggle_lock(self):

        self.locked = not self.locked

        if self.locked:
            self.speak("Gesture control locked")
        else:
            self.speak("Gesture control unlocked")

        return self.locked

    def update_config(self, key, value):

        self.config[key] = value

        with open("config.json", "w") as file:
            json.dump(self.config, file, indent=4)

    def stop(self):

        self.running = False

        if hasattr(self, "worker") and self.worker.is_alive():
            self.worker.join(timeout=2)

        if self.cap:
            self.cap.release()
            self.cap = None

    def shutdown(self):

        self.stop()

        if self.hands:
            self.hands.close()
