# Perspective Projection Math (Canvas 2D)

## Camera Model

Orbit camera around a target point on the ground plane (y=0):

```
camX = targetX + distance * cos(elevation) * sin(azimuth)
camY = distance * sin(elevation)
camZ = targetZ + distance * cos(elevation) * cos(azimuth)
```

Where:
- `azimuth` = horizontal angle in degrees (0=looking from front, 90=right, 180=back)
- `elevation` = vertical angle in degrees (0=top-down, 90=eye-level at ground)
- `distance` = distance from target to camera
- `(targetX, 0, targetZ)` = point on ground plane the camera looks at

## Projection Pipeline

For a world point (wx, wy, wz):

### Step 1: Camera Basis Vectors

```
forward = normalize(targetX - camX, 0 - camY, targetZ - camZ)
right   = cross(UP=(0,1,0), forward)  // normalized
camUp   = cross(forward, right)
```

### Step 2: World → Camera Space

```
dx = wx - camX
dy = wy - camY  
dz = wz - camZ

camX = dot(dx,dy,dz, right)
camY = dot(dx,dy,dz, camUp)
camZ = dot(dx,dy,dz, forward)  // depth: positive = in front of camera
```

### Step 3: Perspective Divide

```
fovScale = 600 / max(camZ, 1)
screenX = camX * fovScale
screenY = -camY * fovScale  // negate because screen Y is inverted
```

### Step 4: Screen Coordinates

```
canvasX = canvasCenterX + screenX
canvasY = canvasCenterY + screenY
```

The `camZ` value is also used for depth sorting (painter's algorithm).

## Screen-to-Ground Ray Casting

For clicking on the ground plane to place/move items:

1. Compute normalized device coordinates from screen position:
   ```
   ndcX = (screenX - canvasCenterX) / 600
   ndcY = (screenY - canvasCenterY) / 600
   ```

2. Build ray direction:
   ```
   ray = forward + right * ndcX + camUp * (-ndcY)
   ```

3. Intersect with y=0 plane:
   ```
   t = -camY / ray.y   // (if ray.y near 0, ray is parallel to ground)
   hitX = camX + ray.x * t
   hitZ = camZ + ray.z * t
   ```

## Box Face Rendering

For a box at position (x, z) on ground, size (w × d × h), rotation angle θ:

1. Compute 8 corners in world space (rotated):
   ```
   function corner(dx, dy, dz):
     rx = dx*cos(θ) - dz*sin(θ)
     rz = dx*sin(θ) + dz*cos(θ)
     return (x + rx, dy, z + rz)
   ```

2. Project all 8 corners to screen

3. Define 5 visible faces as quads:
   - top:    tl, tr, tb, tt  (projected top corners)
   - front:  bl-base, br-base, tr-top, tt-top
   - right:  br-base, bb-base, tb-top, tr-top
   - left:   bl-base, bt-base, tt-top, tl-top
   - back:   bl-base, bb-base, tb-top, tl-top

4. Sort faces by average camZ (farthest first)

5. Draw each face polygon with slightly different shade

## Performance Notes

- `project()` is called many times per frame (grid lines + all items)
- The ground grid uses ~500 project calls at 300×300 grid with step 25
- Minimize repeated `getCameraPos()` calls — compute once per frame
- Canvas 2D handles this easily at 60fps on modern hardware
