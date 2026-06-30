---
name: canvas-3d-scene-builder
description: Build interactive 3D scene/staging tools as single-file HTML apps using Canvas 2D — no Three.js. Covers perspective projection, orbit controls, hit testing, depth-sorted rendering, and 3D shape drawing (boxes, cylinders, panels). Use when the user asks for a visual director console, staging tool, 3D layout editor, or any interactive 3D scene in a browser without dependencies.
triggers: [canvas-3d-scene-builder, build, html, canvas, three]
platforms: [claude-code, hermes, codex]
---

# Canvas 3D Scene Builder

Build interactive 3D scene tools as single-file HTML applications using Canvas 2D with custom perspective projection. No external dependencies — pure JavaScript.

## When to use

- User wants a 3D staging / director console / layout editor
- User asks for 3D visualization in a browser without installing anything
- User needs interactive 3D scene with orbit/pan/zoom
- User wants to place and move objects in a 3D space visually

## Architecture

Single HTML file with embedded `<style>` and `<script>`:

```
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><style>/* all CSS */</style></head>
<body>
  <!-- layout: tabs + sidebar-left + canvas + sidebar-right + bottom-bar -->
  <script>
    // All state in a single App object to avoid global namespace pollution
    // Camera: azimuth, elevation, distance, targetX, targetZ
    // Items: {id, type, x, z, rotation, scale, ...}
    // Projection: world(x,y,z) → screen(x,y) with painter's algorithm
  </script>
</body>
</html>
```

See `templates/scene-starter.html` for a minimal working starter.

## 3D Projection (Canvas 2D)

### Camera model

Orbit camera around a target point on the ground plane (y=0):

```js
// Camera state
let camAzimuth = 30;    // horizontal orbit angle (0=front, 90=right, 180=back)
let camElevation = 50;  // vertical angle (0=top-down, 90=eye-level)
let camDistance = 600;  // distance from target
let camTargetX = 0;     // look-at point on ground
let camTargetZ = 0;

function camPos() {
  const az = d2r(camAzimuth), el = d2r(camElevation);
  return {
    x: camTargetX + camDistance * Math.cos(el) * Math.sin(az),
    y: camDistance * Math.sin(el),
    z: camTargetZ + camDistance * Math.cos(el) * Math.cos(az)
  };
}
```

### Perspective projection

World point (wx, wy, wz) → screen point (sx, sy) with depth for sorting:

1. Build camera basis vectors: forward (target - camera), right (cross(UP, forward)), camUp (cross(forward, right))
2. Vector from camera to world point
3. Dot into camera basis → (camX, camY, camZ)
4. Perspective divide: `sx = camX * 600 / camZ`, `sy = -camY * 600 / camZ`

Full reference: `references/perspective-projection.md`

### Depth sorting

Sort items by squared distance from camera BEFORE drawing (painter's algorithm, far first):

```js
const cam = camPos();
const items = [...scene.items]
  .map(it => ({it, d: (it.x-cam.x)**2 + (it.z-cam.z)**2}))
  .sort((a,b) => b.d - a.d);
```

## Mouse Controls

### Orbit (primary interaction)
Left-drag = orbit camera around target. Map mouse delta to azimuth/elevation change:

```js
// mousedown: save orbitStart = {az, el, clientX, clientY}
// mousemove:
camAzimuth = orbitStart.az - (e.clientX - orbitStart.x) * 0.5;
camElevation = clamp(orbitStart.el + (e.clientY - orbitStart.y) * 0.3, 5, 85);
```

### Pan (secondary)
Right-drag or Shift+drag = move camera target on ground plane:

```js
camTargetX = panStart.tx - (e.clientX - panStart.x) * (camDistance/400);
camTargetZ = panStart.tz + (e.clientY - panStart.y) * (camDistance/400);
```

### Zoom
Mouse wheel or pinch gesture:

```js
camDistance = clamp(camDistance * (deltaY > 0 ? 1.1 : 0.9), 100, 2000);
```

### Touch
- Single finger = orbit
- Two fingers = pinch zoom

## Hit Testing

Reverse-project screen coordinates to find clicked item:
- Project each item's midpoint to screen
- Sort by distance (closest first)
- Check if screen click falls within the item's projected bounds

For screen-to-ground ray casting (needed for move-tool placement):
- Build ray from camera through screen pixel
- Intersect with y=0 plane
- See `screenToGround` in the starter template

## 3D Shape Drawing

### Character (trapezoid body + circle head)
- Project base (feet at y=0) and top (head at y=height)
- Draw trapezoid between projected base and top
- Circle at projected head position
- Shadow ellipse at base
- Direction arrow on ground plane for rotation

### Box (道具方块)
- Calculate 8 world-space corners of the box (accounting for rotation)
- Project all 8 corners to screen
- Define 5 faces (top, front, right, left, back) as polygons
- Sort faces by average depth, draw far-to-near
- Each face gets a slightly different shade for 3D effect
- Icon rendered on top face

### Cylinder
- Project base center and top center
- Draw bottom ellipse, trapezoid body, top ellipse

### Panel
- Thin vertical rectangle with minimal width

## Pitfalls

### Variable naming conflict
**DO NOT** name a function the same as a state variable. `let project = {}` conflicts with `function project(){}` — the function declaration hoists and shadows the variable. Use distinct names: `let App = {}` for state, `function proj(){}` for projection.

### Function nesting from patches
When patching large code sections with `patch`, ensure the replacement text has correct indentation. Functions defined with extra indentation end up nested inside another function scope and become inaccessible globally. After major patches, verify with `node -e "new Function(scriptText)"` syntax check.

### Canvas event capture
The canvas element captures all mouse events in its area. Overlay buttons (toolbar, minimap) need `position:absolute; z-index:10` inside a `position:relative` parent. Disable context menu on canvas with `canvas.addEventListener('contextmenu', e => e.preventDefault())`.

### Data model for 3D
Items use world coordinates: `x` (left-right), `z` (forward-back), `rotation` (world-space facing direction in degrees). The `y` coordinate is height above ground (always 0 for feet, `height` for top). Old 2D data with `{x, y, z}` where `z` was depth needs migration to `{x, z, height}`.

### Props need visible geometry
Users expect props to show actual 3D shapes (box, cylinder, panel) — not just an icon on a flat rectangle. Implement proper face rendering with depth sorting so the shape reads as 3D from any angle.
