# Air Hockey Lab — LLM Chat History

**Tool used:** Antigravity IDE (powered by Google DeepMind) — Claude Sonnet 4.6 (Thinking)  
**Date:** 2026-10-11  
**Project:** `02_air_hockey` — Single-topic Air Hockey game in Pygame

---

## Exchange 1

### 👤 User Prompt
> *"read the code and the read me and tell me what are the causes of the bug?"*

### 🤖 AI Response (Analysis)

The AI read all source files:
- `main.py`
- `game/game_engine.py`
- `game/collisions.py`
- `game/paddle.py`
- `game/puck.py`
- `game/ai.py`
- `game/renderer.py`
- `README.md`

It then identified **one deliberate bug** and **three missing features**:

---

#### 🐛 The Deliberate Bug — Task 1: Broken Puck–Paddle Collision

**Location:** `game/collisions.py`, function `handle_paddle_collision()`

**Buggy code:**
```python
if distance < puck.radius + paddle.radius:
    puck.vx = -puck.vx   # ← BUG
    return True
```

**Root Causes identified:**

1. **Only `vx` is flipped — `vy` is completely ignored.**
   A real collision reflects the puck along the **normal vector** from the paddle center to the puck center. Flipping only `vx` means angled hits (e.g., puck hits the top/bottom edge of a paddle) produce a completely wrong rebound direction.

2. **No positional correction (tunneling / "getting stuck").**
   After detecting overlap, the code never *pushes the puck outside* the paddle. So on the next frame, the puck is still overlapping, `vx` gets flipped *again* (back to the original direction), and the puck tunnels right through — or vibrates inside the paddle indefinitely.

3. **The reflection doesn't account for the angle of impact.**
   Proper circle-to-circle reflection uses the collision normal `(dx/dist, dy/dist)` to compute the reflected velocity component along that normal, not a simple axis flip.

---

#### ❌ Missing Features (Tasks 2–4)

| Task | What's missing | File / Lines |
|---|---|---|
| **Task 2** — Scoring | No score counters; `_handle_goals` calls `_reset_puck()` but never increments any score | `game_engine.py` L72–84 |
| **Task 3** — 30-sec timer | No timer logic anywhere; the game runs indefinitely | `game_engine.py` |
| **Task 4** — Puck reset | `_reset_puck()` sets velocity to `(0, 0)` — the puck **sits motionless** forever after a goal instead of re-launching | `game_engine.py` L86–89 |

The puck reset bug (Task 4) was specifically: `_reset_puck` zeroed out velocity and never called `_launch_puck()` again, so the game effectively froze after the first goal.

---

## Exchange 2

### 👤 User Prompt
> *"implement the fixes"*

### 🤖 AI Response (Implementation)

The AI implemented all four fixes across three files.

---

### Fix 1 — `game/collisions.py` (Task 1: Collision Bug)

**Before:**
```python
def handle_paddle_collision(puck, paddle):
    """
    If the puck overlaps the paddle, bounce it off.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    if distance < puck.radius + paddle.radius:
        puck.vx = -puck.vx
        return True

    return False
```

**After:**
```python
def handle_paddle_collision(puck, paddle):
    """
    If the puck overlaps the paddle, reflect its velocity along the
    collision normal (the vector from paddle centre to puck centre)
    and push the puck outside the paddle so it can't tunnel or stick.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    # Avoid division-by-zero if centres perfectly overlap
    if distance == 0:
        distance = 0.001
        dx, dy = 1, 0

    min_dist = puck.radius + paddle.radius
    if distance < min_dist:
        # 1. Collision normal (unit vector pointing from paddle → puck)
        nx = dx / distance
        ny = dy / distance

        # 2. Reflect velocity along the normal:
        #    v' = v - 2(v·n)n
        dot = puck.vx * nx + puck.vy * ny
        puck.vx -= 2 * dot * nx
        puck.vy -= 2 * dot * ny

        # 3. Push puck outside the paddle so next frame won't re-trigger
        overlap = min_dist - distance
        puck.x += nx * overlap
        puck.y += ny * overlap

        return True

    return False
```

**What changed and why:**
- **Computed the collision normal** as a unit vector pointing from the paddle center to the puck center.
- **Used the physics reflection formula** `v' = v - 2(v·n)n` so both `vx` and `vy` are updated correctly for any angle of impact.
- **Added positional correction** — after a collision, the puck is pushed outside the paddle by the overlap distance so that the next frame won't re-detect a collision and flip the velocity again (the tunneling/sticking bug).
- **Added a zero-distance guard** to prevent division-by-zero if the centers exactly coincide.

---

### Fix 2 — `game/game_engine.py` (Tasks 2, 3, 4)

The entire `game_engine.py` was rewritten to incorporate all three remaining tasks. Key changes:

#### Task 2 — Match Scoring
```python
# Added in __init__:
self.player_score = 0
self.computer_score = 0

# Added in _handle_goals():
if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
    self.computer_score += 1   # left wall = computer scores
    self._reset_puck()

# ...and for the right wall:
if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
    self.player_score += 1     # right wall = player scores
    self._reset_puck()

# Added in draw():
renderer.draw_text(surface, font, f"{self.player_score}",   (WIDTH // 4,      MARGIN + 4))
renderer.draw_text(surface, font, f"{self.computer_score}", (3 * WIDTH // 4,  MARGIN + 4))
```

#### Task 3 — 30-Second Match Timer
```python
# Added constants:
FPS = 60
MATCH_DURATION = 30

# Added in __init__:
self.frames_remaining = MATCH_DURATION * FPS
self.match_over = False
self.winner_text = ""

# Added in update():
self.frames_remaining -= 1
if self.frames_remaining <= 0:
    self._end_match()
    return

# New method:
def _end_match(self):
    self.match_over = True
    self.puck.vx = 0
    self.puck.vy = 0
    if self.player_score > self.computer_score:
        self.winner_text = "You Win!"
    elif self.computer_score > self.player_score:
        self.winner_text = "Computer Wins!"
    else:
        self.winner_text = "Draw!"

# Added in draw():
renderer.draw_text(surface, font, f"{self.seconds_remaining}s", (WIDTH // 2 - 16, MARGIN + 4))
if self.match_over:
    renderer.draw_banner(surface, font, self.winner_text)
```

#### Task 4 — Puck Re-launch After Goals
```python
# Before (puck sat motionless after a goal):
def _reset_puck(self):
    self.puck.x, self.puck.y = WIDTH / 2, HEIGHT / 2
    self.puck.vx = 0
    self.puck.vy = 0

# After (puck immediately re-launches):
def _reset_puck(self):
    """Re-centre and immediately re-launch the puck (Task 4)."""
    self.puck.x, self.puck.y = WIDTH / 2, HEIGHT / 2
    self._launch_puck()   # <- the missing call
```

---

### Bonus Fix — `main.py` (R key restart)

The README stated *"Press R at any time to restart"* but this was never implemented.

**Added:**
```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        engine = GameEngine()   # <- restart by creating fresh engine
```

---

## Exchange 3

### 👤 User Prompt
> *"uhh when i hit the ball it sometimes rotates fully and goes behind the bat if that makes sense the bat rotates 180 so ball doesnt ricochet off of it"*

### 🤖 AI Response (Analysis & Fix)

**Root cause identified — the 180° "through the bat" bug:**

The reflection formula `v' = v - 2(v·n)n` was being applied **unconditionally**, even when the puck was already moving *away* from the paddle. This caused the following sequence:

1. Puck overlaps the paddle at high speed or from a sharp angle.
2. Positional correction pushes the puck out — but sometimes to the wrong side of the paddle center.
3. On the next frame, the normal vector `n` now points in the opposite direction.
4. The dot product `v·n` is now **positive** (puck moving away), but the formula still runs and **reverses the outgoing velocity back into the paddle** — producing the 180° flip the user observed.

**The fix — separating-axis guard (`dot < 0`):**

The collision normal `n` points *from the paddle center toward the puck*. If the puck's velocity is pointing in the opposite direction (toward the paddle), the dot product is **negative**. If it's positive, the puck is already flying away and should not be reflected again.

**Before:**
```python
# 2. Reflect velocity along the normal:
#    v' = v - 2(v·n)n
dot = puck.vx * nx + puck.vy * ny
puck.vx -= 2 * dot * nx
puck.vy -= 2 * dot * ny
```

**After:**
```python
# 2. Reflect velocity along the normal ONLY if puck is moving
#    toward the paddle (dot < 0). If it's already separating,
#    skip the flip — just let the positional push-out do its job.
#    Without this guard the formula reverses an outgoing puck
#    back into the paddle, producing the 180° "through the bat" bug.
dot = puck.vx * nx + puck.vy * ny
if dot < 0:
    puck.vx -= 2 * dot * nx
    puck.vy -= 2 * dot * ny
```

The positional push-out (step 3) still always runs so the puck is never left inside the paddle.

---

## Summary of All Changes

| File | Change | Task |
|---|---|---|
| `game/collisions.py` | Replaced axis-flip with proper vector reflection + positional correction | Task 1 |
| `game/game_engine.py` | Added `player_score`, `computer_score`, incremented on goal, drawn on screen | Task 2 |
| `game/game_engine.py` | Added `frames_remaining` countdown, `_end_match()`, winner/draw banner | Task 3 |
| `game/game_engine.py` | `_reset_puck()` now calls `_launch_puck()` instead of setting velocity to zero | Task 4 |
| `main.py` | Wired `pygame.K_r` event to create a fresh `GameEngine` (restart) | Bonus |
| `game/collisions.py` | Added `dot < 0` separating-axis guard to fix 180° "through the bat" flip bug | Exchange 3 |
