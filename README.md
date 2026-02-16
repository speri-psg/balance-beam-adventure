# Balance Beam Adventure - Kivy Game

A fun game for kids ages 5-8 where a player walks on a balance beam, jumps over bowling balls, and avoids pink-winged bees!

## Running on Windows (Desktop)

### 1. Install Kivy

```bash
pip install kivy
```

### 2. Run the game

```bash
cd BalanceBeamAdventure-Kivy
python main.py
```

## Building for Android (Google Play)

### 1. Install Buildozer (Linux/WSL required)

```bash
pip install buildozer
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

### 2. Build APK

```bash
cd BalanceBeamAdventure-Kivy
buildozer android debug
```

The APK will be in `bin/` folder.

### 3. Build Release APK for Google Play

```bash
buildozer android release
```

Sign the APK with your keystore before uploading to Google Play.

## Building for iOS (App Store)

Building for iOS requires a Mac with Xcode installed.

### 1. Install kivy-ios on Mac

```bash
pip install kivy-ios
```

### 2. Build for iOS

```bash
toolchain build kivy
toolchain create BalanceBeamAdventure .
```

### 3. Open in Xcode

Open the generated Xcode project, configure signing, and build for device/App Store.

## Game Controls

- **Tap anywhere** to jump
- Player automatically walks forward
- Jump over bowling balls
- Avoid the bees with pink wings
- Reach the flag to complete the level

## Levels

| Level | Difficulty | Ball Speed | Obstacles |
|-------|------------|------------|-----------|
| 1 | Easy | Slow | 1 ball, 1 bee |
| 2 | Easy | Slow | 2 balls, 2 bees |
| 3 | Medium | Medium | 2 balls, 2 bees |
| 4 | Medium | Medium | 3 balls, 3 bees |
| 5 | Hard | Fast | 3 balls, 4 bees |

## Features

- 5 progressive levels
- 3 lives system
- 100 points per level
- High score saved locally
- Level unlock progression
- Colorful kid-friendly graphics
