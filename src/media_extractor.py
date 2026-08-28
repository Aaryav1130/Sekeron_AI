import os
import glob
import cv2
import random
from pathlib import Path

class MediaSelector:
    """
    Selects media sensibly to avoid processing every frame or every file blindly.
    This saves compute, token usage, and adheres to the assignment constraints.
    """
    
    def __init__(self, artist_folder: str):
        self.folder = Path(artist_folder)
        
    def select_images(self, max_images: int = 4) -> list[str]:
        """
        Selects up to max_images from the folder.
        In a production scenario, this could use EXIF variance to select diverse images.
        For this prototype, we select the first and last (time-wise) and random mid-points
        to get a diverse spread of their portfolio without processing 100 images blindly.
        """
        image_files = []
        for ext in ["*.jpg", "*.jpeg", "*.png"]:
            image_files.extend(glob.glob(str(self.folder / ext)))
            image_files.extend(glob.glob(str(self.folder / ext.upper())))
            
        if not image_files:
            return []
            
        # Sort by name (which often correlates with time/batch)
        image_files = sorted(image_files)
        
        if len(image_files) <= max_images:
            return image_files
            
        # Pick first, last, and evenly spaced middle ones
        step = len(image_files) / max_images
        selected = [image_files[int(i * step)] for i in range(max_images)]
        return selected

    def extract_video_keyframes(self, max_frames: int = 3) -> list[str]:
        """
        Extracts specific keyframes from videos rather than processing blindly.
        Selects frames at 10%, 50%, and 90% marks to capture beginning, middle, and end.
        """
        video_files = []
        for ext in ["*.mp4", "*.mov", "*.avi"]:
            video_files.extend(glob.glob(str(self.folder / ext)))
            video_files.extend(glob.glob(str(self.folder / ext.upper())))
            
        if not video_files:
            return []
            
        # For simplicity in this assessment, pick the first video found
        video_path = video_files[0]
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            return []
            
        frame_indices = [
            int(total_frames * 0.1),
            int(total_frames * 0.5),
            int(total_frames * 0.9)
        ]
        
        saved_frames = []
        out_dir = self.folder / "processed_keyframes"
        out_dir.mkdir(exist_ok=True)
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frame_path = out_dir / f"frame_{idx}.jpg"
                cv2.imwrite(str(frame_path), frame)
                saved_frames.append(str(frame_path))
                
        cap.release()
        return saved_frames
        
    def select_audio(self) -> list[str]:
        """
        Returns audio files. Audio is typically dense, so we rely on the AI model 
        to sample the audio directly, but we restrict to 1 file to prevent overload.
        """
        audio_files = []
        for ext in ["*.mp3", "*.wav", "*.m4a"]:
            audio_files.extend(glob.glob(str(self.folder / ext)))
            audio_files.extend(glob.glob(str(self.folder / ext.upper())))
            
        if not audio_files:
            return []
            
        return [audio_files[0]]
