import os
import math
import subprocess
import imageio_ffmpeg

# Get ffmpeg binary path
FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()

print(f"Using ffmpeg binary: {FFMPEG_BINARY}")

from moviepy.video.io.VideoFileClip import VideoFileClip

source_path = r"C:\Users\blatam\Videos\largo.mp4"
output_dir = r"C:\Users\blatam\Videos\largo_segments\20s"
segment_duration = 20

def split_video():
    if not os.path.exists(source_path):
        print(f"Error: Source file not found at {source_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Get duration
        with VideoFileClip(source_path) as video:
            duration = video.duration
            print(f"Video duration: {duration} seconds")
            
        num_segments = math.ceil(duration / segment_duration)
        print(f"Splitting into {num_segments} segments...")

        for i in range(num_segments):
            start_time = i * segment_duration
            # Duration for this segment
            current_seg_duration = min(segment_duration, duration - start_time)
            
            output_filename = f"video_{i+1:03d}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"Creating segment {i+1}/{num_segments}: {start_time}s (duration {current_seg_duration}s)")
            
            # Construct ffmpeg command
            # -ss before -i is faster seeking (keyframe) but might be less accurate. 
            # -ss after -i is accurate. For splitting, accurate is better.
            # actually -ss before -i is fine for copy if we don't mind starting at keyframe, but for exact 6s, re-encoding might be needed if keyframes are sparse.
            # But user probably wants speed/copy if possible.
            # However, previous error was about copy failing due to data stream.
            # Let's try copy first with map.
            
            cmd = [
                FFMPEG_BINARY,
                "-y", # overwrite
                "-ss", str(start_time),
                "-t", str(current_seg_duration),
                "-i", source_path,
                "-map", "0:v", # Select video stream
                "-map", "0:a?", # Select audio stream if exists (optional)
                "-c", "copy", # Copy codec (no re-encode)
                output_path
            ]
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error creating segment {i+1}: {result.stderr}")
                # If copy fails, maybe try re-encoding? 
                # But let's stick to this for now.
                
        print("Done!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    split_video()
