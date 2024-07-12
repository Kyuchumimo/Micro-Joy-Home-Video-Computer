# Micro-Joy-Home-Video-Computer
Real old school hardware based fantasy computer.  
For all the details, please visit the [wiki](https://github.com/Kyuchumimo/Micro-Joy-Home-Video-Computer/wiki)  

This repository is under constant construction. Once finished building the libraries, tools and the wiki, the corresponding files will be uploaded. Please be patient.

![Micro Joy Home Video Computer](https://github.com/Kyuchumimo/Micro-Joy-Home-Video-Computer/assets/74131798/26b74839-57f7-4812-b579-5e045b2516cb)

## Specifications
|  | Specifications |
| ------------- | ------------- |
| MCU  | Raspberry Pi RP2040. Dual-core Arm Cortex M0+ processor @ 125MHz, 2/4/8/16MB QSPI Flash + 264kB SRAM  |
| Video  | Texas Instruments TMS9918 compatible Video Display Processor (VDP). Texas Instruments TMS99xx VDP (TMS9918 or 9918A/9118 or 9928A/9128 or 9929A/9129) or Yamaha V99xx VDP (V9938/9958/9990) or SEGA Master System VDP (315-5124/315-5246). Software alternatives: PICO9918: https://github.com/visrealm/pico9918  |
| Audio  | AY-3-8910 compatible Programmable Sound Generator (PSG). General Instruments / Microchip AY-3-891x family (8910/8912/8913/8914/8916/8917/8930) or Yamaha (YM2149F/YM3439/YMZ294/YMZ284/YMZ285) or Toshiba T7766A or Winbond WF19054 or JFC 95101 or File KC89C72. Software alternatives: AVR-AY (ATMEGA8/48/88/168/328): https://www.avray.ru/ or SoundCortexLPC (LPC810/812): https://github.com/toyoshim/SoundCortexLPC or SoundCortexSTM (STM32F042K6T6): https://github.com/toyoshim/SoundCortexSTM. LPC or Text-To-Speech (TTS) or Voice module (optional): Talkie: https://github.com/ArminJo/Talkie or WT588D or JR6001  |
| Input  | x2 8-bit or 16-bit PISO shift register compatible gamepad like NES-004 or NES-039 or SNS/SHVC-005, PS/2 compatible keyboard  |
| Programming language  | MicroPython v1.17 or higher |
| Software media  | 25xx02/04/08/16/32 Mbit external SPI Flash or Internal Flash  |

## Schematics
TODO

## Special thanks to
This project would not have been possible without the existence of these other awesome projects, communities and people:  
* [nesbox/TIC-80](https://github.com/nesbox/TIC-80)
* [AVR-AY](https://www.avray.ru)
* [toyoshim/SoundCortex](https://github.com/toyoshim/SoundCortex)
* [tildearrow/furnace](https://github.com/tildearrow/furnace)
* [Rasmus-M/magellan](https://github.com/Rasmus-M/magellan)
* [peterhinch/micropython_eeprom](https://github.com/peterhinch/micropython_eeprom)
* [mcauser/micropython-74hc595](https://github.com/mcauser/micropython-74hc595)
* [mcauser/micropython-pcd8544](https://github.com/mcauser/micropython-pcd8544)
* [mcauser/micropython-pcf8574](https://github.com/mcauser/micropython-pcf8574)
* [michalin/TMSS9918_Arduino](https://github.com/michalin/TMS9918_Arduino)
* [ricardoquesada/quico](https://gitlab.com/ricardoquesada/quico)
* The Chiptune Café
* Pygame Community
* Python Discord
* Fantasy Consoles 2.0
* [@EricDMG01](https://twitter.com/EricDMG01)
* [@pixelbath](https://twitter.com/pixelbath)
* [@AxlProtogen](https://twitter.com/AxlProtogen)
* [@Dippy0615](https://twitter.com/Dippy0615)
* [@AudioTryhard](https://twitter.com/AudioTryhard)
* [@alexxdip11](https://twitter.com/alexxdip11)
* [Daverd](https://soundcloud.com/daverd-chiptune)
