import os
import cv2
import pytesseract
import pandas as pd
from datetime import timedelta
from multiprocessing import Pool, cpu_count
import logging

# Configure logging
logging.basicConfig(
    filename="video_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Constants
VIDEO_FOLDER = "/Users/studu/Desktop/Photoshop"
ACTIONS_TO_TRACK = [
    "Move", "Marquee", "Lasso", "Object Selection", "Quick Selection", "Magic Wand", "Crop", 
    "Perspective Crop", "Slice", "Slice Select", "Eyedropper", "3D Material Eyedropper", 
    "Color Sampler", "Ruler", "Note", "Count", "Spot Healing Brush", "Healing Brush", "Patch", 
    "Content-Aware Move", "Red Eye", "Brush", "Pencil", "Color Replacement", "Mixer Brush", 
    "Clone Stamp", "Pattern Stamp", "History Brush", "Art History Brush", "Eraser", 
    "Background Eraser", "Magic Eraser", "Gradient", "Paint Bucket", "Blur", "Sharpen", 
    "Smudge", "Dodge", "Burn", "Sponge", "Pen", "Freeform Pen", "Curvature Pen", 
    "Add Anchor Point", "Delete Anchor Point", "Convert Point", "Horizontal Type", 
    "Vertical Type", "Horizontal Type Mask", "Vertical Type Mask", "Path Selection", 
    "Direct Selection", "Rectangle", "Rounded Rectangle", "Ellipse", "Polygon", "Line", 
    "Custom Shape", "Hand", "Rotate View", "Zoom"
]

def extract_ui_text(frame):
    """Extract text from a frame using Tesseract OCR."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    custom_config = r'--oem 3 --psm 6'
    ui_text = pytesseract.image_to_string(frame_rgb, config=custom_config)
    return ui_text.strip()

def process_video_chunk(args):
    """Process a chunk of a video."""
    video_path, start_frame, end_frame, fps, actions_to_track, video_name = args
    dataset = []
    last_detected_tool = None
    active_tool_start_time = None

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Could not open video file: {video_path}")
            return dataset

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        for frame_count in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break

            # Process one frame per second
            if frame_count % fps != 0:
                continue

            timestamp = str(timedelta(seconds=frame_count // fps))
            ui_text = extract_ui_text(frame)

            # Detect the tool in use
            detected_tool = None
            for action in actions_to_track:
                if action.lower() in ui_text.lower():
                    detected_tool = action
                    break

            # Track tool usage duration
            if detected_tool and detected_tool != last_detected_tool:
                if last_detected_tool is not None:
                    dataset.append({
                        "Video Name": video_name,
                        "Action": last_detected_tool,
                        "Start Timestamp": active_tool_start_time,
                        "End Timestamp": timestamp,
                    })
                last_detected_tool = detected_tool
                active_tool_start_time = timestamp

        # Save the last tool's usage
        if last_detected_tool:
            dataset.append({
                "Video Name": video_name,
                "Action": last_detected_tool,
                "Start Timestamp": active_tool_start_time,
                "End Timestamp": timestamp,
            })

    except Exception as e:
        logging.error(f"Error processing chunk {start_frame}-{end_frame} of {video_path}: {e}")
    finally:
        cap.release()

    return dataset

def process_video(video_path, video_name):
    """Process a video file."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Could not open video file: {video_path}")
            return []

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Divide the video into chunks for parallel processing
        num_chunks = cpu_count()
        chunk_size = total_frames // num_chunks
        chunks = [
            (video_path, i, min(i + chunk_size, total_frames), fps, ACTIONS_TO_TRACK, video_name)
            for i in range(0, total_frames, chunk_size)
        ]

        # Process chunks in parallel
        with Pool(processes=num_chunks) as pool:
            results = pool.map(process_video_chunk, chunks)

        # Combine results from all chunks
        dataset = [item for sublist in results for item in sublist]
        return dataset

    except Exception as e:
        logging.error(f"Error processing video {video_path}: {e}")
        return []

def create_csv_from_videos():
    """Process all videos in the folder and create a CSV dataset."""
    all_data = []
    video_files = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.mkv', '.avi'))]

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    for video_file in video_files:
        video_path = os.path.join(VIDEO_FOLDER, video_file)
        video_name = os.path.splitext(video_file)[0]
        logging.info(f"Processing video: {video_name}")

        video_data = process_video(video_path, video_name)
        all_data.extend(video_data)

    # Save the dataset to a CSV file
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("video_tool_usage_dataset.csv", index=False)
        logging.info("Dataset created and saved as 'video_tool_usage_dataset.csv'")
    else:
        logging.warning("No actions detected. Dataset not saved.")

if __name__ == "__main__":
    create_csv_from_videos() 