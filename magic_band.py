#!/usr/bin/env python3
"""
Magic Band - Raspberry Pi Only
Controls RFID reader, audio playback, AND WS2812B LEDs directly.

Run with: sudo python3 magic_band.py
"""

import RPi.GPIO as GPIO
import pygame
import time
import os
import threading
from rpi_ws281x import PixelStrip, Color

# ============= CONFIGURATION =============

# LED Configuration
LED_PIN        = 12       # GPIO 12 (Pin 32)
NUM_LEDS       = 42       # Total number of LEDs in your strip(s)
LED_BRIGHTNESS = 125      # 0-255 (125 = ~50%)
LED_FREQ_HZ    = 800000   # Signal frequency (800kHz for WS2812B)
LED_DMA        = 0        # 0 = PWM mode, avoids SPI/RFID conflict
LED_INVERT     = False
LED_CHANNEL    = 0

# Audio Configuration
AUDIO_FILE = "/home/admin/magic-band/audio/chime.mp3"

# Audio Amplifier GAIN Pin
GAIN_PIN = 23

# RFID
RST_PIN          = 25
COOLDOWN_SECONDS = 0.5

# Animation timing (seconds)
IDLE_CHASE_DELAY       = 0.035  # Idle green chase speed (higher = slower)
TRIGGER_CHASE_DELAY    = 0.012  # Trigger chase speed (higher = slower)
TRIGGER_CHASE_DURATION = 0.9    # How long the trigger chase runs
FLASH_DELAY            = 0.0    # Pause between chase and solid green flash
FLASH_ON_TIME          = 2.0    # How long solid green stays on
FLASH_OFF_TIME         = 0.1    # Pause after flash before idle resumes

# ============= RFID SETUP =============

GPIO.setmode(GPIO.BCM)

# Hard reset MFRC522 via RST pin before importing library
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.output(RST_PIN, GPIO.LOW)   # Hold in reset
time.sleep(0.5)
GPIO.output(RST_PIN, GPIO.HIGH)  # Release reset
time.sleep(1.0)                  # Let it stabilize

from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
print("✓ RFID reader initialized")

# ============= LED SETUP =============

strip = PixelStrip(
    NUM_LEDS, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()
print("✓ LED strip initialized")

# ============= GPIO / AUDIO SETUP =============

GPIO.setup(GAIN_PIN, GPIO.OUT)
gain_pwm = GPIO.PWM(GAIN_PIN, 100)
gain_pwm.start(100)  # Max gain
print("✓ Audio gain configured")

os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['AUDIODEV'] = 'hw:0,0'

# Retry audio init until device is free
for attempt in range(10):
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✓ Audio system initialized")
        break
    except pygame.error as e:
        print(f"⚠ Audio not ready (attempt {attempt+1}/10), retrying...")
        time.sleep(2)
else:
    print("✗ Audio device never became available")
    GPIO.cleanup()
    exit(1)

# ============= LED STATE =============

led_state = "IDLE"
led_lock  = threading.Lock()
chase_position_shared = 0

# ============= LED ANIMATION FUNCTIONS =============

def clear_strip():
    for i in range(NUM_LEDS):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def red_flash():
    """Flash all LEDs red for 1.0 seconds."""
    for i in range(NUM_LEDS):
        strip.setPixelColor(i, Color(255, 0, 0))
    strip.show()
    time.sleep(1.0)
    clear_strip()
    time.sleep(0.1)

def green_chase_frame(position):
    """Draw one frame of the idle green chase animation."""
    TAIL_LENGTH = 15
    for i in range(NUM_LEDS):
        strip.setPixelColor(i, Color(0, 0, 0))
    for i in range(TAIL_LENGTH):
        pos = (position + i) % NUM_LEDS
        brightness = int(255 * (TAIL_LENGTH - i) / TAIL_LENGTH)
        strip.setPixelColor(pos, Color(0, brightness, 0))
    strip.show()

def trigger_animation(start_pos):
    print("💡 Running trigger animation...")

    pos = start_pos
    chase_end = time.time() + TRIGGER_CHASE_DURATION
    while time.time() < chase_end:
        for i in range(NUM_LEDS):
            strip.setPixelColor(i, Color(0, 0, 0))
        for i in range(15):
            pixel = (pos - i) % NUM_LEDS
            brightness = min(255, int(255 * (15 - i) / 15))
            strip.setPixelColor(pixel, Color(0, brightness, 0))
        strip.show()
        pos = (pos + 1) % NUM_LEDS
        time.sleep(TRIGGER_CHASE_DELAY)

    # Brief pause then flash green
    clear_strip()
    time.sleep(FLASH_DELAY)
    for i in range(NUM_LEDS):
        strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()
    time.sleep(FLASH_ON_TIME)

    clear_strip()
    time.sleep(FLASH_OFF_TIME)

    print("✓ Trigger animation complete")

# ============= LED THREAD =============

def led_loop():
    global chase_position_shared
    chase_position = 0
    while True:
        with led_lock:
            state = led_state
            chase_position_shared = chase_position

        if state == "IDLE":
            green_chase_frame(chase_position)
            chase_position = (chase_position + 1) % NUM_LEDS
            time.sleep(IDLE_CHASE_DELAY)
        elif state == "TRIGGER":
            time.sleep(0.05)
        else:
            clear_strip()
            time.sleep(0.1)

led_thread = threading.Thread(target=led_loop, daemon=True)
led_thread.start()
print("✓ LED animation thread started")

# ============= TRIGGER SEQUENCE =============

def run_trigger_sequence():
    global led_state

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        time.sleep(0.1)
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.3)
    print("▶️  Playing audio...")

    with led_lock:
        start_pos = (chase_position_shared + 15) % NUM_LEDS
        led_state = "TRIGGER"
    time.sleep(0.06)

    trigger_animation(start_pos)

    with led_lock:
        led_state = "IDLE"

def stop_and_reset():
    """Stop audio, flash red, then reset LEDs to idle green chase."""
    global led_state
    print("⏹️  Stopping and resetting...")
    pygame.mixer.music.stop()
    with led_lock:
        led_state = "TRIGGER"
    red_flash()
    with led_lock:
        led_state = "IDLE"
    print("✓ Reset complete\n")

# ============= STARTUP CHECK =============

if not os.path.exists(AUDIO_FILE):
    print(f"✗ Audio file not found: {AUDIO_FILE}")
    print("Please upload an audio file to ~/magic-band/audio/")
    GPIO.cleanup()
    exit(1)
print(f"✓ Audio file ready: {os.path.basename(AUDIO_FILE)}")

print("\n" + "="*60)
print("🎵✨ MAGIC BAND READY!")
print("="*60)
print(f"RFID:  Waiting for tags...")
print(f"Audio: {os.path.basename(AUDIO_FILE)}")
print(f"LEDs:  Green chase running on GPIO {LED_PIN} ({NUM_LEDS} pixels)")
print("\nTap RFID tag to trigger!\n")

# ============= MAIN LOOP =============

last_tag_id    = None
last_read_time = 0

try:
    while True:
        id, text = reader.read()
        current_time = time.time()

        if id != last_tag_id or (current_time - last_read_time) > COOLDOWN_SECONDS:
            print("\n" + "─"*60)
            print(f"✨ RFID TAG DETECTED: {id}")
            print("─"*60)

            if pygame.mixer.music.get_busy():
                stop_and_reset()
            else:
                run_trigger_sequence()

            last_tag_id    = id
            last_read_time = current_time

except KeyboardInterrupt:
    print("\n\nShutting down Magic Band...")

finally:
    with led_lock:
        led_state = "OFF"
    time.sleep(0.1)
    clear_strip()

    pygame.mixer.music.stop()
    pygame.mixer.quit()

    gain_pwm.stop()
    GPIO.cleanup()
    print("✓ Cleanup complete. Goodbye!")
