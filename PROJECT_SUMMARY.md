# Charlotte's Balance Beam Adventure

## Project Summary

A fun, kid-friendly balance beam game designed for children ages 5-8, featuring a girl gymnast who walks on a balance beam, jumps over obstacles, and performs floor routines.

---

## Platforms

### 1. Kivy Version (Python)
- **File:** `main.py`
- **Platform:** Desktop (Windows, Mac, Linux), can be compiled for iOS/Android
- **Framework:** Kivy (Python 2D game framework)

### 2. Web Version (JavaScript)
- **File:** `docs/index.html`
- **Platform:** Any web browser, including iPhone/iPad Safari
- **Framework:** Phaser.js (HTML5 game framework)
- **Hosting:** GitHub Pages (free)
- **URL:** https://speri-psg.github.io/balance-beam-adventure/

---

## Game Features

### Core Gameplay
- **Auto-walking gymnast:** Player automatically walks forward on the balance beam
- **Tap/Click to jump:** Simple one-button control suitable for young children
- **Obstacles:**
  - Rolling bowling balls (blue with finger holes)
  - Flying pink-winged bees
- **Lives system:** 3 lives per game
- **Scoring:** 100 points per level completed
- **5 progressive levels:** Increasing difficulty with faster balls and more obstacles

### Visual Design
- Colorful cartoon-style graphics
- Girl gymnast character with:
  - Pink leotard
  - Brown ponytail
  - Happy face with rosy cheeks
- Side view while walking
- Front view after landing from jumps
- Animated walking (leg movement)
- Animated jumping

### Super Jump Feature
- When obstacles are close together (ball + bee within 200 pixels)
- Or any obstacle very close (within 100 pixels)
- Player automatically jumps 50% higher to clear both obstacles

---

## Floor Exercise Routine

When the gymnast reaches the end of the balance beam:

1. **Flip down:** Gymnast does a flip off the beam onto the floor
2. **Cartwheels:** Performs cartwheels across the floor
3. **Pause every 3 flips:** Stops and pauses after every 3 cartwheels
4. **Flip back up:** Flips back onto the balance beam
5. **Next level begins**

---

## Personalization

### Name Input
- Player enters their name on the menu screen
- Name is used throughout the game

### Welcome Greeting (Bilingual)
After entering name, displays:
- "Hi [name]! / Hej [name]!" (English + Swedish)
- "Welcome, [name]!"
- "Välkommen, [name]!" (Swedish)
- "Get Ready! / Gör dig redo!"

### Speech Bubbles
The gymnast speaks during gameplay:
- **"Hi [name]!"** (pink) - When facing the player after a jump
- **"Noooo!"** (red) - When hit by an obstacle
- **"Hooray!"** (green) - When completing a level

---

## Sound Effects

All sounds work on iOS/iPad (using HTML5 Audio with generated WAV files):

| Event | Sound |
|-------|-------|
| Walking | Gentle looping background jingle (C major melody) |
| Hit by obstacle | Descending sad tone (400Hz → 150Hz) |
| Level complete | Ascending happy arpeggio (C-E-G) |
| Level complete | Ringing bell (multiple rings based on level) |

### iOS Audio Solution
- Sounds are generated as WAV files in JavaScript
- Audio is unlocked on first user touch (iOS requirement)
- Uses HTML5 `<audio>` element for compatibility

---

## Level Configuration

| Level | Ball Speed | Ball Count | Bee Count | Difficulty |
|-------|------------|------------|-----------|------------|
| 1 | Slow (120) | 2 | 1 | Easy |
| 2 | Medium (140) | 3 | 2 | Easy-Medium |
| 3 | Medium (160) | 3 | 2 | Medium |
| 4 | Fast (180) | 4 | 3 | Medium-Hard |
| 5 | Fast (200) | 4 | 4 | Hard |

---

## Celebration Effects

When a level is completed:
- Confetti particles fall from the sky (multiple colors)
- Gold medals with ribbons fall
- Spinning star decorations
- Bell sound rings (duration increases with level)
- "Hooray!" speech bubble with happy sound

---

## Project Structure

```
BalanceBeamAdventure-Kivy/
├── main.py                    # Kivy version (Python)
├── docs/
│   └── index.html            # Web version (Phaser.js) - GitHub Pages
├── .github/
│   └── workflows/
│       └── build-ios.yml     # iOS build workflow (manual)
├── IOS_DEPLOYMENT.md         # iOS deployment guide
├── PROJECT_SUMMARY.md        # This document
└── README.md                 # Project readme
```

---

## Deployment

### Web Version (Recommended - Free)
1. Code is in `docs/index.html`
2. GitHub Pages serves from the `docs` folder
3. Accessible on any device with a web browser
4. Works on iPhone/iPad Safari

### iOS App Store (Requires $99/year Apple Developer Account)
1. Manual GitHub Actions workflow available
2. Requires Apple Developer certificates configured as GitHub secrets
3. See `IOS_DEPLOYMENT.md` for detailed instructions

---

## Technical Implementation

### Kivy Version (main.py)
- `Player` class with multiple drawing methods:
  - `drawPlayerSide()` - Walking view
  - `drawPlayerFront()` - Facing player after jump
  - `draw_flipping()` - Flip animation
  - `draw_cartwheel()` - Cartwheel animation
- `BowlingBall` class - Rolling obstacle with rotation
- `Bee` class - Flying obstacle with wing animation
- `GameWidget` - Main game logic and collision detection
- `ConfettiSystem` - Particle effects with medals
- `BellSound` - Level-based bell duration

### Web Version (docs/index.html)
- `MenuScene` - Title screen with name input
- `GameScene` - Main gameplay
- Generated WAV audio for iOS compatibility
- Phaser.js tweens for animations
- Speech bubble system

---

## GitHub Repository

**URL:** https://github.com/speri-psg/balance-beam-adventure

### Recent Commits
1. Add Swedish greeting, Noooo/Hooray sounds, and walking music
2. Use HTML5 Audio for iOS - generate WAV bell sound
3. Fix iOS audio - unlock on first touch with silent buffer
4. Add name input, welcome greeting, and speech bubbles
5. Add floor routine and super jump feature
6. Move web to docs folder for GitHub Pages
7. Add web version (Phaser.js) - works on iPhone/all browsers

---

## How to Play

1. **Open the game** in a web browser (or run main.py for Kivy version)
2. **Enter your name** on the menu screen
3. **Tap PLAY** to start
4. **Tap anywhere** (or press SPACE) to make the gymnast jump
5. **Avoid** bowling balls and bees
6. **Reach the flag** at the end of the beam to complete the level
7. **Watch** the floor exercise routine
8. **Complete all 5 levels** to win!

---

## Credits

- **Game Design & Development:** Claude Opus 4.5 (AI Assistant)
- **Concept:** Balance beam gymnastics adventure for children
- **Dedicated to:** Charlotte

---

*Last Updated: February 2026*
