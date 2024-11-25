sudo systemctl stop vboxdrv
sudo modprobe -r vboxnetadp vboxnetflt vboxdrv
sudo modprobe vboxdrv
sudo modprobe vboxnetflt
sudo modprobe vboxnetadp

sudo systemctl restart vboxdrv
