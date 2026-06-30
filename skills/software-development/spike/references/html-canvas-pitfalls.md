# HTML Canvas Prototyping Pitfalls

Lessons from building a single-file interactive 3D director console (Canvas 2D, no dependencies).

## 1. Variable/function name conflicts kill JS silently

**Symptom:** Page renders static HTML, all interactive elements visible in DOM snapshot, DevTools console shows zero errors (or empty `js_errors: [{"message":"","source":"exception"}]`), but no JavaScript executes. Click handlers don't fire.

**Root cause:** `let project = { scenes: [], ... }` at global scope followed by `function project(wx, wy, wz) { ... }` causes `Identifier 'project' has already been declared`. The `function` declaration is hoisted above the `let`, and `let` rejects the redeclaration. The entire script block aborts at parse time.

**Detection:** Run `node -e "const fs=require('fs'); const html=fs.readFileSync('file.html','utf8'); const m=html.match(/<script>([\s\S]*?)<\/script>/); if(m) new Function(m[1]);"` — this catches the syntax error immediately.

**Fix:** Rename the function to something distinct (e.g., `project3D`, `worldToScreen`, `proj`).

## 2. Patch-stacking creates scope nesting

**Symptom:** After 3+ `patch` tool calls on the same HTML file, functions that should be global end up indented 2 spaces inside the previous function. Browser console reports `ReferenceError: variableName is not defined` for variables that are clearly at the top of the script.

**Root cause:** Each patch's `old_string` must exactly match the file content. When a patch accidentally captures the closing `}` of a function along with the opening of the next function, the replacement text nestles inside the previous scope. The diff looks correct but the resulting file has a silent scope error.

**Detection:** Check indentation — if `function renderCanvas()` starts with 2 spaces instead of 0, it's nested. grep for `^  function` to spot misplaced functions.

**Fix:** After 3+ patches on the same file, **stop patching and rewrite the entire file with `write_file`**. The time saved by patching is false economy when scope bugs lurk.

## 3. Canvas covers interactive elements

**Symptom:** Buttons rendered via `position:absolute; z-index:10` inside a canvas wrapper appear clickable in the DOM but don't respond.

**Root cause:** Usually NOT a z-index issue (the canvas is `position:static` by default, so `position:absolute` siblings sit on top). The real causes:
- Forgetting to set `position:absolute` on the toolbar — `position:static` buttons flow behind the canvas
- Canvas explicitly set to `pointer-events: all` (rare)
- Parent container has `overflow:hidden` hiding the toolbar's overflow

**Fix:** Ensure toolbar and minimap use `position:absolute; z-index:10` inside the `position:relative` canvas wrapper. Set canvas to `display:block` (removes inline gap below canvas).

## 4. Canvas 2D perspective projection (no Three.js)

For single-file 3D prototypes that must have zero dependencies:

```
Camera: spherical coords (azimuth, elevation, distance) orbiting a target point
Projection: standard perspective divide through camera basis vectors
```

**Key functions needed:**
- `camPos()` — camera world position from az/el/distance
- `proj(wx, wy, wz)` — project world point to screen {x, y, z, scale}
- `screenToGround(sx, sy)` — ray-plane intersection to find world XZ from screen click

**Camera basis construction:**
1. `forward = normalize(target - camPos)` — looks at origin
2. `right = cross(UP, forward)` — UP = (0,1,0)
3. `camUp = cross(forward, right)`
4. Vector from camera to world point → dot into basis → perspective divide

**Depth sorting:** Sort items by squared distance to camera (far to near = painter's algorithm), not by projected screen Z.

**Ground grid:** Project a regular XZ grid of points at y=0. Draw each line segment by segment to avoid rendering lines that go behind the camera.

## 5. Hit testing in projected space

Don't try to un-project mouse coordinates through the full inverse projection. Instead:
1. Project every item's midpoint to screen coordinates
2. Sort by distance to camera (closest first)
3. Compute the item's on-screen height from its base-to-top projection
4. Check if mouse falls within the item's screen-space bounding box (width = height * 0.35 * scale + padding)

## 6. Interaction model for orbit controls

Default 3D view manipulation:
- Left-drag → orbit (azimuth + elevation)
- Right-drag or Shift+drag → pan ground plane (move camera target)
- Scroll → zoom (change camera distance)
- Touch single-finger → orbit; two-finger → pinch zoom

**Important:** Call `e.preventDefault()` on `wheel` events and touch events. Disable context menu on canvas with `canvas.addEventListener('contextmenu', e => e.preventDefault())`.
