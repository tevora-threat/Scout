mkdir /tesladrive
touch /tesladrive/recentfiles.txt
touch /tesladrive/savedfolders.txt
mkdir /teslaflash
mkdir /media/l0r3zz/SCOUT
chmod 755 /media/l0r3zz/SCOUT
chmod 755 /tesladrive
chmod 755 /teslaflash
mkdir -p /tesladrive/Videos/RecentClips
mkdir /tesladrive/Videos/SavedClips
mkdir /tesladrive/Frames
mkdir -p /tesladrive/detections/plates
mkdir /tesladrive/detections/vehicles
mkdir ~/scripts
cp preprocessing/* ~/scripts/.
chmod +x ~/scripts/preprocess.sh
sudo cp rc.local /etc/. && chmod +x /etc/rc.local 

echo "UUID=a562f68b-8044-4854-b689-0bb854cf100b /tesladrive ext4 defaults 0 2" >> /etc/fstab
echo "UUID=5f4c0e3b-92b5-4183-abaf-c4b56470213c /teslaflash ext4 defaults 0 2" >> /etc/fstab

cp checkCopy.sh ~/. && chmod +x ~/checkCopy.sh

