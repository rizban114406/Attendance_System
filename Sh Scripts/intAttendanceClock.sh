
#!/bin/bash

sleep 12s

while  :
do
read -r url < /root/heartBitUrl.txt
if curl -m 5 "$url" > /dev/null
then
read -r ipAddress < /root/ntpServer.txt
sudo /etc/init.d/ntp stop
sudo ntpdate -s "$ipAddress"
sudo /etc/init.d/ntp start
break
fi
sleep 2s
done

sleep 3s
while :
do
cd /
cd /root/
sudo python attendanceClock.py
cd /
done
