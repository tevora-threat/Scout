#!/bin/bash

# Copyright (c) 2017-2019, NVIDIA CORPORATION.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AS IS AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

set -e

script_dir="$(cd "$(dirname "$0")" && pwd)"
. "${script_dir}/nv-l4t-usb-device-mode-config.sh"

# Wait for any modules to load and initialize
for attempt in $(seq 60); do
    udc_dev_t210=700d0000.xudc
    if [ -e "/sys/class/udc/${udc_dev_t210}" ]; then
        udc_dev="${udc_dev_t210}"
        break
    fi
    udc_dev_t186=3550000.xudc
    if [ -e "/sys/class/udc/${udc_dev_t186}" ]; then
        udc_dev="${udc_dev_t186}"
        break
    fi
    sleep 1
done
if [ "${udc_dev}" == "" ]; then
    echo No known UDC device found
    exit 1
fi

macs_file="${script_dir}/mac-addresses"
if [ -f "${macs_file}" ]; then
    . "${macs_file}"
else
    # Generate unique data
    if [ -f /proc/device-tree/serial-number ]; then
        random="$(md5sum /proc/device-tree/serial-number|cut -c1-12)"
    else
        random="$(echo "no-serial"|md5sum|cut -c1-12)"
    fi
    # Extract 6 bytes
    b1="$(echo "${random}"|cut -c1-2)"
    b2="$(echo "${random}"|cut -c3-4)"
    b3="$(echo "${random}"|cut -c5-6)"
    b4="$(echo "${random}"|cut -c7-8)"
    b5="$(echo "${random}"|cut -c9-10)"
    b6="$(echo "${random}"|cut -c11-12)"
    # Clear broadcast/multicast, set locally administered bits
    b1="$(printf "%02x" "$(("0x${b1}" & 0xfe | 0x02))")"
    # Set 4 LSBs to unique value per interface
    b6_rndis_h="$(printf "%02x" "$(("0x${b6}" & 0xfc | 0x00))")"
    b6_rndis_d="$(printf "%02x" "$(("0x${b6}" & 0xfc | 0x01))")"
    b6_ecm_h="$(printf "%02x" "$(("0x${b6}" & 0xfc | 0x02))")"
    b6_ecm_d="$(printf "%02x" "$(("0x${b6}" & 0xfc | 0x03))")"
    # Construct complete MAC per interface
    mac_rndis_h="${b1}:${b2}:${b3}:${b4}:${b5}:${b6_rndis_h}"
    mac_rndis_d="${b1}:${b2}:${b3}:${b4}:${b5}:${b6_rndis_d}"
    mac_ecm_h="${b1}:${b2}:${b3}:${b4}:${b5}:${b6_ecm_h}"
    mac_ecm_d="${b1}:${b2}:${b3}:${b4}:${b5}:${b6_ecm_d}"
    # Save values for next boot
    echo "mac_rndis_h=${mac_rndis_h}" > "${macs_file}"
    echo "mac_rndis_d=${mac_rndis_d}" >> "${macs_file}"
    echo "mac_ecm_h=${mac_ecm_h}" >> "${macs_file}"
    echo "mac_ecm_d=${mac_ecm_d}" >> "${macs_file}"
fi

mkdir -p /sys/kernel/config/usb_gadget/l4t
cd /sys/kernel/config/usb_gadget/l4t

echo 0x0103 > bcdDevice
echo 0x0200 > bcdUSB
echo 0x00 > bDeviceClass
echo 0x00 > bDeviceSubClass
echo 0x00 > bDeviceProtocol


mkdir -p strings/0x409
if [ -f /proc/device-tree/serial-number ]; then
    serialnumber="$(cat /proc/device-tree/serial-number|tr -d '\000')"
else
    serialnumber=no-serial
fi

echo "4C531001640415103560" > strings/0x409/serialnumber
echo "SanDisk" > strings/0x409/manufacturer
echo "Ultra" > strings/0x409/product

cfg=configs/c.1
mkdir -p "${cfg}"
cfg_str=""

# Note: RNDIS must be the first function in the configuration, or Windows'
# RNDIS support will not operate correctly.
if [ ${enable_rndis} -eq 1 ]; then
    cfg_str="${cfg_str}+RNDIS"
    func=functions/rndis.usb0
    mkdir -p "${func}"
    echo "${mac_rndis_h}" > "${func}/host_addr"
    echo "${mac_rndis_d}" > "${func}/dev_addr"
    ln -sf "${func}" "${cfg}"

    # Informs Windows that this device is compatible with the built-in RNDIS
    # driver. This allows automatic driver installation without any need for
    # a .inf file or manual driver selection.
    echo 1 > os_desc/use
    echo 0xcd > os_desc/b_vendor_code
    echo MSFT100 > os_desc/qw_sign
    echo RNDIS > "${func}/os_desc/interface.rndis/compatible_id"
    echo 5162001 > "${func}/os_desc/interface.rndis/sub_compatible_id"
    ln -sf "${cfg}" os_desc
fi

# If two USB configs are created, and the second contains RNDIS and ACM, then
# Windows will ignore at the ACM function in that config. Consequently, this
# script creates only a single USB config.
if [ ${enable_acm} -eq 1 ]; then
    cfg_str="${cfg_str}+ACM"
    func=functions/acm.GS0
    mkdir -p "${func}"
    ln -sf "${func}" "${cfg}"
fi

if [ ${enable_ums} -eq 1 ]; then
    cfg_str="${cfg_str}+UMS"
    func=functions/mass_storage.0
    mkdir -p "${func}"
    ln -sf "${func}" "${cfg}"
    # Prevent users from corrupting the disk image; make it read-only
    echo " ${func}   ${cfg} "
    # echo 0 > "${func}/lun.0/ro"
    echo 1 > "${func}/lun.0/removable"
    # echo 0 > "${func}/lun.0/stall"
    # echo 123456 > "${func}/lun.0/iSerialNumber"
    echo "${fs_img}" > "${func}/lun.0/file"
fi

if [ ${enable_ecm} -eq 1 ]; then
    cfg_str="${cfg_str}+ECM"
    func=functions/ecm.usb0
    mkdir -p "${func}"
    echo "${mac_ecm_h}" > "${func}/host_addr"
    echo "${mac_ecm_d}" > "${func}/dev_addr"
    ln -sf "${func}" "${cfg}"
fi

mkdir -p "${cfg}/strings/0x409"
# :1 in the variable expansion strips the first character from the value. This
# removes the unwanted leading + sign. This simplifies the logic to construct
# $cfg_str above; it can always add a leading delimiter rather than only doing
# so unless the string is previously empty.
echo "${cfg_str:1}" > "${cfg}/strings/0x409/configuration"

# Create and configure the network bridge before setting the UDC device. This
# ensures that no matter how quickly udev events (which run -runtime-start.sh)
# are triggered after setting the UDC device below, the bridge device is
# guaranteed to exist, so -runtime-start.sh is guaranteed to be able to
# configure it.
#
# Set the device to "down" initially; if/when -runtime-start.sh runs in response
# to cable presence, the interface will be set to "up".
/sbin/brctl addbr l4tbr0
/sbin/ifconfig l4tbr0 ${net_ip} netmask ${net_mask} down
/sbin/ifconfig l4tbr0 add ${net_ipv6}

echo "${udc_dev}" > UDC

# Ethernet devices require additional configuration. This must happen after the
# UDC device is assigned, since that triggers the creation of the Tegra-side
# Ethernet interfaces.
#
# This script always assigns any-and-all Ethernet devices to an Ethernet
# bridge, and assigns the static IP to that bridge. This allows the script to
# more easily handle the potentially variable set of Ethernet devices.
#
# If your custom use-case requires separate IP addresses per interface, or
# only ever has one interface active, you may modify this script to skip
# bridge creation, and assign IP address(es) directly to the interface(s).

if [ ${enable_rndis} -eq 1 ]; then
    /sbin/brctl addif l4tbr0 "$(cat functions/rndis.usb0/ifname)"
    /sbin/ifconfig "$(cat functions/rndis.usb0/ifname)" up
fi

if [ ${enable_ecm} -eq 1 ]; then
    /sbin/brctl addif l4tbr0 "$(cat functions/ecm.usb0/ifname)"
    /sbin/ifconfig "$(cat functions/ecm.usb0/ifname)" up
fi

cd - # Out of /sys/kernel/config/usb_gadget

# Create a local disk device that exposes the same filesystem image that's
# exported over USB. This will allow local users to see the files too.
# turning off below line because we need to mount in read/write mode, not readonly
#/sbin/losetup -f -r "${fs_img}"

exit 0
