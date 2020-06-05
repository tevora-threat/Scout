mkdir -p /tesladrive
touch  /tesladrive/recentfiles.txt
touch  /tesladrive/savedfolders.txt
mkdir -p /teslaflash
mkdir -p /media/l0r3zz
mkdir -p /media/l0r3zz/SCOUT
chmod 755 /media/l0r3zz/SCOUT
chmod 755 /tesladrive
chmod 755 /teslaflash
mkdir -p /tesladrive/Videos/RecentClips
mkdir -p /tesladrive/Videos/SavedClips
mkdir -p /tesladrive/Frames
mkdir -p /tesladrive/detections/plates
mkdir -p /tesladrive/detections/vehicles
mkdir -p ~/scripts
cp scripts/Nano/preprocessing/* ~/scripts/.
chmod +x ~/scripts/preprocess.sh
sudo cp scripts/Nano/rc.local /etc/. && chmod +x /etc/rc.local 

echo "UUID=a562f68b-8044-4854-b689-0bb854cf100b /tesladrive ext4 defaults 0 2" >> /etc/fstab
echo "UUID=5f4c0e3b-92b5-4183-abaf-c4b56470213c /teslaflash ext4 defaults 0 2" >> /etc/fstab

cp scripts/Nano/checkCopy.sh ~/. && chmod +x ~/checkCopy.sh

