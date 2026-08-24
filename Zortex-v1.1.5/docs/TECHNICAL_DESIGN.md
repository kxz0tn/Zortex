# Zortex v1.1.5 — Technical Design Document

Living document. Maps every Zortex v1.1 (Pygame 2D) system onto the
v1.1.5 browser 3D implementation. Physics is the source of truth.

**Version:** 1.1.5
**Source analyzed:** `https://github.com/kxz0tn/Zortex` → `Zortex v1.1/Zortex v1.1.py` (589 lines)
**Playable deliverable:** `Zortex_v1.1.5.html` (single file)
**Aesthetic:** Cyberpunk black & white. No neon cyan/magenta from v1.1.
**Audio / assets:** 100% original. Procedural geometry + Web Audio API synthesis only.

---

## 0. Reconnaissance Summary

Zortex v1.1 is a fullscreen 60 Hz Pygame arcade survival shooter:

- Inertial ship (accelerate along heading, damp, clamp speed, no screen wrap)
- Irregular spinning asteroids that wrap and curve (heading += spin each tick)
- Pursuit “Devil” aliens that wrap and fire at the ship’s current position
- Tap-to-fire lasers (155 ms cooldown)
- 3 nukes / game, N toggles targeting, mouse hover + L launches
- Score, 3 lives, menu / controls / game-over states
- Particle explosions

v1.1.5 elevates this into a third-person 3D inertial space game without
replacing the fantasy: same numbers, same loop, same weapons, same spawn
curves. Geometry, lighting, camera, collisions, fragments, and audio are
the 3D evolution.

---

## 1. Coordinate & Time Mapping

| Quantity | v1.1 | v1.1.5 |
|---|---|---|
| Tick | `clock.tick(60)` → 1 frame | Fixed physics tick `DT = 1/60` s, decoupled from render |
| Spatial unit | 1 pixel | **1 world unit = 1 original pixel** (zero conversion error) |
| Play plane | Screen XY, Y down | World XZ, Y up. `x → x`, `y → z` |
| Origin | Top-left (0,0) | Ship spawn `(0,0,0)`. Unbounded XZ. |
| Arena | Native fullscreen resolution | **Removed in Iteration 2.** Streaming field around the ship (`FIELD_NEAR` 420, `FIELD_FAR` 1550, `FIELD_CULL` 2100). |
| Heading | Degrees, `0° = +X (right)`, `-90° = up` | Identical degree space. Forward = `(cos θ, 0, sin θ)` |
| Camera | Top-down blit | Chase camera on XZ, +Y offset, momentum lag, trauma shake |

Iteration 1 used a fixed 1920×1080 box so physics was not monitor-sized.
Iteration 2 deletes that box. The ship is free. Threat density is kept by
recycling rocks onto a ring around the player instead of wrapping a rectangle.

---

## 2. Constant Ledger (v1.1 → v1.1.5)

Every number below is copied from `Zortex v1.1.py` unless marked ELEVATION.

### 2.1 Time / loop

| Name | v1.1 | v1.1.5 |
|---|---|---|
| FPS / tick | 60 | `TICK_HZ = 60`, `DT = 1/60` |
| Render | locked 60 | `requestAnimationFrame` (uncapped render, fixed physics) |

### 2.2 Ship (`Spaceship`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Spawn | `(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)` | `(960, 0, 540)` |
| `angle` | `-90` deg | `-90` deg |
| `vx, vy` | 0 | `vx, vz` 0; `vy` exists (6DOF foundation, planar constraint) |
| `max_speed` | `7.5` px/tick | `7.5` u/tick on XZ |
| `acceleration` | `0.28` px/tick² | `0.28` u/tick² along heading |
| `rotation_speed` | `6.5` deg/tick | `6.5` deg/tick yaw (A = +, D = −) |
| Linear damping | `0.982` / tick | `0.982` / tick on `vx, vz` |
| Speed clamp | `hypot(vx,vy) > 7.5` rescale | identical on `(vx, vz)` |
| Position integrate | `x += vx` | `x += vx`, `z += vz`, `y += vy` |
| Bounds | clamp to screen, **no wrap** | **Iteration 2: unbounded.** No clamp, no wrap. |
| `shoot_delay` | `155` ms | `155` ms |
| `lives` | 3 | 3 |
| `nukes` | 3 | 3 |
| `radius` | 27 | 27 |
| Fire input | `KEYDOWN` Space (tap, not hold) | identical |
| Y / 6DOF | n/a | `vy` damped `0.86`/tick; spring `y += (0-y)*0.18`. Roll/pitch are visual angular states with their own damping. Gameplay yaw remains the only control axis. |
| Mass (ELEVATION) | n/a | `12` — used only for momentum transfer |
| I-frames (ELEVATION) | none | `54` ticks (0.9 s) after a life loss. Required: 3D chase cam hides off-axis threats the original top-down view showed. |

### 2.3 Player bullet (`Bullet`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Speed | 14 px/tick | 14 u/tick along heading |
| Life | 70 ticks | 70 ticks |
| Trail length | 10 | 10 samples |
| Visual radius | 6 | 6 |
| vs asteroid collision pad | 7 | 7 |
| vs alien collision pad | 9 | 9 |
| Vertical (orig Y) | despawn off top/bottom | despawn `z < 0` or `z > ARENA_D` |
| Horizontal (orig X) | wrap | **Iteration 2:** no wrap; despawn on life |

### 2.4 Asteroid (`Asteroid`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| `size` | `randint(34, 65)` | same, used as sphere radius |
| Spawn X | left `[-110,-40]` or right `[W+40, W+110]` | identical vs `ARENA_W` |
| Spawn Y | `randint(-80, H+80)` | spawn Z identical vs `ARENA_D` |
| Spawn Y (3D) | n/a | `y ∈ [-22, 22]` (slab, visual depth) |
| `angle` (heading) | `uniform(0,360)` | same |
| `speed` | `uniform(1.1, 2.9)` | same |
| `spin` | `uniform(-3.8, 3.8)` deg/tick | same — **added to movement heading every tick** (curved trajectories; this is not “visual only”) |
| Shape | 12-gon, radius `size * U(0.65,1.2)`, angle jitter ±25° | displaced icosahedron, vertex scale `U(0.65, 1.2)` |
| Wrap | both axes | **Iteration 2:** no wrap. Recycle onto spawn ring if `dist > FIELD_CULL` |
| Visual tumble (ELEVATION) | implied by heading | independent `ω` vector, rad/tick |
| Mass (ELEVATION) | n/a | `0.012 * size³` |
| Initial count | 5 | 5 |
| Cap (ELEVATION) | unbounded | 48 live asteroids (GPU budget; original could accumulate 200+) |

### 2.5 Alien (`Alien`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Spawn X | `0` or `SCREEN_WIDTH` | `0` or `ARENA_W` |
| Spawn Y | `randint(50, H-50)` | spawn Z identical |
| `size` | 31 | 31 |
| `speed` | 2.6 px/tick (direct pursuit, no inertia) | 2.6 u/tick, same steering: `pos += normalize(ship-pos)*speed` |
| Wrap | both axes | **Iteration 2:** no wrap. Despawn if `dist > FIELD_CULL * 1.15` |
| `shoot_delay` | `randint(1000, 2400)` ms | same |
| Aim | current ship position (no lead) | same |
| Cap (ELEVATION) | unbounded | 10 live aliens |

### 2.6 Alien bullet (`AlienBullet`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Speed | 9 px/tick | 9 u/tick |
| Life | 90 ticks | 90 ticks |
| Visual radius | 7 | 7 |
| vs ship collision | `hypot < 26` | 26 (kept, not replaced by `ship.radius`) |
| Wrap | both axes | **Iteration 2:** no wrap; despawn on life |

### 2.7 Nuke (`NukeMissile`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Count | 3 per game, no refill | 3 |
| Mode toggle | N (if nukes > 0) | N |
| Empty warning | 90 ticks `"OUT OF NUKES!"` | 90 ticks |
| Lock test | `hypot(obj, mouse) < obj.size + 70` | ray vs sphere of radius `size + 70` |
| Launch | L while locked | L while locked |
| Speed | 19 px/tick | 19 u/tick |
| Life | 130 ticks | 130 ticks |
| Detonate distance | 20 px to **launch-time** `(tx,ty)` | 20 u to target (live position if still alive) |
| Guidance | straight line at launch heading | **ELEVATION:** proportional retarget each tick (homing). Speed magnitude unchanged. If target dies, fly to last known position. |
| Kill set | locked object only (no splash) | locked object only. Shockwave is visual. |
| Score asteroid | +40 | +40 |
| Score alien | +160 | +160 |

### 2.8 Scoring & spawn curves

| Event | v1.1 | v1.1.5 |
|---|---|---|
| Laser vs asteroid | +15 | +15 |
| Laser vs alien | +90 | +90 |
| Nuke vs asteroid | +40 | +40 |
| Nuke vs alien | +160 | +160 |
| Asteroid spawn | `max(1100 - score//100, 450)` ms | identical |
| Alien spawn | `max(9800 - score//60, 3800)` ms | identical |
| Life loss | asteroid / alien / alien-bullet contact | same three sources |

### 2.9 Particles (`Particle` / `create_explosion`)

| Name | v1.1 | v1.1.5 |
|---|---|---|
| Size | `randint(4,14)` | same (pixel-equivalent point size) |
| Speed | `uniform(2,10)` | same, random unit sphere direction |
| Life | `randint(30,65)` ticks | same |
| Damping | `0.96` / tick | `0.96` / tick |
| Counts | asteroid 42, alien 55, ship-hit 30, ship-asteroid 40, ship-alien 50, nuke 140+100 | same counts (monochrome) |
| Fragments (ELEVATION) | none | 5–8 rigid shards, 1.35 s, inherit velocity + radial impulse, **no damage / no score** |

### 2.10 Collision radii (copied)

| Pair | Test |
|---|---|
| Ship–asteroid | `hypot < asteroid.size + 27` |
| Ship–alien | `hypot < 31 + 27` |
| Ship–alien bullet | `hypot < 26` |
| Bullet–asteroid | `hypot < asteroid.size + 7` |
| Bullet–alien | `hypot < 31 + 9` |
| Nuke–target | `hypot < 20` to aim point |

v1.1 used 2D hypot. v1.1.5 uses 3D hypot on `(x,y,z)` with `y` near 0, so
planar contacts match. Asteroid Y slab (±22) is inside typical `size`.

---

## 3. System Map

### 3.1 Physics core

Per tick, ship:

```
if thrust:  v += accel * heading
if A:       angle += 6.5
if D:       angle -= 6.5
v.xz      *= 0.982
if |v.xz| > 7.5: v.xz = v.xz / |v.xz| * 7.5
p.xz      += v.xz
p.xz      += v.xz          # Iteration 2: no clamp
```

This is the v1.1 integrator, not an approximation of it.

**Momentum transfer (ELEVATION, additive):** sphere–sphere impulse

```
n = (pb - pa) / |pb - pa|
vn = (va - vb) · n          # approaching if vn > 0
j  = -(1+e) vn / (1/ma + 1/mb)
va += (j / ma) n
vb -= (j / mb) n
```

Restitution `e = 0.38`. Applied asteroid–asteroid and asteroid–ship
(ship still loses a life and the asteroid is still destroyed — identity
rule — but the ship receives knockback). Torque on asteroids:
`ω += (r × jn) / I`, `I = 0.4 m r²`.

### 3.2 Camera

Chase / cockpit hybrid:

- Desired position = ship − heading * 126 + up * 58 − velocity * 5.5
- Look point = ship + heading * 48 + velocity * 2.4
- Exponential follow `1 - exp(-λ Δt)`, `λ = 7.2` (locked to momentum, not glued)
- Roll from yaw input and lateral velocity (visual)
- FOV 62°, punch to 68° while thrusting, 74° on nuke detonation
- Trauma shake: damped noise offset on hit / nuke

### 3.3 Combat identity

- Lasers are kinematic (no mass), aliens seek without inertia — v1.1 behavior.
- Do not add weapon types, shields, pickups, or radar.
- Difficulty is only the two spawn-interval formulas.

### 3.4 UI / states

States: `boot → menu ⇄ controls`, `menu → playing ⇄ paused ⇄ playing`, `playing → game_over`, `paused → menu` (QUIT), `game_over → menu`. ESC while playing opens the pause menu (RESUME / RESTART / QUIT TO MENU). It does not dump to the title.

Labels preserved: **BUCKLE UP**, **CONTROLS**, **OUT OF NUKES!**, **GAME OVER**,
`SCORE ######`, `LIVES n`, `NUKES n`. Added (HUD only): `VEL` (XZ speed, original units) and `HDG`.

Palette: `#000000` void, `#ffffff` signal, `#9a9a9a` dim, `#1a1a1a` fill.
Scanline + vignette overlays. No cyan, magenta, purple, orange.

### 3.5 Audio (see also §6)

Web Audio API only. No files, no samples, no codecs. Synthesis recipes
are implemented in `AudioEngine` inside the HTML file and summarized in
§6 so the work remains copyright-clean forever.

---

## 4. Visual Language

- High-contrast monochrome. Lambert/basic materials, white `EdgesGeometry`.
- Asteroids: charcoal fill, white wire.
- Ship: black hull, white edge, additive white engine.
- Aliens: faceted delta, two white emissive eyes (the v1.1 “cyan eyes” become white).
- Lasers: additive white needles + trail.
- Alien bolts: dimmer white spheres.
- Nuke: white dart, long trail, expanding shock ring on detonation.
- Starfield: 1600 points, parallax via camera only (v1.1 used `bg_offset * star.spd`).
- CRT: CSS scanlines, vignette, occasional HUD glitch on damage.

---

## 5. Performance Budget

| Item | Cap |
|---|---|
| Asteroids | 48 |
| Aliens | 10 |
| Player bullets | ~8 (life-limited) |
| Alien bullets | ~20 |
| Particles | 900 pooled |
| Fragments | 64 |
| Pixel ratio | `min(devicePixelRatio, 2)` |
| Target | 60 fps mid-range integrated GPU |

---

## 6. Procedural Audio Recipes (original)

All voices start from oscillators and a 1-second white-noise buffer generated
at runtime (`Math.random()`). Nothing is loaded from disk or network.

| Voice | Method |
|---|---|
| Ambient drone | Two detuned sines (46 Hz, 46.7 Hz) + brown-ish noise through a 180 Hz lowpass. Slow gain LFO 0.04 Hz. |
| Thrust | Noise → bandpass 700 Hz Q=3, plus 58 Hz saw through 320 Hz lowpass. Gain gated by thrust flag, 40 ms attack / 180 ms release. |
| Laser | 40 ms square 1480→420 Hz exponential ramp + short noise click, highpass 900 Hz. |
| Asteroid impact | 80 ms noise burst through lowpass 500 Hz + sine 90→40 Hz. |
| Alien shot | 90 ms square 620→180 Hz, slight duty change via gain tremolo. |
| Nuke launch | 280 ms noise whoosh (bandpass sweep 200→1800 Hz) + rising saw 80→240 Hz. |
| Nuke explosion | Layered: 0.9 s noise, 55 Hz sine decay, 22 Hz sub sine, sparse 3-partial metallic ring (harmonics 1, 1.41, 2.15 — inharmonic by design). |
| UI click | 12 ms impulse through 2 kHz bandpass. |
| Life loss | 200 ms noise + falling sine 300→70 Hz. |

Master chain: gain 0.42 → dynamics compressor (threshold −16 dB, ratio 5).

---

## 7. Explicit Non-Goals

- No new weapons, shops, levels, or narrative.
- No third-party models, textures, fonts-as-files, or audio packs.
- No cyan/magenta “neon cyberpunk” leftover from v1.1.
- No arcade-style instant stop / twin-stick / 6DOF flight as the control scheme.
- No splash damage on nukes.
- No high-score persistence (v1.1 had none).

---

## 8. Controls (player-facing, identity-preserving)

| Action | Desktop | Touch (landscape) |
|---|---|---|
| Rotate left / right | A / D or ← / → | VECTOR pad, horizontal |
| Thrust | W or ↑ | VECTOR pad, up |
| Fire laser | SPACE (tap, 155 ms cooldown) | FIRE (tap) |
| Nuke mode | N | NUKE |
| Aim nuke lock | Mouse | Drag on empty space (reticle follows). Default screen center. |
| Launch nuke | L (while locked) | LAUNCH (glows when locked) |
| Cancel nuke mode | N again | NUKE again |
| Pause | ESC | PAUSE or ESC |
| Menus | ↑ ↓ + Enter / Space | Tap |
| Restart | R (game over) | RESTART |
| Fullscreen | F | Requested on play where the browser allows it |

VECTOR pad is analog. A committed drag matches the keyboard rates (`SHIP_ROT` 6.5° / tick, `SHIP_ACCEL` 0.28). Keyboard flight on desktop is unchanged (full rate while held).

Q on game over: original quit the process. In-browser it returns to the menu
(cannot close the user’s tab).

---

## 9. File Map

| Path | Role |
|---|---|
| `Zortex_v1.1.5.html` | The game. HTML + CSS + JS. Three.js via CDN. |
| `docs/TECHNICAL_DESIGN.md` | This document. |
| `README.md` | Player / contributor entry. |
| `LICENSE` | MIT for this project's own code. |
| `NOTICE` | Third-party licenses: three.js (MIT r160), Orbitron and Share Tech Mono (SIL OFL 1.1). |

---

## 10. Iteration 2 (23 Aug 2026)

Hardcore pass after first playable. Identity (scores, 60 Hz integrator, weapon set) is unchanged.

### 10.1 Control polarity

v1.1 Pygame used `angle += rot` on Left in a Y-down blit. The chase camera in Y-up XZ inverted the *visual* sense of that sign. Iteration 2 maps:

- Left / A → `angle -= 6.5` → nose goes left in the chase view
- Right / D → `angle += 6.5` → nose goes right

Bank (`lean.rotation.x`) follows the same sense. Keyboard and touch pads share `rotLeft()` / `rotRight()`.

### 10.2 Free flight (no play box)

Removed:

- Ship clamp to 1920×1080
- Arena wire rectangle
- Toroidal wrap on rocks, aliens, bullets, bolts

Added a **streaming local field**:

| Name | Value | Role |
|---|---|---|
| `FIELD_NEAR` | 420 | inner spawn ring around the ship |
| `FIELD_FAR` | 1550 | outer spawn ring |
| `FIELD_CULL` | 2100 | rocks recycle onto the ring; aliens despawn |

Physics numbers (accel, damp, max speed, spin, pursuit 2.6) are unchanged. The world is unbounded; density is maintained by recycling instead of wrapping.

Origin is now `(0,0,0)` instead of arena-center `(960, 0, 540)`.

### 10.3 Visual elevation

- **Ship:** dagger interceptor — cone nose, box fuselage, canted wings, twin nacelles, dorsal fin, white canopy, emissive spine. Not the extruded 2D silhouette.
- **Aliens:** chevron predator — pincer horns, stalk eyes (pulse), wide plates, tail spike.
- **Asteroids:** icosahedron detail 2 → non-indexed, two-octave hash displacement + crater term, vertex colors, flat Phong. No platonic wire overlay.
- Lighting: key + fill + ship-relative rim. FogExp2. Starfield wraps around the camera. Local nav rings follow the ship (orientation only, not a wall).
- Camera: 148 back / 62 up, stronger look-ahead, thrust FOV 60→67.

### 10.4 Platform

- Landscape only. Portrait shows `#rotate-gate` (CSS `@media (orientation: portrait)` plus JS `blocked()` which skips the physics tick). `visualViewport`, `orientationchange`, and `screen.orientation` all reflow the canvas.
- Touch UI when `pointer: coarse` / `hover: none`, iPadOS desktop-mode (`MacIntel` + `maxTouchPoints > 1`), or `navigator.userAgentData.mobile`. VECTOR analog pad (yaw + thrust) + FIRE / NUKE / LAUNCH / PAUSE.
- Nuke lock on touch: drag (or tap) on empty space while armed; reticle follows the finger; default is screen center. Desktop still uses the mouse. Same ray / `visualRadius` lock as PC.
- Pause menu on ESC or PAUSE. Backgrounding the tab also pauses.
- HUD uses Orbitron + Share Tech Mono (SIL OFL 1.1, Google Fonts CDN). Safe-area insets.

### 10.5 Unchanged

Scores 15 / 90 / 40 / 160, spawn formulas, 3 lives, 3 nukes, 155 ms laser, tap-not-hold fire, Web Audio recipes, no splash damage.

---

## 12. Iteration 3

### Nuke lifecycle
Stuck missiles were chasing rocks that **recycled** to the far spawn ring (`FIELD_CULL`) while `worldHas` still returned true, so the seeker never closed. Secondary issue: fuse radius was a flat 20 u against rock radii 34–65, so the dart buried itself in the mesh.

Fixes:
- `target.nukeLocked` prevents recycle / alien despawn while a missile is in flight
- Fuse uses `max(20, target.size * 0.92)` against the **live** body, not the lead point
- Velocity lead `0.65 * eta`, homing gain `0.34`, arming delay 5 ticks, life 160 ticks
- Dart is a cone group with `lookAt` (geometry rotated once — no per-tick `rotateX` accumulation)
- Score still only the locked object, no splash

### UI
`.frame { overflow: hidden }` — letter-spacing on ZORTEX was overflowing and spawning a Windows scrollbar gutter. Panels are compact; no scrollbars.

### Visual
Ship and aliens now use extruded planforms + vertex-color paneling (same language as the rocks). Title uses a monochrome clip-path glitch (luminance split, not neon). Explosions: denser particles, dual shock rings, harder key light, thicker fog.

---

## 11. Phase Log

| Phase | Status | Notes |
|---|---|---|
| 0 Recon & setup | done | Source constants extracted from `Zortex v1.1.py`. |
| 1 3D core + ship | done | Implemented inside the single HTML file. |
| 2 Asteroids + collisions | done | Curved heading+spin preserved. Impulse solver added. |
| 3 Aliens + combat | done | Pursuit + scores 15 / 90. |
| 4 Nukes | done | 3-count, N/L, homing elevation, scores 40 / 160. |
| 5 B&W UI | done | Menu, controls, HUD, game over, scanlines. |
| 6 Procedural audio | done | Web Audio only. |
| 7 Integration / feel | done | State machine, shake, FOV, i-frames, caps. |
| 8 Packaging | done | README, LICENSE, gitignore, this document. |
