#!/bin/bash
# Script to install LCDWiki driver for 3.5inch RPi Display
# Source: https://www.lcdwiki.com/3.5inch_RPi_Display

echo "Downloading LCD-show driver..."
if [ -d "LCD-show" ]; then
    echo "LCD-show folder already exists. Removing..."
    sudo rm -rf LCD-show
fi
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/

echo "Installing driver for 3.5 inch display..."
# This command will reboot the Pi!
sudo ./LCD35-show
