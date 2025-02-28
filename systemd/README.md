# Systemd Service Installation

This application can start up automatically on reboot of your Raspberry Pi. Use the following commands to install the service, start it, and enable it to start up on reboot:

```bash
cd /home/pi/repos/pi-random-qr-print
sudo cp systemd/pi-random-qr-print.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl stop pi-random-qr-print.service
sudo systemctl start pi-random-qr-print.service
sudo systemctl enable pi-random-qr-print.service
```
