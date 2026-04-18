# 🪄 Magic Band

Last Halloween I came across [this video](https://www.youtube.com/watch?v=f09JSgdGhIk) in a Facebook group with a replica of the Haunted Mansion Magic Band reader for the Lightning Lane at Disney World. Fortunately, the creator made the 3D print files available, but excluded the electronics that make it come to life. The electronics were excluded due to a complex, multi-unit custom implementation. Since my kids love going to Disney, I wanted to build one for them. There's also been growing interest in a standalone solution — so this is for everyone who would like to build their own.

<img alt="mb-reader-static" src="https://github.com/user-attachments/assets/b52963d8-96a4-4b9d-b553-0d87c9bf57ff" />

## Overview

The Magic Band reader is powered by a Raspberry Pi Zero 2w. When powered on, the Raspberry Pi will automatically run the program. In the idle state, the LED lights will circle the reader. When an RFID card is presented to the reader, an LED animation is triggered along with a "chime" sound. If the audio is replaced with something longer, there is an option to tap the RFID card again which will stop the audio. The lights will briefly turn the lights red to acknowledge the tap.

The current implementation of this Magic Band reader is compatible with virtually any 13.56MHz RFID device.

## Bill of Materials

- **[Raspberry Pi Zero 2W](https://www.digikey.ca/en/products/detail/raspberry-pi/SC0721/24627135)** — The brains of the operation
- **[RC522 Mini RFID Reader](https://www.aliexpress.com/item/1005006907801802.html)** — SPI-connected tag scanning
- **[MAX98357A I2S Amplifier](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/3006/6058477)** — digital audio output
- **[Adafruit 3351 Speaker](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/3351/6612456)** - plays audio, does not require power source
- **[BTF-Lighting 1m 144 Light LED Strip](https://www.amazon.ca/dp/B0F5WQLMK7?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_6&th=1)** — LED lights
- **[BTF-Lighting 5V 6A PSU](https://www.amazon.ca/dp/B0FNWDR7TT?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2&th=1)** — powers LED lights
- **[Micro SD card 32-64gb](https://www.amazon.ca/SanDisk-Extreme-microSDXC-Memory-Adapter/dp/B09X7C7LL1?th=1)** - SD card for Raspberry Pi OS and audio files
- **[Dupont cables](https://www.amazon.ca/RGBZONE-Multicolored-Breadboard-Arduino-Raspberry/dp/B08TWSV2DY?th=1)** - Various cables to connect everything
- **[WAGO 221 Lever Nuts](https://www.homedepot.ca/product/wago-lever-nuts-3-conductor-compact-splicing-connectors-12-24awg-10-pack-/1001877147?TTID=MA_EN_B)** - Easily connect wires together without having to solder them

All of the materials needed to make the housing for the electronics can be found in the [Makerworld file](https://makerworld.com/en/models/1998101-disney-haunted-mansion-inspired-magicband-reader?from=search#profileId-2151033)



## Features

- RFID tag detection triggers LED lights and audio file
- Programming of individual RFID tags is not needed. There is no limit on how many tags you can use.
- Replaceable audio with stop functionality
- Animation timing is easily configurable

## Tech Stack

- Python (Pi-side RFID + LED lights + audio logic)
- I2S audio, SPI (RFID)

## Supporting files

- [Model of the Magic Band reader housing](https://makerworld.com/en/models/1998101-disney-haunted-mansion-inspired-magicband-reader?from=search#profileId-2151033)
- [Internal control panel (Print ready)](https://github.com/adamkool/magic-band-reader/blob/0c3ac6cd2602aba7beed5e0e5c9bfb62491abfb1/Magic%20Band%20Control%20Board.stl)
- [Internal control panel Fusion file (Excludes WAGO terminal)](https://github.com/adamkool/magic-band-reader/blob/0c3ac6cd2602aba7beed5e0e5c9bfb62491abfb1/Magic%20Band%20Control%20Board.f3d)
- [WAGO Terminal](https://makerworld.com/en/models/936345-wago-221-awg-24-12-connector-modular-mount-for-3x?from=search#profileId-901281)


