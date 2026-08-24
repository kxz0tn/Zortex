# ZORTEX v1.1.5

**3D inertial space survival.** A single-file browser game. Landscape on every device.

**[Play now](https://kxz0tn.github.io/Zortex/)** — desktop, phone, and tablet (rotate to landscape).

Pilot a spacecraft through an unbounded black void. Drift with real inertia. Survive asteroid fields. Engage hostile aliens. You have three nukes.

Open `Zortex_v1.1.5.html` in a current Chromium, Safari, or Firefox browser. No install. No build. On a phone or tablet: rotate to **landscape** first. Portrait is locked out on purpose.

**Version:** 1.1.5  
**Original (v1.1):** [github.com/kxz0tn/Zortex](https://github.com/kxz0tn/Zortex) — Pygame 2D  
**This build:** Three.js + Web Audio, cyberpunk black & white

---

## How to play

1. Double-click `Zortex_v1.1.5.html`, or serve the folder and open the file.
2. Click or tap **BUCKLE UP**.
3. A network connection is required on first load for the Three.js CDN (`three@0.160.1`) and Google Fonts. After that the browser cache is enough.
4. Press **F** for fullscreen (desktop).

### Controls

| Action | Desktop | Touch (landscape) |
|---|---|---|
| Rotate | **A / D** or **← / →** | Drag the **VECTOR** pad left / right |
| Thrust | **W** or **↑** | Drag the **VECTOR** pad **up** |
| Fire laser | **SPACE** (tap, 155 ms cooldown) | Tap **FIRE** |
| Nuke mode | **N** (3 per run) | Tap **NUKE** (button fills when armed) |
| Aim nuke lock | Move the mouse | Drag on empty space (reticle follows the finger). Default is screen center. |
| Launch nuke | Lock target + **L** | Lock target + **LAUNCH** (glows when locked) |
| Cancel nuke | **N** again | **NUKE** again |
| Pause | **ESC** | **PAUSE** (top center) or **ESC** |
| Pause menu | RESUME / RESTART / QUIT TO MENU | Same buttons (tap) |
| Menus | **↑ ↓** + **Enter** / **Space** | Tap the option |
| Restart | **R** on Game Over | **RESTART** |
| Fullscreen | **F** | Requested on **BUCKLE UP** where the browser allows it |

Right yaws right. Left yaws left. The ship is not boxed in — fly any direction. It keeps drifting after you release thrust. That is the game.

On touch, the VECTOR pad is analog: small deflections turn or thrust gently; a committed drag matches the desktop rates (`6.5°` yaw and `0.28` accel per tick). Keyboard flight on desktop is unchanged (full rate while a key is held). FIRE is tap-to-shot (same 155 ms cooldown as Space). NUKE then drag-to-aim is the touch equivalent of N then mouse; LAUNCH is L.

### Platform

- **Landscape only.** Portrait is blocked by a full-screen rotate gate (CSS + JS). Physics does not run while the gate is up.
- **Phones and tablets.** Coarse-pointer / no-hover devices, iPadOS desktop-mode, and `navigator.userAgentData.mobile` get the on-screen VECTOR pad, FIRE, NUKE, LAUNCH, and PAUSE. On supported browsers the first play gesture also requests fullscreen so the OS can honor a landscape lock.
- **Pause.** ESC or PAUSE. The run also pauses if the tab or app is sent to the background.
- **iOS.** Safari does not expose `screen.orientation.lock`. Landscape is enforced by the rotate gate, not by the OS. That is an OS limit, not a reduced game.

### Scoring

| Event | Points |
|---|---|
| Asteroid (laser) | 15 |
| Devil alien (laser) | 90 |
| Asteroid (nuke) | 40 |
| Devil alien (nuke) | 160 |

Spawn rates accelerate with score, matching v1.1:

- Asteroids every `max(1100 − score/100, 450)` ms
- Aliens every `max(9800 − score/60, 3800)` ms

Three lives. Contact with an asteroid, an alien, or an alien bolt costs one life.

---

## What v1.1.5 is

Zortex v1.1 was a fullscreen Pygame shooter: inertial ship, wrapping rocks, pursuit aliens, tap-fire lasers, a three-nuke mouse-lock weapon.

v1.1.5 is that game in 3D, not a different fantasy.

- **Physics first.** The 60 Hz integrator is the v1.1 integrator. Acceleration `0.28`, max speed `7.5`, yaw `6.5°` per tick, damping `0.982`. 1 world unit = 1 original pixel. The ship is not clamped; space is open and the asteroid field streams around you.
- **Visuals second.** High-contrast monochrome. Scanlines, vignette, holographic wireframes. No neon cyan / magenta from v1.1.
- **Nukes elevated, not replaced.** Still 3 per run, still N then L. Missiles now home. Kill set is still the locked target only.
- **Collisions elevated, not replaced.** Sphere tests use the original radii. Rocks now exchange momentum. Destruction throws physical fragments (no extra score, no extra damage).

The constant-by-constant map lives in [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md).

---

## Originality / copyright

Everything you see and hear in v1.1.5 is original to this file, except the runtime libraries listed in [`NOTICE`](NOTICE).

- **Geometry** is built at runtime (dagger interceptor, rocky displaced asteroids, predator aliens, heavy nuke).
- **Particles, shockwaves, starfield** are procedural.
- **Audio is 100% synthesized** with the Web Audio API. No files, no sample packs, no codecs, no third-party sound.
- Runtime CDNs: **Three.js r160** (MIT) and **Orbitron / Share Tech Mono** (SIL OFL 1.1). See NOTICE.

Do not drop external assets into this project. If you fork it, keep audio procedural. If you vendor `three.min.js` or embed the font files, keep their licenses next to them.

---

## Version history

| Version | Date | Notes |
|---|---|---|
| v1.0 | 2026 | Initial Pygame release |
| v1.1 | 11 Apr 2026 | Inertia, working nukes, bullet edge fix, clamped ship, numbered lives |
| **v1.1.5** | 24 Aug 2026 | 3D browser rebuild. Free flight, landscape/touch, VECTOR pad, pause menu. |

---

## Physics notes (short)

Tick = 1/60 s, decoupled from rendering.

```
if thrust:  v += 0.28 * heading
if Left:    angle -= 6.5°     # chase-cam corrected
if Right:   angle += 6.5°
v         *= 0.982
if |v| > 7.5: v = v / |v| * 7.5
position  += v                # no clamp, no wrap
```

Asteroids still curve: heading is incremented by `spin ∈ [−3.8, 3.8]` deg/tick. They no longer wrap a box — far rocks recycle onto a ring around the ship (420–1550 units).

Documented elevations (do not change identity):

- Free flight (unbounded XZ). Streaming asteroid field.
- Chase-cam yaw polarity (Right = yaw right)
- 0.9 s invulnerability after a life loss
- Homing nukes at the original 19 u/tick
- Asteroid–asteroid and asteroid–ship momentum transfer
- Live caps: 48 asteroids, 10 aliens
- Landscape-only on phones/tablets, with a rotate-device gate
- Touch VECTOR pad + FIRE / NUKE / LAUNCH on coarse-pointer devices
- Pause menu on ESC (does not dump to the title)

---

## Files

| Path | Role |
|---|---|
| `Zortex_v1.1.5.html` | The game. HTML + CSS + JS. |
| `README.md` | Player / contributor entry. |
| `LICENSE` | MIT for this project's own code |
| `NOTICE` | Third-party licenses: three.js (MIT), Orbitron and Share Tech Mono (SIL OFL 1.1) |
| `docs/TECHNICAL_DESIGN.md` | System map and constant ledger |

---

## License

This project's own code is MIT (see `LICENSE`). Third-party runtime dependencies are listed in `NOTICE`.

---

Developed from Zortex by **kxz0tn**, originally with help from Grok (xAI).  
v1.1.5 is a 3D evolution of that work.
