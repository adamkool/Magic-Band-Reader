# Magic Band RFID Audio Player — Complete Setup Guide

A beginner-friendly guide to building an RFID-triggered audio player with LED animations using a Raspberry Pi Zero 2W. When you tap an RFID tag, the LEDs animate and a chime plays — just like a Disney Magic Band.

---

## What You'll Need

### Hardware
| Item | Notes |
|---|---|
| Raspberry Pi Zero 2W | The main brain of the project |
| MicroSD card | 32GB, Class 10 minimum |
| RC522 RFID Reader Module | Reads your RFID tags |
| RFID Tags | 13.56MHz — at least 1 for testing |
| MAX98357A I2S Audio Amplifier | Plays the audio |
| Speaker | 4–8Ω, 3W |
| WS2812B LED Strip | Up to 144 pixels |
| 5V External Power Supply | 10A+ for 144 LEDs |
| Micro USB cable | Powers the Pi |
| Jumper wires | Female-to-female |

### Optional but Recommended
- 470Ω resistor (LED data line protection)
- 1000µF capacitor (LED power smoothing)

---

## Part 1 — Wiring

> ⚠️ **Always power off the Pi before changing wiring.**

### RFID Reader (RC522) → Pi

```
RC522 Pin    →    Pi Pin         (GPIO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SDA (SS)     →    Pin 24         (GPIO 8,  SPI CE0)
SCK          →    Pin 23         (GPIO 11, SPI CLK)
MOSI         →    Pin 19         (GPIO 10, SPI MOSI)
MISO         →    Pin 21         (GPIO 9,  SPI MISO)
RST          →    Pin 22         (GPIO 25)
3.3V         →    Pin 1          (3.3V)
GND          →    Pin 6          (GND)
```

### Audio Amplifier (MAX98357A) → Pi

```
MAX98357A    →    Pi Pin         (GPIO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIN          →    Pin 2          (5V)
GND          →    Pin 14         (GND)
DIN          →    Pin 40         (GPIO 21, I2S Data)
BCLK         →    Pin 12         (GPIO 18, I2S Clock)
LRC          →    Pin 35         (GPIO 19, I2S LR)
GAIN         →    Pin 16         (GPIO 23)
```

### LED Strip → Pi + External Power Supply

```
LED Strip    →    Destination
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIN (Data)   →    Pi Pin 32      (GPIO 12)
5V (Red)     →    External PSU +5V
GND (Black)  →    External PSU GND  ← also connect to Pi GND!
```

### Speaker → Audio Amplifier

```
Speaker      →    MAX98357A
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+ (positive) →    MAX98357A +
- (negative) →    MAX98357A -
```

---

### Complete Visual Wiring Diagram

```
Pi Zero 2W                          Components
══════════                          ══════════

[Pin  1 / 3.3V    ] ─────────────► RFID 3.3V
[Pin  6 / GND     ] ─────────────► RFID GND
[Pin 19 / GPIO 10 ] ─────────────► RFID MOSI
[Pin 21 / GPIO  9 ] ─────────────► RFID MISO
[Pin 22 / GPIO 25 ] ─────────────► RFID RST
[Pin 23 / GPIO 11 ] ─────────────► RFID SCK
[Pin 24 / GPIO  8 ] ─────────────► RFID SDA

[Pin  2 / 5V      ] ─────────────► Audio Amp VIN
[Pin 14 / GND     ] ─────────────► Audio Amp GND
[Pin 12 / GPIO 18 ] ─────────────► Audio Amp BCLK
[Pin 16 / GPIO 23 ] ─────────────► Audio Amp GAIN
[Pin 35 / GPIO 19 ] ─────────────► Audio Amp LRC
[Pin 40 / GPIO 21 ] ─────────────► Audio Amp DIN

[Pin 32 / GPIO 12 ] ─────────────► LED Strip DIN (data)

External PSU +5V ────────────────► LED Strip 5V  (red wire)
External PSU GND ────────┬───────► LED Strip GND (black wire)
                         └───────► Pi GND (Pin 6)  ← SHARED!

Audio Amp + ─────────────────────► Speaker +
Audio Amp - ─────────────────────► Speaker -
```

### Critical Wiring Rules

1. **Shared Ground** — Pi GND, LED power supply GND, and audio amp GND must all connect together
2. **LED Power** — Never power the LED strip from the Pi. Always use an external 5V supply
3. **LED Data Pin** — Use GPIO 12 (Pin 32), NOT GPIO 18 (that's used by audio)
4. **RFID RST Pin** — Must connect to GPIO 25 (Pin 22) for the reset sequence to work

---

### LED Daisy Chain (Two Strips)

If you have two LED strips, connect them in a chain:

```
Pi GPIO 12 ──────► Strip 1 DIN
                   Strip 1 DOUT ──────► Strip 2 DIN

External PSU +5V ──────┬──────────────► Strip 1 5V
                       └──────────────► Strip 2 5V

External PSU GND ──────┬──────────────► Strip 1 GND
                       ├──────────────► Strip 2 GND
                       └──────────────► Pi GND
```

> Power both strips directly from the PSU — don't chain power through Strip 1.

---

## Part 2 — Raspberry Pi OS Setup

### Step 1: Flash the SD Card

1. Download **Raspberry Pi Imager** from [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Insert your MicroSD card
3. Open Imager → Choose OS → **Raspberry Pi OS Lite (64-bit)**
4. Click the gear icon ⚙️ and configure:
   - Set hostname: `Magic-Band`
   - Enable SSH
   - Set username: `admin`
   - Set a password
   - Configure your WiFi network
5. Click Write and wait for it to finish
6. Insert the SD card into the Pi and power it on

### Step 2: Connect via SSH

Wait about 60 seconds for the Pi to boot, then on your computer:

```bash
ssh admin@Magic-Band.local
```

Enter your password when prompted. If it doesn't connect, try:

```bash
ssh -v admin@Magic-Band.local
```

### Step 3: Enable SPI (Required for RFID)

```bash
sudo raspi-config
```

Navigate to: **Interface Options → SPI → Yes → Finish**

Then reboot:
```bash
sudo reboot
```

Reconnect via SSH after reboot, then verify SPI is enabled:
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### Step 4: Enable I2S Audio

```bash
sudo nano /boot/firmware/config.txt
```

Add these lines at the bottom:
```
dtparam=i2s=on
dtoverlay=i2s-mmap
dtoverlay=googlevoicehat-soundcard
```

Save with `Ctrl+X` → `Y` → `Enter`, then reboot:
```bash
sudo reboot
```

---

## Part 3 — Install Software

Reconnect via SSH, then run these commands one at a time:

### Step 1: Update the System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Required Libraries

```bash
sudo pip3 install RPi.GPIO --break-system-packages
sudo pip3 install mfrc522 --break-system-packages
sudo pip3 install pygame --break-system-packages
sudo pip3 install rpi_ws281x --break-system-packages
sudo apt install -y ffmpeg
```

### Step 3: Create Project Folders

```bash
mkdir -p ~/magic-band/audio
```

### Step 4: Add Your Audio File

Copy your audio file to the Pi. From your computer (not the Pi):

```bash
scp /path/to/your/chime.wav admin@Magic-Band.local:~/magic-band/audio/
```

Then convert it to MP3 on the Pi:
```bash
ffmpeg -i ~/magic-band/audio/chime.wav ~/magic-band/audio/chime.mp3
```

---

## Part 4 — The Script

Create the main script:

```bash
nano ~/magic-band/magic_band.py
```

Paste the entire script below, then save with `Ctrl+X` → `Y` → `Enter`.

```python
#!/usr/bin/env python3
"""
Magic Band - Raspberry Pi Only
Controls RFID reader, audio playback, AND WS2812B LEDs directly.
No ESP32 required.

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

# Animation speeds (seconds)
IDLE_CHASE_DELAY       = 0.035  # Idle green chase speed (higher = slower)
TRIGGER_CHASE_DELAY    = 0.015  # Trigger chase speed (higher = slower)
TRIGGER_CHASE_DURATION = 1.0    # How long the trigger chase runs (seconds)
FLASH_ON_TIME          = 1.5    # How long solid green stays on (seconds)
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

    # Flash green
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
```

---

## Part 5 — Testing

### Test 1: LEDs Only

```bash
sudo python3 -c "
from rpi_ws281x import PixelStrip, Color
import time
strip = PixelStrip(42, 12, 800000, 0, False, 125, 0)
strip.begin()
print('Turning strip green for 3 seconds...')
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 255, 0))
strip.show()
time.sleep(3)
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 0))
strip.show()
print('Done!')
"
```

### Test 2: RFID Reader Only

```bash
sudo python3 -c "
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
print('Tap your RFID tag now...')
id, text = reader.read()
print(f'Tag ID: {id}')
"
```

### Test 3: Full System

```bash
sudo python3 ~/magic-band/magic_band.py
```

Expected startup output:
```
✓ RFID reader initialized
✓ LED strip initialized
✓ Audio gain configured
✓ Audio system initialized
✓ LED animation thread started
✓ Audio file ready: chime.mp3

============================================================
🎵✨ MAGIC BAND READY!
============================================================
Tap RFID tag to trigger!
```

---

## Part 6 — Auto-Start on Boot

### Step 1: Create the Service File

```bash
sudo nano /etc/systemd/system/magic-band.service
```

Paste:
```ini
[Unit]
Description=Magic Band RFID Audio Player
After=sound.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/admin/magic-band
ExecStart=/usr/bin/python3 /home/admin/magic-band/magic_band.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 2: Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable magic-band.service
sudo systemctl start magic-band.service
```

### Step 3: Test Boot

```bash
sudo reboot
```

After 60 seconds the LEDs should start animating automatically. Tap your RFID tag to trigger the full sequence.

---

## Part 7 — Adjusting Settings

All timing and brightness settings are at the top of `magic_band.py`:

| Setting | Default | What It Does |
|---|---|---|
| `NUM_LEDS` | 42 | Total number of LEDs |
| `LED_BRIGHTNESS` | 125 | LED brightness (0-255) |
| `IDLE_CHASE_DELAY` | 0.035 | Idle chase speed (higher = slower) |
| `TRIGGER_CHASE_DELAY` | 0.015 | Trigger chase speed (higher = slower) |
| `TRIGGER_CHASE_DURATION` | 1.0 | How long the fast chase runs (seconds) |
| `FLASH_ON_TIME` | 1.5 | How long the green flash stays on (seconds) |
| `AUDIO_FILE` | chime.mp3 | Path to your audio file |

To edit:
```bash
# Stop the service first
sudo systemctl stop magic-band.service

# Edit the script
nano ~/magic-band/magic_band.py

# Test your changes
sudo python3 ~/magic-band/magic_band.py

# When happy, restart the service
sudo systemctl start magic-band.service
```

---

## Part 8 — How It Works

### Tap Sequence
1. **Tap RFID tag** → audio plays immediately
2. **LEDs speed up** into fast chase animation
3. **Green flash** at end of chase
4. **LEDs return** to slow idle chase
5. **Tap again while audio plays** → red flash, audio stops, back to idle

### Why These Specific Pins?
- **GPIO 12** for LEDs — uses PWM0, avoids conflicting with SPI (used by RFID)
- **GPIO 18** for audio clock — standard I2S pin
- **GPIO 25** for RFID reset — used to hard-reset the reader on boot

### The RST Pin Fix
The RFID reader can hang during boot if initialized too early. The script manually pulls the RST pin LOW then HIGH before initializing the reader, forcing a clean hardware reset every time.

---

## Troubleshooting

### LEDs don't light up
- Run the LED test above
- Check GPIO 12 → LED DIN connection
- Verify external power supply is on
- Confirm shared ground between Pi and PSU

### RFID not reading
- Check SPI is enabled: `ls /dev/spi*` should show `/dev/spidev0.0`
- Verify all 7 RFID wires are connected
- Run the isolated RFID test above

### No audio
- Check speaker wires to MAX98357A
- Verify VIN on MAX98357A goes to 5V (not 3.3V)
- Check I2S overlay is in `/boot/firmware/config.txt`
- Run: `aplay -l` to list audio devices

### Service won't start
```bash
sudo journalctl -u magic-band.service -f
```
This shows live logs — paste any errors for diagnosis.

### SSH won't connect
```bash
ssh -v admin@Magic-Band.local
```
The `-v` flag shows verbose output to diagnose connection issues.

---

## Quick Reference Commands

```bash
# Run script manually (stop service first)
sudo systemctl stop magic-band.service
sudo python3 ~/magic-band/magic_band.py

# Service management
sudo systemctl start magic-band.service
sudo systemctl stop magic-band.service
sudo systemctl restart magic-band.service
sudo systemctl status magic-band.service

# View live service logs
sudo journalctl -u magic-band.service -f

# Convert audio file
ffmpeg -i ~/magic-band/audio/input.wav ~/magic-band/audio/output.mp3

# Force kill service if stuck
sudo systemctl kill magic-band.service
```

---

## Bill of Materials

| Item | Approximate Cost |
|---|---|
| Raspberry Pi Zero 2W | $15 |
| MicroSD Card 32GB | $8 |
| RC522 RFID Reader + Tags | $8 |
| MAX98357A Audio Amp | $6 |
| WS2812B LED Strip (1m/144px) | $12 |
| Speaker (3W 8Ω) | $5 |
| 5V 10A Power Supply | $15 |
| Jumper Wires | $5 |
| **Total** | **~$74** |

---

*Version 2.0 — Pi Only Edition — April 2026*
