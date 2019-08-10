mkdir /tesladrive
touch /tesladrive/recentfiles.txt
touch /tesladrive/savedfolders.txt
mkdir /teslaflash
mkdir /media/CHANGEME(USERNAME)/SCOUT
chmod 755 /media/CHANGEME(USERNAME)/SCOUT
chmod 755 /tesladrive
chmod 755 /teslaflash

echo "UUID=CHANGEME(UUID_OF_500GB_PARTITION) /tesladrive ext4 defaults 0 2" >> /etc/fstab
echo "UUID=CHANGEME(UUID_OF_284GB_PARTITION) /teslaflash ext4 defaults 0 2" >> /etc/fstab

cp checkCopy.sh ~/. && chmod +x ~/checkCopy.sh