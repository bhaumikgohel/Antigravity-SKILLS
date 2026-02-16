# FFMPEG Camera Movement Guide

This guide provides the FFMPEG filter strings for synthesizing camera movements programmatically.

## 1. Zoom / Dolly
Use the `zoompan` filter.
- **Zoom In**: `zoompan=z='min(zoom+0.0015,1.5)':d=125:s=1920x1080`
- **Zoom Out**: `zoompan=z='max(1.5-0.0015,1.0)':d=125:s=1920x1080`

## 2. Pan / Truck
Use `crop` and `x` coordinates.
- **Pan Right**: `crop=w=iw/1.1:h=ih/1.1:x='(t/duration)*(iw-ow)':y=ih/2-oh/2`

## 3. Tilt / Pedestal
- **Tilt Up**: `crop=w=iw/1.1:h=ih/1.1:x=iw/2-ow/2:y='(1-t/duration)*(ih-oh)'`

## 4. Handheld (Shake)
Use `deshake` in reverse or `crop` with random noise.
- **Shake**: `crop=w=iw-20:h=ih-20:x='10+5*sin(2*PI*t*5)':y='10+5*cos(2*PI*t*7)'`

## 5. Whip Pan
Combine fast crop move with boxblur.
- **Whip**: `crop=...,boxblur=lr='t*20':lp=2`

## Pro Tips for FFMPEG
- **Interpolation**: Always set `s=WxH` (size) to prevent the video from shrinking during zoom.
- **Dolly Zoom**: Dynamically change `z` while simultaneously cropping the viewport to keep the subject centered.
- **Ease-In/Out**: Use algebraic expressions for the coordinates instead of linear `t/duration`. 
  - *Example (Ease-In)*: `(t/duration)^2`
