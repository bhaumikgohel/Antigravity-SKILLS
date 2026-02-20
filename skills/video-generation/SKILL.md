---
name: generating-camera-movements
description: Implements and simulates professional camera movements on video content. Includes logic for tracking, dolly, pan, tilt, zoom, and complex cinematic effects like the dolly zoom and whip pan. Use when building video editors or shot simulators.
---

# Generating Camera Movements

This skill provides the technical implementation and cinematic theory for applying camera movements to video content. These techniques can be used to simulate high-end cinematography in post-production or dynamic web applications.

## When to use this skill
- When building a video editing tool that requires shot simulation.
- When creating dynamic hero sections or interactive video experiences.
- When you need to explain or implement cinematic techniques in code (CSS/SVG/Canvas).

## Camera Movement Catalog

### 1. Tracking Shot
- **Description**: The camera physically moves through the scene (sideways, forward, or backward).
- **Implementation**: Combine `translate` (sideways) and `scale` (forward/backward) over a long duration.
- **Vibe**: Immersive, following the subject.

### 2. Dolly Shot
- **Description**: Moving the entire camera forward or backward.
- **Implementation**: Transition `scale` from 1 to 1.5 (Push-in) or 1.5 to 1 (Pull-out).
- **Vibe**: Focuses attention on a subject or reveals the environment.

### 3. Truck Shot
- **Description**: Moving the camera left or right along a track.
- **Implementation**: Transition `translateX` from `-10%` to `10%`.
- **Vibe**: Observational, following a character walking.

### 4. Pan Shot
- **Description**: Pivoting left or right on a horizontal axis.
- **Implementation**: Transition `translateX` while slightly adjusting `perspective` and `rotateY` for realism.
- **Vibe**: Expanding the field of view.

### 5. Whip Pan (Swish Pan)
- **Description**: A very fast pan creating motion blur.
- **Implementation**: Rapid `translateX` combined with a `filter: blur(xpx)` that peaks in the middle of the transition.
- **Vibe**: Energetic, used for transitions or showing passage of time.

### 6. Tilt Shot
- **Description**: Pivoting vertically (up or down).
- **Implementation**: Transition `translateY` with subtle `rotateX`.
- **Vibe**: Establishing tall scenery or dramatic character introductions.

### 7. Crane Shot (Jib Shot)
- **Description**: Camera mounted on a robotic crane, moving in any direction (often up and over).
- **Implementation**: Multi-axis movement: `translateY(up)`, `scale(up)`, and subtle `rotate`.
- **Vibe**: Epic, "god-like" perspective transitions.

### 8. Aerial Shot
- **Description**: extremely high bird's eye view (Drones/Helicopters).
- **Implementation**: High `scale` (zoomed out) with very slow, drifting `translate` and `rotate`.
- **Vibe**: Context-setting, grand scale.

### 9. Pedestal Shot
- **Description**: Vertical camera movement (up/down) relative to the subject.
- **Implementation**: Pure `translateY` transition.
- **Vibe**: Moving with a subject standing up or sitting down.

### 10. Handheld Shot
- **Description**: Unstabilized, physical holding of the camera.
- **Implementation**: High-frequency, low-amplitude `translate` and `rotate` jitter using `requestAnimationFrame` or CSS Keyframes.
- **Vibe**: Frenzied, hectic, or "found footage" realism.

### 11. Zoom Shot
- **Description**: Changing focal length while stationary.
- **Implementation**: Pure `scale` transition. Distinct from Dolly because perspective doesn't change.
- **Vibe**: Close-ups or wide shots without moving through space.

### 12. Rack Focus
- **Description**: Changing lens focus mid-shot.
- **Implementation**: Transitioning `filter: blur(xpx)` from a high value to 0 (or vice versa).
- **Vibe**: Shifting viewer attention between foreground and background.

### 13. Dolly Zoom (Vertigo Effect)
- **Description**: Dollying while zooming in the opposite direction.
- **Implementation**: Simultaneously `scale` up while "moving back" (decreasing effective viewport size) to keep the subject the same size while the background distorts.
- **Vibe**: Disorienting, psychological tension.

## Workflow

1. **Selection**: Identify the desired emotional impact (e.g., Dolly for tension, Pan for scale).
2. **Container Setup**:
   - Wrap the `<video>` in a `div` with `overflow: hidden`.
   - Ensure the video is slightly larger than the container (e.g., `transform: scale(1.1)`) to allow room for "movement" without showing edges.
3. **Execution**:
   - Apply CSS Transitions or Web Animations API (WAAPI) for smooth movement.
   - Use `cubic-bezier` for cinematic easing (standard `ease-in-out` often feels too mechanical).
4. **Validation**: Check for "edge-peeking" where the video doesn't cover the container during movement.

## Instructions for implementation

### Basic Movement Component (CSS)
```css
.camera-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 2s cubic-bezier(0.4, 0, 0.2, 1), filter 2s ease;
}

/* Example: Dolly In */
.dolly-in .camera-video {
  transform: scale(1.3);
}

/* Example: Whip Pan */
@keyframes whip-pan {
  0% { transform: translateX(0); filter: blur(0); }
  50% { transform: translateX(50%); filter: blur(10px); }
  100% { transform: translateX(100%); filter: blur(0); }
}
```

## Resources
- [Example Web App Implementation](examples/web-app/index.html)
- [FFMPEG Shot Synthesis Guide](resources/ffmpeg-guide.md)
