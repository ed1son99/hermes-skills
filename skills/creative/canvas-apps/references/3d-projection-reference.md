# 3D Perspective Projection for Canvas 2D (Reference)

Key concepts for building a 360° orbit-able 3D scene in vanilla Canvas 2D.

## Coordinate System
- X = world right/left
- Y = world up (height from ground)
- Z = world forward/back (depth)
- Ground plane at Y = 0

## Camera
Spherical coordinates orbiting around a target point on the ground plane:
- `camAzimuth` — horizontal orbit angle (0=front, 90=right, 180=back, 270=left)
- `camElevation` — vertical angle (0=top-down, 90=eye-level at ground)
- `camDistance` — radial distance from target
- `camTargetX, camTargetZ` — look-at point on ground (for panning)

## Projection Pipeline
1. Compute camera world position from spherical coords
2. Build orthonormal camera basis: forward (target - camera), right (cross(worldUp, forward)), cameraUp (cross(forward, right))
3. Subtract camera position from world point → vector
4. Dot into camera basis → camera-space coordinates
5. Perspective divide: screenX = camX * (focalLength / camZ)
6. cull points with camZ ≤ 1 (behind camera)

## Focal Length
Use `fovScale = 600 / camZ` for reasonable perspective. Adjust 600 to change field of view.

## Painter's Algorithm
Sort items by squared distance from camera (far to near) before drawing. Transparency-free depth ordering.

## Screen-to-Ground Ray Casting
For item placement: cast ray from camera through screen pixel, intersect with Y=0 plane.
Compute ray direction = forward + right*dx + cameraUp*(-dy) where dx,dy are screen offsets from center divided by focal length.
Solve: cam.y + t * rayY = 0 → t = -cam.y / rayY.
World hit point = (cam.x + t*rayX, 0, cam.z + t*rayZ).

## Pitfalls
- `function project()` conflicts with `let project` — use `project3D()` instead
- Elevation must be clamped [5°, 85°] to avoid gimbal lock at 0° or 90°
- Items near camera edges may project outside canvas bounds — check before drawing
- Ground grid lines should be pre-projected and drawn with lineTo in screen space
