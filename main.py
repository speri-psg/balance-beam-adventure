"""
Balance Beam Adventure - A Kivy Game for Kids
Player walks on a balance beam, jumps over bowling balls, and avoids bees!
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line, Triangle, Quad
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
import random
import math

# Fullscreen on desktop (Windows/Mac/Linux)
import sys
if sys.platform in ['win32', 'darwin', 'linux']:
    Window.fullscreen = 'auto'  # True fullscreen
    # Alternative: Window.maximize() for windowed fullscreen

# ============== CONSTANTS ==============
class Colors:
    SKY_BLUE = (0.53, 0.81, 0.92, 1)
    BEAM_BROWN = (0.55, 0.27, 0.07, 1)
    BEAM_DARK = (0.4, 0.26, 0.13, 1)
    PLAYER_GREEN = (0.2, 0.8, 0.2, 1)
    PLAYER_DARK_GREEN = (0.13, 0.55, 0.13, 1)
    BALL_BLUE = (0.12, 0.23, 0.37, 1)
    BEE_YELLOW = (1, 0.84, 0, 1)
    BEE_PINK = (1, 0.41, 0.71, 1)
    GRASS_GREEN = (0.49, 0.99, 0, 1)
    BUTTON_ORANGE = (1, 0.65, 0, 1)
    BUTTON_GREEN = (0.3, 0.8, 0.3, 1)
    BUTTON_RED = (1, 0.39, 0.28, 1)
    WHITE = (1, 1, 1, 1)
    BLACK = (0, 0, 0, 1)
    GRAY = (0.5, 0.5, 0.5, 1)
    SUN_YELLOW = (1, 1, 0.4, 1)

class GameSettings:
    # Scale factor based on screen size (base design is 700px height)
    SCALE = max(1.0, Window.height / 700)

    PLAYER_RADIUS = int(30 * SCALE)
    PLAYER_WALK_SPEED = int(100 * SCALE)
    PLAYER_JUMP_FORCE = int(550 * SCALE)
    GRAVITY = int(-1000 * SCALE)

    BALL_RADIUS = int(25 * SCALE)
    BALL_SLOW_SPEED = int(140 * SCALE)
    BALL_MEDIUM_SPEED = int(200 * SCALE)
    BALL_FAST_SPEED = int(280 * SCALE)

    BEE_WIDTH = int(40 * SCALE)
    BEE_HEIGHT = int(26 * SCALE)
    BEE_SPEED = int(180 * SCALE)

    BEAM_HEIGHT = int(30 * SCALE)
    BEAM_Y_POSITION = int(Window.height * 0.2)  # 20% from bottom

    INITIAL_LIVES = 3
    POINTS_PER_LEVEL = 100
    TOTAL_LEVELS = 5

# Level configurations
LEVEL_CONFIGS = [
    {"level": 1, "ball_speed": GameSettings.BALL_SLOW_SPEED, "ball_count": 1, "bee_count": 1, "ball_interval": 4.0, "bee_interval": 6.0},
    {"level": 2, "ball_speed": GameSettings.BALL_SLOW_SPEED, "ball_count": 2, "bee_count": 2, "ball_interval": 3.5, "bee_interval": 5.0},
    {"level": 3, "ball_speed": GameSettings.BALL_MEDIUM_SPEED, "ball_count": 2, "bee_count": 2, "ball_interval": 3.0, "bee_interval": 4.5},
    {"level": 4, "ball_speed": GameSettings.BALL_MEDIUM_SPEED, "ball_count": 3, "bee_count": 3, "ball_interval": 2.5, "bee_interval": 4.0},
    {"level": 5, "ball_speed": GameSettings.BALL_FAST_SPEED, "ball_count": 3, "bee_count": 4, "ball_interval": 2.0, "bee_interval": 3.0},
]

# ============== GAME MANAGER ==============
class GameManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.store = JsonStore('balance_beam_save.json')
        self.lives = GameSettings.INITIAL_LIVES
        self.score = 0
        self.current_level = 1
        self.load_data()

    def load_data(self):
        if self.store.exists('game_data'):
            data = self.store.get('game_data')
            self.high_score = data.get('high_score', 0)
            self.highest_unlocked_level = data.get('unlocked_level', 1)
        else:
            self.high_score = 0
            self.highest_unlocked_level = 1

    def save_data(self):
        self.store.put('game_data',
                       high_score=self.high_score,
                       unlocked_level=self.highest_unlocked_level)

    def reset_lives(self):
        self.lives = GameSettings.INITIAL_LIVES

    def lose_life(self):
        self.lives -= 1
        return self.lives > 0

    def add_points(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_data()

    def complete_level(self):
        self.add_points(GameSettings.POINTS_PER_LEVEL)
        if self.current_level >= self.highest_unlocked_level and self.current_level < GameSettings.TOTAL_LEVELS:
            self.highest_unlocked_level = self.current_level + 1
            self.save_data()

    def advance_level(self):
        if self.current_level < GameSettings.TOTAL_LEVELS:
            self.current_level += 1
            return True
        return False

    def start_new_game(self):
        self.reset_lives()
        self.score = 0
        self.current_level = 1

    def get_level_config(self):
        return LEVEL_CONFIGS[self.current_level - 1]


# ============== COLORS FOR GYMNAST ==============
class GymnastColors:
    SKIN = (1.0, 0.85, 0.75, 1)       # Light skin tone
    LEOTARD = (1.0, 0.41, 0.71, 1)    # Pink leotard
    LEOTARD_DARK = (0.9, 0.3, 0.6, 1) # Darker pink
    HAIR = (0.4, 0.26, 0.13, 1)       # Brown hair
    HAIR_HIGHLIGHT = (0.5, 0.35, 0.2, 1)


# ============== GAME OBJECTS ==============
class Player(Widget):
    velocity_y = NumericProperty(0)
    is_jumping = BooleanProperty(False)
    is_on_ground = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        s = GameSettings.SCALE
        self.size = (int(50 * s), int(80 * s))  # Taller for gymnast
        self.leg_angle = 0
        self.leg_direction = 1
        self.arm_angle = 0
        self.facing_front = False  # True when turning to face player
        self.front_timer = 0  # How long to face front
        self.was_jumping = False  # Track if we just landed

        # Flip animation state
        self.is_flipping = False
        self.flip_angle = 0  # 0 to 360 degrees
        self.flip_height = 0
        self.flip_phase = 0  # 0=jump up, 1=flip, 2=land
        self.flip_callback = None  # Called when flip completes

        # Floor exercise state
        self.is_floor_exercise = False
        self.floor_y = 0  # Y position of floor
        self.cartwheel_angle = 0
        self.floor_target_x = 0  # Where to stop

        # Flip up to beam state
        self.is_flipping_up = False
        self.flip_up_start_y = 0
        self.flip_up_target_y = 0

        self.draw_player()

    def draw_player(self):
        self.canvas.clear()
        s = GameSettings.SCALE
        cx = self.center_x

        if self.is_flipping or self.is_flipping_up:
            self.draw_flipping(s, cx)
        elif self.is_floor_exercise:
            if hasattr(self, 'is_pausing') and self.is_pausing:
                self.draw_floor_standing(s, cx)  # Standing pose during pause
            else:
                self.draw_cartwheel(s, cx)
        elif self.facing_front:
            self.draw_front_view(s, cx)
        else:
            self.draw_side_view(s, cx)

    def draw_flipping(self, s, cx):
        """Draw gymnast doing a flip (rotating)"""
        from kivy.graphics import PushMatrix, PopMatrix, Rotate, Translate

        with self.canvas:
            PushMatrix()

            # Move to center of character, rotate, move back
            char_center_y = self.y + 40 * s
            Translate(cx, char_center_y + self.flip_height, 0)
            Rotate(angle=self.flip_angle, axis=(0, 0, 1))
            Translate(-cx, -char_center_y, 0)

            # Draw tucked body during flip
            body_y = self.y

            # Tucked legs
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - 10*s, body_y + 5*s), size=(8*s, 15*s))
            Ellipse(pos=(cx + 2*s, body_y + 5*s), size=(8*s, 15*s))

            # Body (tucked)
            Color(*GymnastColors.LEOTARD)
            Ellipse(pos=(cx - 12*s, body_y + 18*s), size=(24*s, 28*s))

            # Arms wrapped
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - 15*s, body_y + 25*s), size=(6*s, 18*s))
            Ellipse(pos=(cx + 9*s, body_y + 25*s), size=(6*s, 18*s))

            # Head
            head_y = body_y + 42 * s
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - 12*s, head_y), size=(24*s, 22*s))

            # Ponytail flying
            pony_angle = self.flip_angle * 0.5
            PushMatrix()
            Rotate(angle=pony_angle, origin=(cx, head_y + 11*s))
            Rectangle(pos=(cx - 4*s, head_y + 8*s), size=(8*s, 18*s))
            PopMatrix()

            # Face
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - 9*s, head_y + 2*s), size=(18*s, 16*s))

            # Determined expression
            Color(*Colors.BLACK)
            # Focused eyes
            Ellipse(pos=(cx - 6*s, head_y + 10*s), size=(4*s, 4*s))
            Ellipse(pos=(cx + 2*s, head_y + 10*s), size=(4*s, 4*s))

            PopMatrix()

    def draw_cartwheel(self, s, cx):
        """Draw gymnast doing a cartwheel (floor exercise)"""
        from kivy.graphics import PushMatrix, PopMatrix, Rotate, Translate

        with self.canvas:
            PushMatrix()

            # Rotate around center
            char_center_y = self.y + 40 * s
            Translate(cx, char_center_y, 0)
            Rotate(angle=self.cartwheel_angle, axis=(0, 0, 1))
            Translate(-cx, -char_center_y, 0)

            # Extended body for cartwheel
            body_y = self.y

            # Legs spread (one up, one down)
            Color(*GymnastColors.SKIN)
            # First leg
            PushMatrix()
            Rotate(angle=30, origin=(cx, body_y + 20*s))
            Rectangle(pos=(cx - 4*s, body_y + 20*s), size=(8*s, 28*s))
            PopMatrix()
            # Second leg
            PushMatrix()
            Rotate(angle=-30, origin=(cx, body_y + 20*s))
            Rectangle(pos=(cx - 4*s, body_y - 10*s), size=(8*s, 28*s))
            PopMatrix()

            # Body (stretched)
            Color(*GymnastColors.LEOTARD)
            Rectangle(pos=(cx - 10*s, body_y + 18*s), size=(20*s, 30*s))

            # Arms spread wide
            Color(*GymnastColors.SKIN)
            # Left arm up
            PushMatrix()
            Rotate(angle=45, origin=(cx - 8*s, body_y + 45*s))
            Rectangle(pos=(cx - 12*s, body_y + 45*s), size=(6*s, 22*s))
            PopMatrix()
            # Right arm down
            PushMatrix()
            Rotate(angle=-45, origin=(cx + 8*s, body_y + 45*s))
            Rectangle(pos=(cx + 6*s, body_y + 25*s), size=(6*s, 22*s))
            PopMatrix()

            # Head
            head_y = body_y + 48 * s
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - 10*s, head_y), size=(20*s, 18*s))

            # Ponytail flying
            PushMatrix()
            Rotate(angle=self.cartwheel_angle * 0.3, origin=(cx, head_y + 9*s))
            Rectangle(pos=(cx - 3*s, head_y + 6*s), size=(6*s, 15*s))
            PopMatrix()

            # Face
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - 8*s, head_y + 2*s), size=(16*s, 14*s))

            # Determined eyes
            Color(*Colors.BLACK)
            Ellipse(pos=(cx - 5*s, head_y + 8*s), size=(3*s, 3*s))
            Ellipse(pos=(cx + 2*s, head_y + 8*s), size=(3*s, 3*s))

            PopMatrix()

    def draw_floor_standing(self, s, cx):
        """Draw gymnast standing on floor during pause (facing player with arms raised)"""
        with self.canvas:
            body_y = self.y

            # Legs together
            Color(*GymnastColors.SKIN)
            Rectangle(pos=(cx - 10*s, body_y), size=(8*s, 24*s))
            Rectangle(pos=(cx + 2*s, body_y), size=(8*s, 24*s))

            # Body
            Color(*GymnastColors.LEOTARD)
            Rectangle(pos=(cx - 11*s, body_y + 22*s), size=(22*s, 28*s))
            # Rounded shoulders
            Ellipse(pos=(cx - 14*s, body_y + 42*s), size=(10*s, 10*s))
            Ellipse(pos=(cx + 4*s, body_y + 42*s), size=(10*s, 10*s))

            # Arms raised in V shape (victory pose!)
            Color(*GymnastColors.SKIN)
            from kivy.graphics import PushMatrix, PopMatrix, Rotate
            # Left arm
            PushMatrix()
            Rotate(angle=30, origin=(cx - 12*s, body_y + 48*s))
            Rectangle(pos=(cx - 15*s, body_y + 48*s), size=(6*s, 22*s))
            PopMatrix()
            # Right arm
            PushMatrix()
            Rotate(angle=-30, origin=(cx + 12*s, body_y + 48*s))
            Rectangle(pos=(cx + 9*s, body_y + 48*s), size=(6*s, 22*s))
            PopMatrix()

            # Head
            head_y = body_y + 50 * s

            # Hair behind
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - 12*s, head_y), size=(24*s, 22*s))

            # Ponytail
            Rectangle(pos=(cx - 4*s, head_y + 16*s), size=(8*s, 14*s))

            # Face
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - 10*s, head_y + 2*s), size=(20*s, 18*s))

            # Hair bangs
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - 8*s, head_y + 14*s), size=(16*s, 8*s))

            # Happy eyes (closed, smiling)
            Color(*Colors.BLACK)
            Line(bezier=[cx - 7*s, head_y + 12*s, cx - 4*s, head_y + 14*s, cx - 1*s, head_y + 12*s], width=1.5*s)
            Line(bezier=[cx + 1*s, head_y + 12*s, cx + 4*s, head_y + 14*s, cx + 7*s, head_y + 12*s], width=1.5*s)

            # Big smile
            Line(bezier=[cx - 6*s, head_y + 6*s, cx, head_y + 3*s, cx + 6*s, head_y + 6*s], width=1.5*s)

            # Rosy cheeks
            Color(1.0, 0.5, 0.5, 0.6)
            Ellipse(pos=(cx - 10*s, head_y + 5*s), size=(5*s, 4*s))
            Ellipse(pos=(cx + 5*s, head_y + 5*s), size=(5*s, 4*s))

    def start_flip(self, callback=None, flip_down=False, target_y=None):
        """Start the flip animation"""
        self.is_flipping = True
        self.flip_angle = 0
        self.flip_height = 0
        self.flip_phase = 0
        self.flip_callback = callback
        self.flip_down = flip_down  # If true, land lower (on floor)
        self.flip_target_y = target_y  # Target Y position after flip

    def start_flip_up(self, target_y, callback=None):
        """Start flipping up onto the beam"""
        self.is_flipping_up = True
        self.is_flipping = False
        self.flip_angle = 0
        self.flip_up_start_y = self.y
        self.flip_up_target_y = target_y
        self.flip_phase = 0
        self.flip_callback = callback

    def start_floor_exercise(self, target_x, floor_y, callback=None):
        """Start floor exercise (cartwheels) to target position"""
        self.is_floor_exercise = True
        self.floor_target_x = target_x
        self.floor_y = floor_y
        self.y = floor_y
        self.cartwheel_angle = 0
        self.flip_count = 0  # Count completed flips
        self.is_pausing = False  # Pause after 3 flips
        self.pause_timer = 0
        self.flip_callback = callback

    def update_flip(self, dt):
        """Update flip animation, returns True when complete"""
        if not self.is_flipping and not self.is_flipping_up:
            return False

        s = GameSettings.SCALE

        if self.is_flipping_up:
            # Flipping up onto the beam
            if self.flip_phase == 0:
                # Jump up and start rotating
                progress = self.flip_angle / 360
                height_curve = math.sin(progress * math.pi)  # Arc motion
                self.y = self.flip_up_start_y + (self.flip_up_target_y - self.flip_up_start_y) * progress + height_curve * 60 * s
                self.flip_angle += 540 * dt

                if self.flip_angle >= 360:
                    self.flip_angle = 0
                    self.y = self.flip_up_target_y
                    self.is_flipping_up = False
                    self.facing_front = True
                    self.front_timer = 0.5

                    if self.flip_callback:
                        self.flip_callback()
                    return True
        else:
            # Regular flip (or flip down)
            if self.flip_phase == 0:
                # Jump up phase
                self.flip_height += 400 * s * dt
                if self.flip_height >= 80 * s:
                    self.flip_phase = 1

            elif self.flip_phase == 1:
                # Spinning phase
                self.flip_angle += 720 * dt
                if self.flip_angle >= 360:
                    self.flip_angle = 360
                    self.flip_phase = 2

            elif self.flip_phase == 2:
                # Landing phase
                self.flip_height -= 400 * s * dt

                # If flipping down, also move Y down
                if hasattr(self, 'flip_down') and self.flip_down and self.flip_target_y is not None:
                    self.y -= 300 * s * dt
                    if self.y <= self.flip_target_y:
                        self.y = self.flip_target_y
                        self.flip_height = 0

                if self.flip_height <= 0:
                    self.flip_height = 0
                    self.is_flipping = False

                    if hasattr(self, 'flip_down') and self.flip_down:
                        # Don't face front yet, will do floor exercise
                        pass
                    else:
                        self.facing_front = True
                        self.front_timer = 0.8

                    if self.flip_callback:
                        self.flip_callback()
                    return True

        self.draw_player()
        return False

    def update_floor_exercise(self, dt):
        """Update floor exercise animation, returns True when complete"""
        if not self.is_floor_exercise:
            return False

        s = GameSettings.SCALE

        # Handle pause between flip sets
        if self.is_pausing:
            self.pause_timer -= dt
            # During pause, draw standing pose (angle = 0)
            self.cartwheel_angle = 0
            if self.pause_timer <= 0:
                self.is_pausing = False
                self.flip_count = 0  # Reset flip count for next set
            self.draw_player()
            return False

        # Move left while doing cartwheels
        speed = 250 * s
        self.x -= speed * dt
        self.cartwheel_angle += 400 * dt  # Rotate for cartwheel effect

        # Count completed flips (when we cross 360)
        if self.cartwheel_angle >= 360:
            self.cartwheel_angle -= 360
            self.flip_count += 1

            # Pause after every 3 flips
            if self.flip_count >= 3:
                self.is_pausing = True
                self.pause_timer = 0.5  # Pause for 0.5 seconds
                self.cartwheel_angle = 0  # Stand upright during pause

        self.draw_player()

        # Check if reached target
        if self.x <= self.floor_target_x:
            self.x = self.floor_target_x
            self.is_floor_exercise = False
            self.cartwheel_angle = 0

            if self.flip_callback:
                self.flip_callback()
            return True

        return False

    def draw_side_view(self, s, cx):
        """Draw gymnast from side (facing right)"""
        from kivy.graphics import PushMatrix, PopMatrix, Rotate

        # Animation offsets for walking
        leg_swing = math.sin(self.leg_angle) * 20
        arm_swing = math.sin(self.leg_angle) * 15

        with self.canvas:
            # ===== BACK LEG (further from viewer) =====
            leg_width = 7 * s
            leg_height = 24 * s

            Color(*GymnastColors.SKIN[:3], 0.8)  # Slightly transparent for depth
            PushMatrix()
            Rotate(angle=-leg_swing, origin=(cx - 2*s, self.y + 22*s))
            Rectangle(pos=(cx - 5*s, self.y), size=(leg_width, leg_height))
            PopMatrix()

            # ===== BODY/LEOTARD (side view - narrower) =====
            body_y = self.y + 20 * s
            body_height = 28 * s
            body_width = 16 * s

            Color(*GymnastColors.LEOTARD)
            Rectangle(pos=(cx - body_width/2, body_y), size=(body_width, body_height))

            # ===== BACK ARM =====
            arm_width = 5 * s
            arm_height = 18 * s

            Color(*GymnastColors.SKIN[:3], 0.8)
            PushMatrix()
            Rotate(angle=arm_swing + 20, origin=(cx - 4*s, body_y + body_height - 5*s))
            Rectangle(pos=(cx - 6*s, body_y + body_height - arm_height - 5*s), size=(arm_width, arm_height))
            PopMatrix()

            # ===== FRONT LEG =====
            Color(*GymnastColors.SKIN)
            PushMatrix()
            Rotate(angle=leg_swing, origin=(cx + 2*s, self.y + 22*s))
            Rectangle(pos=(cx - 2*s, self.y), size=(leg_width, leg_height))
            PopMatrix()

            # ===== FRONT ARM =====
            Color(*GymnastColors.SKIN)
            PushMatrix()
            Rotate(angle=-arm_swing - 20, origin=(cx + 4*s, body_y + body_height - 5*s))
            Rectangle(pos=(cx + 1*s, body_y + body_height - arm_height - 5*s), size=(arm_width, arm_height))
            PopMatrix()

            # ===== HEAD (side profile) =====
            head_size = 18 * s
            head_y = body_y + body_height

            # Hair back (behind head)
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - head_size/2 - 4*s, head_y), size=(head_size, head_size + 2*s))

            # Ponytail flowing behind
            pony_swing = math.sin(self.leg_angle * 1.5) * 8
            PushMatrix()
            Rotate(angle=pony_swing - 45, origin=(cx - head_size/2, head_y + head_size/2))
            Rectangle(pos=(cx - head_size/2 - 18*s, head_y + head_size/2 - 4*s), size=(20*s, 8*s))
            Ellipse(pos=(cx - head_size/2 - 22*s, head_y + head_size/2 - 6*s), size=(10*s, 10*s))
            PopMatrix()

            # Face (skin) - side profile oval
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - head_size/2 + 2*s, head_y), size=(head_size - 2*s, head_size))

            # Hair bangs on forehead
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx, head_y + head_size - 8*s), size=(8*s, 10*s))

            # Eye (side view - one eye visible)
            eye_y = head_y + head_size/2 + 2*s
            Color(*Colors.WHITE)
            Ellipse(pos=(cx + 2*s, eye_y), size=(6*s, 5*s))
            # Pupil (looking forward/right)
            Color(*Colors.BLACK)
            Ellipse(pos=(cx + 5*s, eye_y + 1*s), size=(3*s, 3*s))

            # Nose (small bump)
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx + head_size/2 - 4*s, head_y + head_size/2 - 2*s), size=(5*s, 4*s))

            # Smile (side view)
            Color(*Colors.BLACK)
            smile_y = head_y + 4*s
            Line(points=[cx + 2*s, smile_y, cx + 8*s, smile_y + 2*s], width=1.2*s)

            # Rosy cheek
            Color(1.0, 0.6, 0.6, 0.5)
            Ellipse(pos=(cx + 1*s, smile_y - 1*s), size=(5*s, 4*s))

    def draw_front_view(self, s, cx):
        """Draw gymnast facing the player (front view)"""
        from kivy.graphics import PushMatrix, PopMatrix, Rotate

        with self.canvas:
            # ===== LEGS =====
            leg_width = 8 * s
            leg_height = 22 * s

            Color(*GymnastColors.SKIN)
            # Left leg
            Rectangle(pos=(cx - 12*s, self.y), size=(leg_width, leg_height))
            # Right leg
            Rectangle(pos=(cx + 4*s, self.y), size=(leg_width, leg_height))

            # ===== BODY/LEOTARD =====
            body_y = self.y + 20 * s
            body_height = 28 * s
            body_width = 22 * s

            Color(*GymnastColors.LEOTARD)
            Rectangle(pos=(cx - body_width/2, body_y), size=(body_width, body_height))
            # Rounded shoulders
            Ellipse(pos=(cx - body_width/2 - 3*s, body_y + body_height - 8*s), size=(10*s, 10*s))
            Ellipse(pos=(cx + body_width/2 - 7*s, body_y + body_height - 8*s), size=(10*s, 10*s))

            # ===== ARMS (raised in celebration!) =====
            arm_width = 6 * s
            arm_height = 20 * s
            arm_y = body_y + body_height - 5*s

            Color(*GymnastColors.SKIN)
            # Left arm raised
            PushMatrix()
            Rotate(angle=45, origin=(cx - 14*s, arm_y))
            Rectangle(pos=(cx - 18*s, arm_y), size=(arm_width, arm_height))
            PopMatrix()

            # Right arm raised
            PushMatrix()
            Rotate(angle=-45, origin=(cx + 14*s, arm_y))
            Rectangle(pos=(cx + 12*s, arm_y), size=(arm_width, arm_height))
            PopMatrix()

            # ===== HEAD =====
            head_size = 20 * s
            head_y = body_y + body_height

            # Hair (behind head)
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - head_size/2 - 2*s, head_y + 2*s), size=(head_size + 4*s, head_size + 6*s))

            # Ponytail (behind, centered)
            pony_x = cx - 4*s
            pony_y = head_y + head_size
            Ellipse(pos=(pony_x, pony_y - 2*s), size=(8*s, 6*s))
            Rectangle(pos=(pony_x, pony_y - 12*s), size=(8*s, 12*s))

            # Face (skin)
            Color(*GymnastColors.SKIN)
            Ellipse(pos=(cx - head_size/2, head_y), size=(head_size, head_size))

            # Hair bangs
            Color(*GymnastColors.HAIR)
            Ellipse(pos=(cx - head_size/2 + 2*s, head_y + head_size - 6*s), size=(head_size - 4*s, 8*s))

            # Eyes (happy/closed - celebrating!)
            eye_y = head_y + head_size/2 + 2*s
            Color(*Colors.BLACK)
            # Happy closed eyes (curved lines)
            Line(bezier=[cx - 9*s, eye_y, cx - 6*s, eye_y + 3*s, cx - 3*s, eye_y], width=1.5*s)
            Line(bezier=[cx + 3*s, eye_y, cx + 6*s, eye_y + 3*s, cx + 9*s, eye_y], width=1.5*s)

            # Big happy smile
            smile_y = head_y + 4*s
            Line(bezier=[cx - 6*s, smile_y,
                        cx, smile_y - 3*s,
                        cx + 6*s, smile_y], width=1.5*s)

            # Rosy cheeks (bigger when happy!)
            Color(1.0, 0.5, 0.5, 0.6)
            Ellipse(pos=(cx - 11*s, smile_y - 1*s), size=(5*s, 4*s))
            Ellipse(pos=(cx + 6*s, smile_y - 1*s), size=(5*s, 4*s))

    def update(self, dt, ground_y):
        # Handle front-facing timer (after landing from jump)
        if self.facing_front:
            self.front_timer -= dt
            if self.front_timer <= 0:
                self.facing_front = False

        # Walking animation (faster for gymnast)
        if not self.is_jumping and not self.facing_front:
            self.leg_angle += dt * 12
            self.arm_angle = self.leg_angle

        # Track if we were jumping
        was_in_air = self.is_jumping

        # Jumping physics
        if self.is_jumping:
            self.velocity_y += GameSettings.GRAVITY * dt
            self.y += self.velocity_y * dt

            landing_y = ground_y
            if self.y <= landing_y and self.velocity_y < 0:
                self.y = landing_y
                self.velocity_y = 0
                self.is_jumping = False
                self.is_on_ground = True

                # Just landed! Turn to face the player briefly
                self.facing_front = True
                self.front_timer = 0.4  # Face front for 0.4 seconds

        self.draw_player()

    def jump(self, super_jump=False):
        if self.is_on_ground and not self.is_jumping:
            self.is_jumping = True
            self.is_on_ground = False
            # Super jump is 50% higher when obstacles are close together
            if super_jump:
                self.velocity_y = GameSettings.PLAYER_JUMP_FORCE * 1.5
            else:
                self.velocity_y = GameSettings.PLAYER_JUMP_FORCE

    def get_collision_rect(self):
        s = GameSettings.SCALE
        # Collision area around the body
        return (self.x + 10*s, self.y + 20*s, self.width - 20*s, 40*s)


class BowlingBall(Widget):
    speed = NumericProperty(GameSettings.BALL_SLOW_SPEED)
    rotation = NumericProperty(0)

    def __init__(self, speed=GameSettings.BALL_SLOW_SPEED, **kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.size = (GameSettings.BALL_RADIUS * 2, GameSettings.BALL_RADIUS * 2)
        self.draw_ball()

    def draw_ball(self):
        self.canvas.clear()
        with self.canvas:
            # Save the current matrix
            from kivy.graphics import PushMatrix, PopMatrix, Rotate
            PushMatrix()
            Rotate(angle=self.rotation, origin=(self.center_x, self.center_y))

            # Ball body
            Color(*Colors.BALL_BLUE)
            Ellipse(pos=self.pos, size=self.size)

            # Shine
            Color(1, 1, 1, 0.3)
            Ellipse(pos=(self.x + 5, self.y + self.height - 15), size=(10, 10))

            # Finger holes
            Color(*Colors.WHITE)
            # Top hole
            Ellipse(pos=(self.center_x - 4, self.center_y + 2), size=(8, 8))
            # Bottom left hole
            Ellipse(pos=(self.center_x - 10, self.center_y - 10), size=(8, 8))
            # Bottom right hole
            Ellipse(pos=(self.center_x + 2, self.center_y - 10), size=(8, 8))

            PopMatrix()

    def update(self, dt):
        self.x -= self.speed * dt
        self.rotation -= self.speed * dt * 2
        self.draw_ball()

    def get_collision_circle(self):
        return (self.center_x, self.center_y, GameSettings.BALL_RADIUS)


class Bee(Widget):
    speed = NumericProperty(GameSettings.BEE_SPEED)
    wing_angle = NumericProperty(0)
    bob_offset = NumericProperty(0)
    bob_direction = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (GameSettings.BEE_WIDTH + 20, GameSettings.BEE_HEIGHT + 25)
        self.draw_bee()

    def draw_bee(self):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        s = GameSettings.SCALE  # Scale factor

        with self.canvas:
            # Pink wings (the distinctive feature!)
            wing_scale = 0.7 + abs(math.sin(self.wing_angle)) * 0.6

            Color(*Colors.BEE_PINK[:3], 0.7)
            # Left wing
            Ellipse(pos=(cx - 22*s, cy + 2*s), size=(18*s, 12*s * wing_scale))
            # Right wing
            Ellipse(pos=(cx + 4*s, cy + 2*s), size=(18*s, 12*s * wing_scale))

            # Wing outline
            Color(*Colors.BEE_PINK)
            Line(ellipse=(cx - 22*s, cy + 2*s, 18*s, 12*s * wing_scale), width=1.5*s)
            Line(ellipse=(cx + 4*s, cy + 2*s, 18*s, 12*s * wing_scale), width=1.5*s)

            # Body (yellow oval)
            Color(*Colors.BEE_YELLOW)
            Ellipse(pos=(cx - 15*s, cy - 10*s), size=(30*s, 20*s))

            # Black stripes
            Color(*Colors.BLACK)
            Rectangle(pos=(cx - 5*s, cy - 8*s), size=(4*s, 16*s))
            Rectangle(pos=(cx + 3*s, cy - 8*s), size=(4*s, 16*s))

            # Stinger
            Triangle(points=[cx - 15*s, cy, cx - 23*s, cy, cx - 15*s, cy - 3*s])

            # Eyes
            Ellipse(pos=(cx + 8*s, cy - 2*s), size=(6*s, 6*s))
            Ellipse(pos=(cx + 8*s, cy - 8*s), size=(6*s, 6*s))

            # Antennae
            Line(points=[cx + 2*s, cy + 10*s, cx - 5*s, cy + 18*s], width=2*s)
            Line(points=[cx + 6*s, cy + 10*s, cx + 13*s, cy + 18*s], width=2*s)
            # Antenna tips
            Ellipse(pos=(cx - 7*s, cy + 16*s), size=(4*s, 4*s))
            Ellipse(pos=(cx + 11*s, cy + 16*s), size=(4*s, 4*s))

    def update(self, dt):
        self.x -= self.speed * dt

        # Wing flapping
        self.wing_angle += dt * 25

        # Bobbing motion
        self.bob_offset += self.bob_direction * dt * 40
        if abs(self.bob_offset) > 20:
            self.bob_direction *= -1
        self.y += self.bob_direction * dt * 40

        self.draw_bee()

    def get_collision_circle(self):
        return (self.center_x, self.center_y, 15)


# ============== CONFETTI & MEDALS ==============
class ConfettiParticle(Widget):
    """A single confetti particle that falls and spins"""
    def __init__(self, x, y, is_medal=False, **kwargs):
        super().__init__(**kwargs)
        s = GameSettings.SCALE
        self.is_medal = is_medal

        if is_medal:
            self.size = (30 * s, 35 * s)
        else:
            self.size = (random.uniform(8, 15) * s, random.uniform(8, 15) * s)

        self.pos = (x, y)
        self.velocity_x = random.uniform(-100, 100) * s
        self.velocity_y = random.uniform(-200, 100) * s
        self.gravity = -400 * s
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-300, 300)

        # Random bright color for confetti
        self.confetti_color = random.choice([
            (1, 0.84, 0, 1),      # Gold
            (1, 0.41, 0.71, 1),   # Pink
            (0.53, 0.81, 0.92, 1), # Light blue
            (0.56, 0.93, 0.56, 1), # Light green
            (1, 0.5, 0, 1),       # Orange
            (0.8, 0.52, 0.98, 1), # Purple
        ])

        self.draw_particle()

    def draw_particle(self):
        self.canvas.clear()
        s = GameSettings.SCALE

        with self.canvas:
            from kivy.graphics import PushMatrix, PopMatrix, Rotate
            PushMatrix()
            Rotate(angle=self.rotation, origin=(self.center_x, self.center_y))

            if self.is_medal:
                # Draw a medal
                # Ribbon
                Color(0.8, 0.1, 0.1, 1)  # Red ribbon
                Rectangle(pos=(self.center_x - 4*s, self.center_y), size=(8*s, 15*s))

                # Medal circle (gold)
                Color(1, 0.84, 0, 1)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.width))

                # Medal shine
                Color(1, 0.95, 0.6, 1)
                Ellipse(pos=(self.x + 3*s, self.y + self.width - 12*s), size=(8*s, 8*s))

                # Star on medal
                Color(1, 0.95, 0.4, 1)
                star_cx = self.center_x
                star_cy = self.y + self.width/2
                star_size = 6 * s
                # Simple star shape using triangles
                Triangle(points=[
                    star_cx, star_cy + star_size,
                    star_cx - star_size * 0.6, star_cy - star_size * 0.4,
                    star_cx + star_size * 0.6, star_cy - star_size * 0.4
                ])
                Triangle(points=[
                    star_cx, star_cy - star_size,
                    star_cx - star_size * 0.6, star_cy + star_size * 0.4,
                    star_cx + star_size * 0.6, star_cy + star_size * 0.4
                ])
            else:
                # Draw confetti piece
                Color(*self.confetti_color)
                if random.random() < 0.5:
                    Ellipse(pos=self.pos, size=self.size)
                else:
                    Rectangle(pos=self.pos, size=self.size)

            PopMatrix()

    def update(self, dt):
        self.velocity_y += self.gravity * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.rotation += self.rotation_speed * dt
        self.draw_particle()

        # Return True if particle is off screen
        return self.y < -50


class ConfettiSystem(Widget):
    """Manages multiple confetti particles"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.is_active = False

    def start(self, num_confetti=50, num_medals=8):
        self.is_active = True
        self.particles = []

        # Create confetti particles
        for i in range(num_confetti):
            x = random.uniform(0, Window.width)
            y = Window.height + random.uniform(0, 100)
            particle = ConfettiParticle(x, y, is_medal=False)
            self.particles.append(particle)
            self.add_widget(particle)

        # Create medal particles
        for i in range(num_medals):
            x = random.uniform(Window.width * 0.2, Window.width * 0.8)
            y = Window.height + random.uniform(50, 200)
            medal = ConfettiParticle(x, y, is_medal=True)
            self.particles.append(medal)
            self.add_widget(medal)

        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        if not self.is_active:
            return False

        for particle in self.particles[:]:
            if particle.update(dt):
                self.remove_widget(particle)
                self.particles.remove(particle)

        # Stop when all particles are gone
        if not self.particles:
            self.is_active = False
            return False

    def stop(self):
        self.is_active = False
        Clock.unschedule(self.update)
        for particle in self.particles:
            self.remove_widget(particle)
        self.particles = []


# ============== BELL SOUND ==============
class BellSound:
    """Ringing bell sound that increases duration per level"""

    def __init__(self):
        self.sounds = {}  # Cache sounds per level

    def _create_bell_sound_for_level(self, level):
        """Create a ringing bell sound with duration based on level"""
        import struct
        import io
        import wave

        try:
            sample_rate = 44100

            # Duration increases by 50% per level
            # Level 1: 3 rings, Level 2: 4-5 rings, Level 3: 6-7 rings, etc.
            base_rings = 3
            duration_multiplier = 1.5 ** (level - 1)
            num_rings = int(base_rings * duration_multiplier)
            ring_spacing = 0.25

            # Create ring times
            ring_times = [i * ring_spacing for i in range(num_rings)]
            total_duration = ring_times[-1] + 0.7  # Extra time for decay

            all_samples = []
            num_samples = int(sample_rate * total_duration)

            for i in range(num_samples):
                t = i / sample_rate
                sample_value = 0

                # Add each bell ring
                for ring_start in ring_times:
                    if t >= ring_start:
                        ring_t = t - ring_start

                        # Bell frequencies (creates metallic ringing sound)
                        f1 = 1200  # High bell tone
                        f2 = 1500  # Higher harmonic
                        f3 = 800   # Lower resonance
                        f4 = 2000  # Shimmer

                        # Exponential decay for each ring
                        decay = math.exp(-ring_t * 4)

                        # Tremolo effect (ringing vibration)
                        tremolo = 1 + 0.3 * math.sin(2 * math.pi * 12 * ring_t)

                        # Combine frequencies for bell-like timbre
                        ring_sample = (
                            math.sin(2 * math.pi * f1 * ring_t) * 0.4 +
                            math.sin(2 * math.pi * f2 * ring_t) * 0.25 +
                            math.sin(2 * math.pi * f3 * ring_t) * 0.2 +
                            math.sin(2 * math.pi * f4 * ring_t) * 0.15
                        ) * decay * tremolo

                        sample_value += ring_sample

                # Normalize and convert to int16
                sample_value = max(-1, min(1, sample_value * 0.5))
                all_samples.append(int(sample_value * 32767))

            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                for sample in all_samples:
                    wav_file.writeframes(struct.pack('<h', sample))

            # Save to temp file
            import tempfile
            import os
            temp_dir = tempfile.gettempdir()
            sound_path = os.path.join(temp_dir, f'bell_sound_level{level}.wav')

            with open(sound_path, 'wb') as f:
                f.write(wav_buffer.getvalue())

            # Load with Kivy
            sound = SoundLoader.load(sound_path)
            if sound:
                sound.volume = 0.8
            return sound

        except Exception as e:
            print(f"Could not create bell sound: {e}")
            return None

    def play(self, level=1):
        if level not in self.sounds:
            self.sounds[level] = self._create_bell_sound_for_level(level)

        if self.sounds[level]:
            self.sounds[level].play()


# ============== GAME SCREEN ==============
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = GameWidget()
        self.add_widget(self.game_widget)

    def on_enter(self):
        self.game_widget.start_game()

    def on_leave(self):
        self.game_widget.stop_game()


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_manager = GameManager()
        self.player = None
        self.balls = []
        self.bees = []
        self.is_active = False
        self.is_game_over = False
        self.is_level_complete = False
        self.is_invincible = False

        self.ball_timer = 0
        self.bee_timer = 0
        self.balls_spawned = 0
        self.bees_spawned = 0
        self.confetti = None

        self.beam_width = 0
        self.beam_left = 0
        self.beam_right = 0
        self.beam_top = GameSettings.BEAM_Y_POSITION + GameSettings.BEAM_HEIGHT

        # UI elements
        self.score_label = None
        self.lives_label = None
        self.level_label = None

        # Bind touch
        Window.bind(on_touch_down=self.on_touch)

    def start_game(self):
        # Clean up confetti if exists
        if self.confetti:
            self.confetti.stop()
            self.confetti = None

        self.clear_widgets()
        self.canvas.clear()

        # Calculate beam dimensions
        self.beam_width = Window.width - 40
        self.beam_left = 20
        self.beam_right = Window.width - 20

        # Reset game state
        level_config = self.game_manager.get_level_config()
        self.balls_spawned = 0
        self.bees_spawned = 0
        self.ball_timer = level_config["ball_interval"] / 2
        self.bee_timer = level_config["bee_interval"] / 2
        self.is_active = True
        self.is_game_over = False
        self.is_level_complete = False
        self.is_invincible = False

        # Clear old objects
        self.balls = []
        self.bees = []

        # Create player
        self.player = Player()
        start_x = self.beam_left + 20
        start_y = self.beam_top
        self.player.pos = (start_x, start_y)
        self.add_widget(self.player)

        # Create UI
        self.create_ui()

        # Start game loop
        Clock.schedule_interval(self.update, 1/60)

    def stop_game(self):
        Clock.unschedule(self.update)
        Clock.unschedule(self.update_flip_animation)
        self.is_active = False

    def create_ui(self):
        s = GameSettings.SCALE
        font_large = f'{int(28 * s)}sp'
        font_medium = f'{int(22 * s)}sp'

        # Level label
        self.level_label = Label(
            text=f"Level {self.game_manager.current_level}",
            font_size=font_large,
            bold=True,
            color=Colors.BLACK,
            pos=(Window.width/2 - 75*s, Window.height - 70*s),
            size=(150*s, 50*s)
        )
        self.add_widget(self.level_label)

        # Score label
        self.score_label = Label(
            text=f"Score: {self.game_manager.score}",
            font_size=font_medium,
            color=Colors.BLACK,
            pos=(20, Window.height - 70*s),
            size=(150*s, 50*s),
            halign='left'
        )
        self.add_widget(self.score_label)

        # Lives label
        self.lives_label = Label(
            text=f"Lives: {'❤️' * self.game_manager.lives}",
            font_size=font_medium,
            color=Colors.BLACK,
            pos=(Window.width - 180*s, Window.height - 70*s),
            size=(170*s, 50*s),
            halign='right'
        )
        self.add_widget(self.lives_label)

    def update_ui(self):
        if self.score_label:
            self.score_label.text = f"Score: {self.game_manager.score}"
        if self.lives_label:
            self.lives_label.text = f"Lives: {'❤️' * self.game_manager.lives}{'🖤' * (GameSettings.INITIAL_LIVES - self.game_manager.lives)}"

    def draw_background(self):
        s = GameSettings.SCALE
        with self.canvas.before:
            self.canvas.before.clear()

            # Sky
            Color(*Colors.SKY_BLUE)
            Rectangle(pos=(0, 0), size=Window.size)

            # Sun
            Color(*Colors.SUN_YELLOW)
            Ellipse(pos=(Window.width - 100*s, Window.height - 140*s), size=(80*s, 80*s))

            # Clouds - spread across the screen
            Color(*Colors.WHITE)
            Ellipse(pos=(50*s, Window.height - 180*s), size=(80*s, 40*s))
            Ellipse(pos=(90*s, Window.height - 165*s), size=(65*s, 32*s))
            Ellipse(pos=(25*s, Window.height - 172*s), size=(55*s, 28*s))

            Ellipse(pos=(Window.width * 0.4, Window.height - 220*s), size=(70*s, 35*s))
            Ellipse(pos=(Window.width * 0.4 + 35*s, Window.height - 205*s), size=(60*s, 30*s))

            Ellipse(pos=(Window.width * 0.7, Window.height - 160*s), size=(75*s, 38*s))
            Ellipse(pos=(Window.width * 0.7 + 40*s, Window.height - 150*s), size=(55*s, 28*s))

            # Grass
            Color(*Colors.GRASS_GREEN)
            Rectangle(pos=(0, 0), size=(Window.width, GameSettings.BEAM_Y_POSITION - 40*s))

            # Balance beam
            Color(*Colors.BEAM_BROWN)
            Rectangle(pos=(self.beam_left, GameSettings.BEAM_Y_POSITION),
                     size=(self.beam_width, GameSettings.BEAM_HEIGHT))

            # Beam supports
            Color(*Colors.BEAM_DARK)
            support_width = 20 * s
            support_height = 80 * s
            Rectangle(pos=(self.beam_left + 40*s, GameSettings.BEAM_Y_POSITION - support_height), size=(support_width, support_height))
            Rectangle(pos=(self.beam_right - 60*s, GameSettings.BEAM_Y_POSITION - support_height), size=(support_width, support_height))

            # Finish flag
            flag_height = 70 * s
            flag_width = 35 * s
            Color(*Colors.BEAM_DARK)
            Rectangle(pos=(self.beam_right - 30*s, self.beam_top), size=(5*s, flag_height))
            Color(*Colors.BUTTON_RED)
            Triangle(points=[
                self.beam_right - 25*s, self.beam_top + flag_height,
                self.beam_right - 25*s, self.beam_top + flag_height - 25*s,
                self.beam_right - 25*s + flag_width, self.beam_top + flag_height - 12*s
            ])

    def update(self, dt):
        if not self.is_active or self.is_game_over or self.is_level_complete:
            return

        self.draw_background()

        level_config = self.game_manager.get_level_config()

        # Update player
        self.player.x += GameSettings.PLAYER_WALK_SPEED * dt
        self.player.update(dt, self.beam_top)

        # Check finish line
        if self.player.x >= self.beam_right - 50:
            self.level_complete()
            return

        # Spawn obstacles
        self.ball_timer += dt
        if self.ball_timer >= level_config["ball_interval"] and self.balls_spawned < level_config["ball_count"]:
            self.spawn_ball(level_config["ball_speed"])
            self.ball_timer = 0
            self.balls_spawned += 1

        self.bee_timer += dt
        if self.bee_timer >= level_config["bee_interval"] and self.bees_spawned < level_config["bee_count"]:
            self.spawn_bee()
            self.bee_timer = 0
            self.bees_spawned += 1

        # Update balls
        for ball in self.balls[:]:
            ball.update(dt)
            if ball.x < -50:
                self.remove_widget(ball)
                self.balls.remove(ball)
            elif not self.is_invincible and self.check_collision_circle_rect(ball.get_collision_circle(), self.player.get_collision_rect()):
                self.player_hit()

        # Update bees
        for bee in self.bees[:]:
            bee.update(dt)
            if bee.x < -50:
                self.remove_widget(bee)
                self.bees.remove(bee)
            elif not self.is_invincible and self.check_collision_circles(bee.get_collision_circle(),
                    (self.player.center_x, self.player.center_y, GameSettings.PLAYER_RADIUS)):
                self.player_hit()

    def check_collision_circle_rect(self, circle, rect):
        cx, cy, cr = circle
        rx, ry, rw, rh = rect

        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))

        distance = math.sqrt((cx - closest_x) ** 2 + (cy - closest_y) ** 2)
        return distance < cr

    def check_collision_circles(self, c1, c2):
        x1, y1, r1 = c1
        x2, y2, r2 = c2
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance < (r1 + r2)

    def spawn_ball(self, speed):
        ball = BowlingBall(speed=speed)
        ball.pos = (Window.width + 10, self.beam_top)
        self.add_widget(ball)
        self.balls.append(ball)

    def spawn_bee(self):
        bee = Bee()
        min_y = self.beam_top + 50
        max_y = Window.height - 150
        bee.pos = (Window.width + 10, random.uniform(min_y, max_y))
        self.add_widget(bee)
        self.bees.append(bee)

    def player_hit(self):
        if self.is_invincible:
            return

        self.is_invincible = True
        Clock.schedule_once(lambda dt: setattr(self, 'is_invincible', False), 1.5)

        # Flash player
        anim = Animation(opacity=0.3, duration=0.1) + Animation(opacity=1, duration=0.1)
        anim.repeat = True
        anim.start(self.player)
        Clock.schedule_once(lambda dt: Animation.cancel_all(self.player), 1.5)
        Clock.schedule_once(lambda dt: setattr(self.player, 'opacity', 1), 1.5)

        still_alive = self.game_manager.lose_life()
        self.update_ui()

        if not still_alive:
            self.game_over()
        else:
            self.reset_player_position()

    def reset_player_position(self):
        self.player.pos = (self.beam_left + 20, self.beam_top)
        self.player.velocity_y = 0
        self.player.is_jumping = False
        self.player.is_on_ground = True

        # Reset spawning
        level_config = self.game_manager.get_level_config()
        self.balls_spawned = 0
        self.bees_spawned = 0
        self.ball_timer = level_config["ball_interval"] / 2
        self.bee_timer = level_config["bee_interval"] / 2

        # Remove obstacles
        for ball in self.balls[:]:
            self.remove_widget(ball)
        self.balls.clear()

        for bee in self.bees[:]:
            self.remove_widget(bee)
        self.bees.clear()

    def level_complete(self):
        self.is_level_complete = True
        self.is_active = False

        # Calculate floor Y position (below the beam)
        s = GameSettings.SCALE
        self.floor_y = GameSettings.BEAM_Y_POSITION - 60 * s

        # Start the flip DOWN to floor
        self.player.start_flip(callback=self.on_flip_down_complete, flip_down=True, target_y=self.floor_y)

        # Schedule animation updates
        Clock.schedule_interval(self.update_transition_animation, 1/60)

    def update_transition_animation(self, dt):
        """Update all transition animations"""
        # Update whichever animation is active
        if self.player.is_flipping or self.player.is_flipping_up:
            self.player.update_flip(dt)
        elif self.player.is_floor_exercise:
            self.player.update_floor_exercise(dt)

        self.draw_background()
        self.player.draw_player()

    def on_flip_down_complete(self):
        """Called when flip down to floor is complete"""
        # Start floor exercise (cartwheels) back to the beginning
        target_x = self.beam_left + 20
        self.player.start_floor_exercise(target_x, self.floor_y, callback=self.on_floor_exercise_complete)

    def on_floor_exercise_complete(self):
        """Called when floor exercise is complete"""
        # Now flip UP onto the beam
        target_y = self.beam_top
        self.player.start_flip_up(target_y, callback=self.on_flip_up_complete)

    def on_flip_up_complete(self):
        """Called when flip up to beam is complete"""
        # Stop the transition animation loop
        Clock.unschedule(self.update_transition_animation)

        # Now complete the level
        self.game_manager.complete_level()
        self.update_ui()

        # Play bell sound (longer for higher levels)
        bell = BellSound()
        bell.play(level=self.game_manager.current_level)

        self.show_level_complete_ui()

    def game_over(self):
        self.is_game_over = True
        self.is_active = False
        self.show_game_over_ui()

    def show_level_complete_ui(self):
        s = GameSettings.SCALE
        btn_width = 220 * s
        btn_height = 65 * s

        # Overlay
        overlay = Widget()
        with overlay.canvas:
            Color(0, 0, 0, 0.5)
            Rectangle(pos=(0, 0), size=Window.size)
        self.add_widget(overlay)

        # Start confetti with medals!
        self.confetti = ConfettiSystem()
        self.add_widget(self.confetti)
        self.confetti.start(num_confetti=60, num_medals=10)

        # Level complete text
        current_level = self.game_manager.current_level
        if current_level >= GameSettings.TOTAL_LEVELS:
            title = "You Won!"
            subtitle = "Congratulations! All levels complete!"
        else:
            title = "Level Complete!"
            subtitle = f"+{GameSettings.POINTS_PER_LEVEL} points!"

        title_label = Label(
            text=title,
            font_size=f'{int(42 * s)}sp',
            bold=True,
            color=Colors.WHITE,
            center=(Window.width/2, Window.height/2 + 120*s)
        )
        self.add_widget(title_label)

        subtitle_label = Label(
            text=subtitle,
            font_size=f'{int(28 * s)}sp',
            color=Colors.BEE_YELLOW,
            center=(Window.width/2, Window.height/2 + 60*s)
        )
        self.add_widget(subtitle_label)

        # Buttons
        if current_level < GameSettings.TOTAL_LEVELS:
            next_btn = Button(
                text="Next Level",
                font_size=f'{int(26 * s)}sp',
                size=(btn_width, btn_height),
                pos=(Window.width/2 - btn_width/2, Window.height/2 - 30*s),
                background_color=Colors.BUTTON_GREEN
            )
            next_btn.bind(on_press=self.next_level)
            self.add_widget(next_btn)
        else:
            play_again_btn = Button(
                text="Play Again",
                font_size=f'{int(26 * s)}sp',
                size=(btn_width, btn_height),
                pos=(Window.width/2 - btn_width/2, Window.height/2 - 30*s),
                background_color=Colors.BUTTON_GREEN
            )
            play_again_btn.bind(on_press=self.restart_game)
            self.add_widget(play_again_btn)

        menu_btn = Button(
            text="Main Menu",
            font_size=f'{int(26 * s)}sp',
            size=(btn_width, btn_height),
            pos=(Window.width/2 - btn_width/2, Window.height/2 - 110*s),
            background_color=Colors.BUTTON_ORANGE
        )
        menu_btn.bind(on_press=self.go_to_menu)
        self.add_widget(menu_btn)

    def show_game_over_ui(self):
        s = GameSettings.SCALE
        btn_width = 220 * s
        btn_height = 65 * s

        # Overlay
        overlay = Widget()
        with overlay.canvas:
            Color(0, 0, 0, 0.6)
            Rectangle(pos=(0, 0), size=Window.size)
        self.add_widget(overlay)

        # Game over text
        title_label = Label(
            text="Game Over",
            font_size=f'{int(46 * s)}sp',
            bold=True,
            color=Colors.BUTTON_RED,
            center=(Window.width/2, Window.height/2 + 120*s)
        )
        self.add_widget(title_label)

        score_label = Label(
            text=f"Score: {self.game_manager.score}",
            font_size=f'{int(30 * s)}sp',
            color=Colors.WHITE,
            center=(Window.width/2, Window.height/2 + 50*s)
        )
        self.add_widget(score_label)

        messages = ["Nice try!", "Keep practicing!", "You can do it!", "Almost there!"]
        message_label = Label(
            text=random.choice(messages),
            font_size=f'{int(24 * s)}sp',
            color=Colors.WHITE,
            center=(Window.width/2, Window.height/2)
        )
        self.add_widget(message_label)

        # Buttons
        retry_btn = Button(
            text="Try Again",
            font_size=f'{int(26 * s)}sp',
            size=(btn_width, btn_height),
            pos=(Window.width/2 - btn_width/2, Window.height/2 - 80*s),
            background_color=Colors.BUTTON_GREEN
        )
        retry_btn.bind(on_press=self.retry_level)
        self.add_widget(retry_btn)

        menu_btn = Button(
            text="Main Menu",
            font_size=f'{int(26 * s)}sp',
            size=(btn_width, btn_height),
            pos=(Window.width/2 - btn_width/2, Window.height/2 - 160*s),
            background_color=Colors.BUTTON_ORANGE
        )
        menu_btn.bind(on_press=self.go_to_menu)
        self.add_widget(menu_btn)

    def check_obstacles_close(self):
        """Check if both a ball and bee are close - requires super jump"""
        if not self.player:
            return False

        danger_range = 200  # pixels ahead of player
        very_close_range = 100  # very close requires super jump

        player_x = self.player.x
        ball_close = False
        bee_close = False
        any_very_close = False

        # Check balls
        for ball in self.balls:
            dist = ball.x - player_x
            if 0 < dist < danger_range:
                ball_close = True
                if dist < very_close_range:
                    any_very_close = True

        # Check bees
        for bee in self.bees:
            dist = bee.x - player_x
            if 0 < dist < danger_range:
                bee_close = True
                if dist < very_close_range:
                    any_very_close = True

        # Need super jump if both ball and bee close, or any obstacle very close
        return (ball_close and bee_close) or any_very_close

    def on_touch(self, window, touch):
        if self.is_active and not self.is_game_over and not self.is_level_complete:
            if self.player:
                # Check if we need a super jump (obstacles close together)
                needs_super_jump = self.check_obstacles_close()
                self.player.jump(super_jump=needs_super_jump)
        return False

    def next_level(self, instance):
        self.game_manager.advance_level()
        self.start_game()

    def retry_level(self, instance):
        self.game_manager.reset_lives()
        self.start_game()

    def restart_game(self, instance):
        self.game_manager.start_new_game()
        self.start_game()

    def go_to_menu(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'


# ============== MENU SCREEN ==============
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        s = GameSettings.SCALE
        layout = FloatLayout()

        # Background
        with layout.canvas.before:
            Color(*Colors.SKY_BLUE)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)

            # Sun
            Color(*Colors.SUN_YELLOW)
            Ellipse(pos=(Window.width - 100*s, Window.height - 140*s), size=(80*s, 80*s))

            # Decorative grass
            Color(*Colors.GRASS_GREEN)
            Rectangle(pos=(0, 0), size=(Window.width, 120*s))

        # Title
        title1 = Label(
            text="Balance Beam",
            font_size=f'{int(52 * s)}sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        layout.add_widget(title1)

        title2 = Label(
            text="Adventure",
            font_size=f'{int(46 * s)}sp',
            bold=True,
            color=Colors.BUTTON_ORANGE,
            pos_hint={'center_x': 0.5, 'center_y': 0.72}
        )
        layout.add_widget(title2)

        # Play button
        play_btn = Button(
            text="Play",
            font_size=f'{int(32 * s)}sp',
            size_hint=(None, None),
            size=(240*s, 75*s),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=Colors.BUTTON_GREEN
        )
        play_btn.bind(on_press=self.start_game)
        layout.add_widget(play_btn)

        # Level select button
        levels_btn = Button(
            text="Select Level",
            font_size=f'{int(28 * s)}sp',
            size_hint=(None, None),
            size=(240*s, 65*s),
            pos_hint={'center_x': 0.5, 'center_y': 0.38},
            background_color=Colors.BUTTON_ORANGE
        )
        levels_btn.bind(on_press=self.go_to_levels)
        layout.add_widget(levels_btn)

        # High score
        gm = GameManager()
        high_score_label = Label(
            text=f"High Score: {gm.high_score}",
            font_size=f'{int(24 * s)}sp',
            color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.28}
        )
        layout.add_widget(high_score_label)

        self.add_widget(layout)

    def on_enter(self):
        # Refresh high score display
        self.clear_widgets()
        self.build_ui()

    def start_game(self, instance):
        GameManager().start_new_game()
        app = App.get_running_app()
        app.root.current = 'game'

    def go_to_levels(self, instance):
        app = App.get_running_app()
        app.root.current = 'levels'


# ============== LEVEL SELECT SCREEN ==============
class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        s = GameSettings.SCALE
        layout = FloatLayout()

        # Background
        with layout.canvas.before:
            Color(*Colors.SKY_BLUE)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(*Colors.GRASS_GREEN)
            Rectangle(pos=(0, 0), size=(Window.width, 100*s))

        # Title
        title = Label(
            text="Select Level",
            font_size=f'{int(42 * s)}sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.88}
        )
        layout.add_widget(title)

        # Level buttons
        gm = GameManager()
        button_size = int(100 * s)
        spacing = int(30 * s)
        start_x = Window.width / 2 - button_size - spacing / 2
        start_y = Window.height * 0.65

        difficulties = {1: "Easy", 2: "Easy", 3: "Medium", 4: "Medium", 5: "Hard"}
        diff_colors = {
            "Easy": Colors.BUTTON_GREEN,
            "Medium": Colors.BUTTON_ORANGE,
            "Hard": Colors.BUTTON_RED
        }

        for level in range(1, GameSettings.TOTAL_LEVELS + 1):
            row = (level - 1) // 2
            col = (level - 1) % 2

            x = start_x + col * (button_size + spacing)
            y = start_y - row * (button_size + spacing)

            is_unlocked = level <= gm.highest_unlocked_level
            difficulty = difficulties[level]

            if is_unlocked:
                btn_color = diff_colors[difficulty]
                btn_text = str(level)
            else:
                btn_color = Colors.GRAY
                btn_text = "🔒"

            btn = Button(
                text=btn_text,
                font_size=f'{int(38 * s)}sp',
                size_hint=(None, None),
                size=(button_size, button_size),
                pos=(x, y),
                background_color=btn_color
            )

            if is_unlocked:
                btn.bind(on_press=lambda inst, lv=level: self.select_level(lv))

                # Difficulty label
                diff_label = Label(
                    text=difficulty,
                    font_size=f'{int(14 * s)}sp',
                    color=Colors.WHITE,
                    pos=(x, y - 25*s),
                    size=(button_size, 25*s)
                )
                layout.add_widget(diff_label)

            layout.add_widget(btn)

        # Legend
        legend_y = 0.18
        legend_items = [("Easy", Colors.BUTTON_GREEN), ("Medium", Colors.BUTTON_ORANGE), ("Hard", Colors.BUTTON_RED)]
        for i, (text, color) in enumerate(legend_items):
            x_pos = 0.2 + i * 0.3

            # Color dot
            dot = Widget(size_hint=(None, None), size=(20*s, 20*s), pos_hint={'center_x': x_pos - 0.05, 'center_y': legend_y})
            with dot.canvas:
                Color(*color)
                Ellipse(pos=dot.pos, size=dot.size)
            layout.add_widget(dot)

            label = Label(
                text=text,
                font_size=f'{int(18 * s)}sp',
                color=(0.2, 0.2, 0.2, 1),
                pos_hint={'center_x': x_pos + 0.03, 'center_y': legend_y}
            )
            layout.add_widget(label)

        # Back button
        back_btn = Button(
            text="Back",
            font_size=f'{int(26 * s)}sp',
            size_hint=(None, None),
            size=(150*s, 60*s),
            pos_hint={'center_x': 0.5, 'center_y': 0.08},
            background_color=(0.3, 0.3, 0.3, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def select_level(self, level):
        gm = GameManager()
        gm.current_level = level
        gm.reset_lives()
        app = App.get_running_app()
        app.root.current = 'game'

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'


# ============== MAIN APP ==============
class BalanceBeamApp(App):
    def build(self):
        self.title = "Balance Beam Adventure"

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LevelSelectScreen(name='levels'))
        sm.add_widget(GameScreen(name='game'))

        return sm


if __name__ == '__main__':
    BalanceBeamApp().run()
