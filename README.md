# 🪄 Magic Band

A Disney-inspired RFID audio/LED system that plays themed sounds and triggers light animations when a Magic Band (or compatible RFID tag) is scanned.

## Overview

Magic Band is a physical computing project built around a **Raspberry Pi Zero 2W**, designed to recreate the Disney MagicBand experience. Tap an RFID wristband/fob/card and get a personalized audio response with synchronized LED animations.

## Hardware

- **Raspberry Pi Zero 2W** — RFID detection and audio playback
- **RC522 Mini RFID Reader** — SPI-connected tag scanning
- **MAX98357A I2S Amplifier** — digital audio output
- **Adafruit 3351 Speaker** - plays audio, does not require power source
- **BTF-Lighting 5V 6A PSU** — powers LED lights


## Features

- RFID tag detection triggers LED lights and audio file
- Programming of RFID tags is not needed. There is no limit on how many tags you can use.
- Remote development support via Cursor Remote-SSH

## Tech Stack

- Python (Pi-side RFID + LED lights + audio logic)
- I2S audio, SPI (RFID)
