#!/bin/bash 
sudo touch /etc/chromium-browser/customizations/01-disable-update-check;echo CHROMIUM_FLAGS=\"\$\{CHROMIUM_FLAGS\} --check-for-update-interval=31536000\" | sudo tee /etc/chromium-browser/customizations/01-disable-update-check
sudo cp autostart /etc/xdg/lxsession/LXDE-pi/autostart

