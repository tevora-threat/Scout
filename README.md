# Surveillance Detection Scout - Your Lookout on Autopilot

[![DEFCON 22 Badge](https://img.shields.io/badge/DEFCON-27-blue.svg)](https://defcon.org/html/defcon-27/dc-27-speakers.html#Kain)
[![OPEN-SOURCE](https://img.shields.io/badge/OPEN-SOURCE-orange.svg)](#)
[![GPL Licence](https://img.shields.io/badge/LICENSE-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0/)

Surveillance Detection Scout is a hardware and software stack that makes use of your Tesla's cameras to tell you if you're being followed in real-time. The name, as you likely gathered, pays homage to the ever-effective "Surveillance Detection Route". When parked, Scout makes an excellent static surveillance practitioner as well, allowing you to run queries and establish patterns-of-life on detected persons.

--
Feb Update: README to be updated shortly to reflect initial FCR.
--

Before going any further, I want to make sure to acknowledge the people (and repositories) who helped this project, with or without knowing they did so.

1. TeslaUSB (https://github.com/marcone/teslausb).
2. ALPR-Unconstrained (https://github.com/sergiomsilva/alpr-unconstrained).
3. Facenet (found at https://github.com/davidsandberg/facenet) and facenet_trt (https://github.com/JerryJiaGit/facenet_trt).
4. TeslaJS (https://github.com/mseminatore/TeslaJS) build off the original work of Tim Dorr (https://tesla-api.timdorr.com/)
5. The whole team at Tevora (https://threat.tevora.com).

## Information

Scout is a simple to install (at v1.0), and simple to use tool for analyzing video data from Tesla Model S, 3 and X camera feeds.

Scout is intended to be built on an Nvidia Jetson Xavier or Nano, but you may use a Raspberry Pi 4 if real time notification isn't a priority.

Detailed documentation coming shortly.

# First Things First (Polling Data)

Even if you don't yet have the hardware necessary to start running inference with Scout, you can start polling your vehicle, so that at least you can start to capture your historical trip data. Scout utilizes [TeslaJS](https://github.com/mseminatore/TeslaJS) for polling.

NOTE: Replace all CHANGEME areas in code

If you'd like to restart the poll script automatically if it crashes (internet outage or similar), uncomment lines 3 and 4 of `setup.sh`, and comment line 5.

Finally, run `./scripts/TeslaJS/setup.sh`.

# Xavier Setup

1. Jetpack SDK full install
2. Install NVMe SSD (great instructional article [here](https://medium.com/@ramin.nabati/installing-an-nvme-ssd-drive-on-nvidia-jetson-xavier-37183c948978))
3. 3D print Xavier base cover to hold antennas
4. Install wireless adapter and antennas
5. Install Node
6. Install, configure and start up a MongoDB instance
7. Create one 240GB EXT4 partition on the SSD
8. Copy the files in `scripts/Xavier/l4t-usb-device-mode` over to `/opt/nvidia/l4t-usb-device-mode/.`
9. Plug the rear USB C into a Windows or Mac, then `/opt/nvidia/l4t-usb-device-mode/nv-l4t-usb-device-mode-start.sh`
10. Once you see the drive come up on your Windows or Mac, reformat it (from said Windows/Mac) as EXT4
11. Eject the drive from Windows/Mac
12. Run `service nv-l4t-usb-device-mode stop`
13. Close and reopen the Disks app on Xavier
14. Create another partition, 284GB, EXT4
15. Create a partition image of the 240GB partition which you just reformatted- save it inside the new 284GB partition as `sdsusb.img`
16. Delete the 240GB partition
17. Create a 500GB EXT4 Partition
18. In `/opt/nvidia/l4t-usb-device-mode/nv-l4t-usb-device-mode-config.sh`, uncomment line 110 and comment line 109
19. Get the UUIDs of the two partions on the SSD, and update the CHANGEME areas of `./scripts/Xavier/setup.sh` appropriately
20. Run `./scripts/Xavier/setup.sh` and `./setup.sh` from the `scripts/alpr-unconstrained` directory
21. Reboot Xaxier
22. Add the lines in ./scripts/Xavier/crontab to your user's crontab
23. Congratulations, you are now a data hoarder.
24. The lp2 directory requires a weights file which you can download [here](https://drive.google.com/open?id=1XC8eu-GIAg_k9A07U-vl_sPjHrjYirnZ). This is simply custom training YoloV3 to detect license plates using the Google OpenImages dataset.
25. You should run the command in unixTS from within the mongo shell to add unixTS field to any existing poll docs. This will be implemented as an automated method shortly.

Try powering down the Xavier and plugging it into a Tesla USB slot (unplug your existing flash drive first if you're using one), using the provided Xavier USB-C to USB-A cable, and powering the Xavier via USB-C car charger (into the USB-C port on the side of the Xavier with the other various ports). Tesla will either automatically mount the device, or if you see the camera icon with a gray dot, you can press-hold on the camera button to mount the device. That gray dot should turn red.

---

_Next Up: Familiar Face Detection, then GUI. *Watch* this repo to be notified as code is released. Releasing code as soon as I am able._

# BOM

List:

- Nvidia Jetson Xavier (https://www.amazon.com/NVIDIA-Jetson-AGX-Xavier-Developer/dp/B07G5FCJQB) or Jetson Nano (https://www.amazon.com/NVIDIA-Jetson-Nano-Developer-Kit/dp/B07PZHBDKT)
- 1TB PCIe NVMe - M.2 (https://www.amazon.com/Samsung-970-PRO-Internal-MZ-V7P1T0BW/dp/B07BYHGNB5)
- Wireless Network Adapter (https://www.amazon.com/Wireless-Card-2-4GHz-Intel-8265-NGW/dp/B07Q3NG5CZ)
- Antennas for Wireless Adapter (https://www.amazon.com/CHAOHANG-RP-SMA-Antenna-Soldering-Wireless/dp/B01E29566W)
- USB C Car Charger - 30W Minimum (https://www.amazon.com/Charger-Anker-PowerDrive-Adapter-MacBook/dp/B071WYF9HP)
- USB C Cable (https://www.amazon.com/Anker-PowerLine-Durability-Including-Matebook/dp/B071XYBPMN)

# Disclaimer

This framework is provided for educational purposes only. Using this framework without permission from all appropriate parties may be against the law depending on your jurisdiction. Use at your own risk.

You may use this library with the understanding that doing so is **AT YOUR OWN RISK**. No warranty, express or implied, is made with regards to the fitness or safety of this code for any purpose. If you use this library to query or change settings of your vehicle you understand that it is possible to make changes that could inadvertently lower the security of your vehicle, or cause damage, through actions including but not limited to:

- Unlocking the vehicle
- Remotely starting the vehicle
- Opening the sunroof
- Opening the frunk or trunk
- Lowering the battery charge level
- Impacting the long-term health of your battery

Please be careful not to use this code in a way that loads the Tesla servers with too many concurrent requests. Calling the Tesla REST APIs at a very high frequency will stress the Tesla servers and could get your IP or favorite cloud service blocked by Tesla. Or in the worst case it could cause Tesla to revoke the key that enables access via this and many other libraries.
