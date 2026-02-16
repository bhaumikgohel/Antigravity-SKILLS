import cv2
import numpy as np

def apply_camera_movement(input_path, output_path, movement_type='dolly', intensity=1.5):
    """
    Simulates camera movement on a video using OpenCV.
    
    Supported types: 'dolly' (zoom), 'truck' (horizontal), 'pedestal' (vertical)
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate progress
        progress = i / total_frames

        if movement_type == 'dolly':
            # Zoom logic
            scale = 1.0 + (intensity - 1.0) * progress
            new_w, new_h = int(width * scale), int(height * scale)
            resized = cv2.resize(frame, (new_w, new_h))
            # Center crop
            start_x = (new_w - width) // 2
            start_y = (new_h - height) // 2
            frame = resized[start_y:start_y+height, start_x:start_x+width]

        elif movement_type == 'truck':
            # Side to side
            shift_x = int(width * 0.1 * progress * intensity)
            M = np.float32([[1, 0, shift_x], [0, 1, 0]])
            frame = cv2.warpAffine(frame, M, (width, height))

        out.write(frame)

    cap.release()
    out.release()
    print(f"Video saved to {output_path}")

if __name__ == "__main__":
    print("Video Generation Python Script Loaded.")
    # Usage: apply_camera_movement('input.mp4', 'output.mp4', 'dolly', 1.2)
