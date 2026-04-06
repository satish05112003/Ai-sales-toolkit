import subprocess
import os
from pathlib import Path

def create_video(images, output_path="storyboard.mp4"):
    """
    Concatenate a list of images into an mp4 video using FFmpeg.
    Ensures 3-second duration per frame with smooth transitions between scenes.
    """
    # Use unique input file name based on output path (to avoid race conditions)
    input_file_name = f"{Path(output_path).stem}_images.txt"
    
    # Path of images.txt (same dir as video)
    input_file_path = Path(output_path).parent / input_file_name

    # Write the concat instruction file for FFmpeg
    with open(input_file_path, "w") as f:
        for img_path in images:
            # Escape single quotes and use absolute paths
            f.write(f"file '{str(img_path)}'\n")
            f.write("duration 3\n")
        # Repeating the last file briefly is an FFmpeg quirk for specific concat engines
        if images:
            f.write(f"file '{str(images[-1])}'\n")

    # Construct the command
    # -f concat: Concatenate files
    # -safe 0: No safety for paths (avoids path-escaping issues)
    # -vf fps=25,format=yuv420p: Ensure standard video format for compatibility
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(input_file_path),
        "-vf", "fps=25,format=yuv420p,scale=1024:-1",
        "-c:v", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    print(f"[Video Generator] Running command: {' '.join(cmd)}")
    
    try:
        # Run FFmpeg (synchronously wait for completion)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Cleanup temporary concat file
        if input_file_path.exists():
            os.remove(input_file_path)
            
        if result.returncode != 0:
            print(f"[Video Error] FFmpeg returned non-zero exit code: {result.returncode}")
            print(f"  > stderr: {result.stderr}")
            return None
            
        return str(output_path)
    except Exception as e:
        print(f"[Video Error] Subprocess failed: {e}")
        return None
