---
name: canvas-apps
description: Build interactive single-file HTML canvas applications — drag-and-drop staging tools, director consoles, visual editors. Use when the user asks for a visual canvas tool with draggable elements, pan/zoom, touch gestures, or scene management.
triggers: [canvas-apps, build, html, use]
platforms: [claude-code, hermes, codex]
---

# Canvas Apps — Interactive HTML Canvas Applications

Build self-contained single-file HTML applications using Canvas 2D API. No dependencies, no build step — browser opens the file directly.

## Interaction Model (DEFAULT)

The user prefers a **pan-first** interaction model for canvas apps:

| Action | Effect |
|--------|--------|
| Single finger/mouse drag on canvas | **Pan** (move viewport) |
| Two-finger pinch / mouse wheel | **Zoom** in/out |
| Two-finger drag | Simultaneous zoom + pan |
| Click on element | Select it (show properties) |
| Click on empty space | Deselect |
| Explicit "move" tool mode | Drag to reposition elements |

**Do NOT make single-drag move elements by default.** The canvas is a viewport; panning is the primary navigation gesture. Moving individual elements requires an explicit tool switch (e.g., "拖动物体" button).

## Touch Gesture Reference

```javascript
// Single finger = pan
function onTouchStart(e) {
  if (e.touches.length === 1) {
    touchPanStart = { x: e.touches[0].clientX - panX, y: e.touches[0].clientY - panY };
    isPanning = true;
  }
}

// Two fingers = pinch zoom + pan
function onTouchMove(e) {
  if (e.touches.length === 2) {
    const dist = Math.hypot(dx, dy);
    zoom *= dist / lastTouchDist;
    // Center-point pan
    const cx = (touches[0].clientX + touches[1].clientX) / 2;
    panX = cx - touchPanStart.x;
    panY = cy - touchPanStart.y;
  }
}
```

## Canvas Rendering Patterns

### World-to-screen coordinate transform
```javascript
ctx.save();
ctx.translate(canvas.width/2 + panX, canvas.height/2 + panY);
ctx.scale(zoom, zoom);
// ... draw in world coordinates ...
ctx.restore();
```

### Hit testing in transformed coordinates
```javascript
function canvasToWorld(e) {
  return {
    x: (e.clientX - rect.left - W/2 - panX) / zoom,
    y: (e.clientY - rect.top - H/2 - panY) / zoom,
  };
}
```

### Z-depth for parallax
```javascript
const depthFactor = 1 + item.z * 0.008;  // scale
const adjY = item.y + item.z * 1.5;       // vertical offset
```

### Human figure drawing (simple)
Standing: circle head, rectangle torso, thin arms/legs.
Sitting: circle head, wider torso, horizontal legs.

## Staging/Director Tools (2D Mode)

For director console / staging tools in flat 2D mode, include:
- **Perspective grid** — ground plane grid for spatial reference
- **Horizon line** — dashed line at ~40% of stage height
- **Camera frame** — aspect ratio overlay (16:9, 2.35:1, 4:3, 1:1, 9:16)
- **Rule of thirds** — dotted 3×3 grid inside camera frame
- **Minimap** — top-down overview in corner
- **Z-depth slider** — move elements forward/back (affects scale and Y position)
- **Rotation** — facing direction indicator

## 3D Perspective Mode (orbit camera)

When the user wants 360° rotation, a true 3D space, or "三维空间", use the 3D perspective projection mode. This replaces the 2D pan/zoom/canvas-transform approach with a camera orbiting around a ground plane.

### Camera State

```javascript
let camAzimuth = 30;      // degrees, horizontal orbit (0=front, 90=right, 180=back, 270=left)
let camElevation = 50;    // degrees, 0=top-down, 90=eye-level at ground
let camDistance = 600;    // distance from target
let camTargetX = 0;       // look-at point X on ground plane
let camTargetZ = 0;       // look-at point Z on ground plane
```

### Perspective Projection

World coordinate system: X=right, Y=up (height), Z=forward (depth). Ground plane is Y=0.

Build camera basis vectors (forward, right, camera-up) from spherical coords, then project each world point (wx, wy, wz):

```javascript
function project3D(wx, wy, wz) {
  const cam = getCameraPos();  // from azimuth/elevation/distance
  const forward = normalize(targetX - cam.x, 0 - cam.y, targetZ - cam.z);
  const right = normalize(cross(worldUp, forward));
  const camUp = cross(forward, right);
  
  const dx = wx - cam.x, dy = wy - cam.y, dz = wz - cam.z;
  const camX = dot(dx,dy,dz, right);
  const camY = dot(dx,dy,dz, camUp);
  const camZ = dot(dx,dy,dz, forward);
  
  if (camZ <= 1) return null;  // behind camera
  const fovScale = 600 / camZ;
  return { x: camX * fovScale, y: -camY * fovScale, z: camZ };
}
```

### 3D Character Rendering

Project base (feet at Y=0) and top (head at Y=height) separately:
- Draw shadow ellipse at base
- Draw trapezoid body from base to head
- Draw circle head at top
- Sort items by distance from camera (painter's algorithm, far first)

### 3D Interaction Model

| Action | Effect |
|--------|--------|
| Left mouse drag | **Orbit** (rotate azimuth + elevation) |
| Right mouse drag or Shift+drag | **Pan** ground plane (move targetX/targetZ) |
| Scroll / pinch | **Zoom** (change distance) |
| Click on element | Select it |
| "Move" tool active | Drag element on ground plane (ray-cast to Y=0) |

### Screen-to-Ground Ray Casting

To place/move items by clicking: cast a ray from camera through the screen point, intersect with the Y=0 plane. Compute ray direction from camera basis vectors + screen offset, then solve `cam.y + t * rayY = 0` for `t`. See `references/3d-projection-reference.md` for full math.

### Orbit Buttons

Provide quick-rotate buttons (±45°) in the toolbar so the user can rotate without mouse drags. Implement as `camAzimuth = (camAzimuth + delta) % 360`.

## JS Pitfall: Variable/Function Name Conflict

**Never name a `function` the same as a `let`/`const` variable.** Function declarations are hoisted; a `let project = {}` after `function project()` will throw `Identifier has already been declared` at parse time with a silent blank error in the browser console. Rename the function (e.g., `project3D()`) when the variable name is already taken.

## Templates

- `templates/director-console-2d.html` — 2D pan/zoom director console
- `templates/director-console-3d.html` — 3D orbit camera director console with 360° rotation, perspective projection, ground-plane grid, camera frame overlay, minimap with view cone

Copy and modify as a starting point for visual staging tools.
