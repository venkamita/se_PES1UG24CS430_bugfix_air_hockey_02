# SE Lab – Air Hockey Bug Fix

**Name:** Sharat Doddihal  
**SRN:** PES1UG24CS430  
**Class:** H  

---

## What Was Done

Started with a broken Pygame Air Hockey game that had one deliberate bug and three unimplemented features.

### Bug Fixed
- **Puck–Paddle Collision (`collisions.py`):** The original code only flipped `vx`, causing wrong rebound angles and the puck getting stuck inside paddles. Fixed using proper circle-to-circle vector reflection (`v' = v - 2(v·n)n`) with positional correction to push the puck out on overlap. Also added a separating-axis guard (`dot < 0`) to prevent a secondary bug where the puck would pass clean through the paddle at high speeds.

### Features Added
- **Scoring (`game_engine.py`):** Tracks player and computer goals, displays both scores on screen during play.
- **30-Second Timer (`game_engine.py`):** Countdown timer displayed during the match; when it hits zero the game freezes and shows "You Win!", "Computer Wins!", or "Draw!" based on the score.
- **Puck Reset (`game_engine.py`):** After every goal the puck is re-centred and immediately re-launched at a random angle — the original code left it motionless.

### Bonus
- **R key restart (`main.py`):** The README mentioned pressing R to restart but it was never wired up — fixed.
