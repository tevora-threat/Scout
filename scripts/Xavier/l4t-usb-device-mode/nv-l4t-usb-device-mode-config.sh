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

# These variables define which set of protocols are supported. Each variable
# should be set to either 0 or 1. Note that Windows caches information about
# each USB device; if these values are changed, Windows users may need to
# manually uninstall drivers/devices using Device Manager, delete cached USB OS
# descriptors using regedit on HLKM\SYSTEM\CurrentControlSet\Control\UsbFlags,
# and delete cached OEM .inf files using pnputil -d. These actions require
# considerable care to avoid impacting other devices and drivers. Linux and
# MacOS do not appear to have this issue.
#
# If this script is modified in a way that alters information visible to the
# USB host (adding/removing/enabling/disabling/reordering protocols, or
# adding/removing/modifying OS descriptors), then the host must be informed of
# this by modifying the USB device identity:
#
# - NVIDIA engineers should increase the bcdDevice value that is written below.
#
# - NVIDIA customers MUST initially change the idVendor, idProduct values and
#   manufacturer and product strings that are set below and reset the bcdDevice
#   value to 1. Later modifications may simply increase the bcdDevice value.
#
# - In all cases, any associated Windows INF files MUST be updated to match the
#   changes made here, or Windows will not match the INF file against the HW.
#
# Ethernet using the RNDIS protocol.
# Linux: Supported automatically.
# Windows: Supported automatically via OS descriptors.
# MacOS: Requires the HoRNDIS driver to be installed.
enable_rndis=0
# CDC ACM serial port/UART.
# Linux: Supported automatically.
# Windows 10: Supported automatically.
# Windows other: Requires driver manual selection by use of l4t-serial.inf.
# Mac OS: Supported automatically.
enable_acm=0
# Ethernet using the CDC ECM protocol.
# Linux: Supported automatically.
# Windows: Not supported.
# Mac OS: Supported automatically.
enable_ecm=0
# USB Mass Storage (virtual disk drive/USB memory stick).
# Linux: Supported automatically.
# Windows: Supported automatically.
# Mac OS: Supported automatically.
enable_ums=1

# The IP address shared by all USB network interfaces created by this script.
net_ip=192.168.55.1
# The associated netmask.
net_mask=255.255.255.0
# The associated network address.
net_net=192.168.55.0
# DHCP parameters:
# Linux kernel 4.8 and later contain commit a5a18bdf7453 "rndis_host: Set valid
# random MAC on buggy devices", which causes any device-provided MAC address to
# be replaced with a host generated random MAC address. This circumvents this
# script's attempt to set up a consistent MAC address. To work around this, a
# DHCP pool with a single entry (net_dhcp_start==net_dhcp_end) must be used so
# that no matter what MAC address the host chooses, it will always receive the
# same IP address. To prevent this from causing pool exhaustion, the DHCP lease
# time must be set to a very small value so that when Jetson reboots or is
# power cycled, the lease will have expired by the time the reboot has
# completed. Cable unplug/replug can occur much more quickly; an IP address may
# not be assigned for roughly 15 seconds (plus host DHCP request repeat delay)
# after a quick unplug/replug.
# The DHCP pool range
net_dhcp_start=192.168.55.100
net_dhcp_end=192.168.55.100
# The duration of a DHCP lease
net_dhcp_lease_time=15
# The IPv6 address shared by all USB network interfaces created by this script.
# This should be a link-local address.
net_ipv6=fe80::1
# The metric of the IPv4 default route; higher value is lower priority
# Leave blank to prevent creating a default route
net_ipv4_defroute_router=192.168.55.100
# The metric value for the default route; can be empty for none.
# Empirically, 32766 is the largest metric value, so lowest priority available.
net_ipv4_defroute_metric=32766

# The disk image to export as a USB Mass Storage device
fs_img="/dev/nvme0n1p1"
#fs_img="/teslaflash/sdsusb.img"

