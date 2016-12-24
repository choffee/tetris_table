This is the code that runs my tetris table. It's just a Raspberry Pi, some
neopixels and a table I made.
It's written in python and uses pygame for some parts. There is also a basic
emulator using pygame for testing. It will probably not work with legacy python versions.

To get the emulator working:

  python3 -m venv ./venv
  source ./venv/bin/activate
  pip install pygame
  TETRIS_EMU=TRUE ./tetris.py
  
The TETRIS_EMU setting will use the pygame emulator if you are using this on the tetris table, then the pi_setup.sh script should set things up for you and you can either just use the script directly or install the service file.

It's all written in python and licence under GPL v3 as per the COPYING file.
Copyright John Cooper 2016.
