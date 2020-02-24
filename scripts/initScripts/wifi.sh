#!/bin/bash
nmcli radio wifi off
rfkill unblock wlan

sleep 10

WLAN_IF=wlan0

SSID='testingtime' #CHANGEME
WPA_PASSPHRASE='testboi' #CHANGEME

ifconfig $WLAN_IF up 10.0.0.1 netmask 255.255.255.0
ifconfig $WLAN_HS up
echo "bringing wifi interface online"
sleep 10

cat <<-EOF > ./hostapd.conf
interface=${WLAN_IF}
ssid=${SSID}
channel=11
driver=nl80211
wpa=2
wpa_passphrase=${WPA_PASSPHRASE}
hw_mode=g
EOF

echo "starting dhcp server"
if [ "$(ps -e | grep dhcpd)" == "" ]; then
    dhcpd -cf ./dhcpd.conf  
fi
###########
#Enable NAT
echo "flushing dhcp rules"
iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain

if [ $# -eq 1 ]
then

XAVIER_IP=$1
iptables -t nat -A PREROUTING -s $XAVIER_IP

iptables -t nat -A PREROUTING -p tcp -d 172.217.164.110 --dport 80  -j DNAT --to $XAVIER_IP:80 #CHANGEME
iptables -t nat -A PREROUTING -p tcp -d 172.217.164.110 --dport 443  -j DNAT --to $XAVIER_IP:443 #CHANGEME

fi

iptables -t nat -A PREROUTING -s $XAVIER_IP
iptables -t nat -A POSTROUTING  -j MASQUERADE
 
sysctl -w net.ipv4.ip_forward=1
hostapd ./hostapd.conf 
killall dhcpd

iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
sysctl -w net.ipv4.ip_forward=0
