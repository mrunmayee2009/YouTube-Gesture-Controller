
# YouTube Gesture Controller

A Python-based hand gesture recognition application that allows users to control YouTube video playback using simple hand gestures through a webcam.

## Project Overview

The YouTube Gesture Controller uses computer vision and hand tracking to recognize finger gestures and perform media control actions. It provides a touch-free way to interact with YouTube videos.

## Features

- Real-time hand detection using a webcam.
- Finger counting and gesture recognition.
- YouTube playback control using hand gestures.
- Voice feedback for detected actions.
- Live camera preview with hand landmarks.
- Interactive dashboard built using Tkinter.
- Gesture locking and unlocking.
- Activity history to view detected actions.
- Customizable application settings.

## Gesture Controls

| Hand Gesture | Action |
|---|---|
| 0 Fingers (Fist) | Mute / Unmute |
| 1 Finger | Seek Forward |
| 2 Fingers | Seek Backward |
| 3 Fingers | Volume Up |
| 4 Fingers | Volume Down |
| 5 Fingers | Play / Pause |

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Tkinter
- PyAutoGUI
- Pillow
- Pyttsx3

## Project Structure

```text
YouTube-Gesture-Controller/
│
├── main.py
├── gesture_controller.py
├── config.json
├── requirements.txt
├── README.md
│
└── assets/
```

## Installation

### 1. Clone the Repository

```text
git clone YOUR_GITHUB_REPOSITORY_LINK
```

### 2. Open the Project Folder

Open the downloaded project folder in Visual Studio Code.

### 3. Install Required Libraries

Open the VS Code terminal and execute:

```text
python -m pip install -r requirements.txt
```

### 4. Run the Application

In the VS Code terminal, execute:

```text
python main.py
```

## How to Use

1. Connect your webcam to the computer.
2. Open the project in Visual Studio Code.
3. Open the VS Code terminal in the project folder.
4. Run the application using `python main.py`.
5. The YouTube Gesture Controller dashboard will open.
6. Click **Start Controller** to activate the webcam and begin gesture detection.
7. Open YouTube in your web browser.
8. Play a video and click on the video player to make it the active window.
9. Keep YouTube in the foreground. The gesture controller will continue running in the background.
10. Show your hand in front of the webcam to control YouTube using the supported gestures.
11. Use **Lock Gestures** on the dashboard to temporarily disable gesture actions.
12. Click **Stop Controller** to stop gesture detection.
13. Click **Exit** to close the application.

## Requirements

- Windows operating system.
- Python 3.10 or compatible installed version.
- Working webcam.
- Internet connection to access YouTube.
- Required Python libraries listed in `requirements.txt`.

## Future Improvements

- Improved gesture recognition accuracy.
- Additional customizable hand gestures.
- Support for more media platforms.
- Improved gesture control and user experience.

## Author

Developed as a Python-based Computer Vision project.
