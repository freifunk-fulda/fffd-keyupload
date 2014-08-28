#!/bin/sh
set -e

IFACES=$(ls /var/lib/vnstat/)

TARGET=/var/www/gw01.freifunk-fulda.de/

for iface in $IFACES; do
    /usr/bin/vnstati -i ${iface} -h -o ${TARGET}${iface}_hourly.png
    /usr/bin/vnstati -i ${iface} -d -o ${TARGET}${iface}_daily.png
    /usr/bin/vnstati -i ${iface} -m -o ${TARGET}${iface}_monthly.png
    /usr/bin/vnstati -i ${iface} -t -o ${TARGET}${iface}_top10.png
    /usr/bin/vnstati -i ${iface} -s -o ${TARGET}${iface}_summary.png
done

cat > ${TARGET}stats <<EOT
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Freifunk Fulda</title>
  </head>

<body>
EOT

for iface in $IFACES; do
  sed s/IFACE/${iface}/g >> ${TARGET}stats.html <<EOT
  <div style="display:inline-block;vertical-align: top">
    <img src="IFACE_summary.png" alt="traffic summary" /><br>
    <img src="IFACE_monthly.png" alt="traffic per month" /><br>
    <img src="IFACE_hourly.png" alt="traffic per hour" /><br>
    <img src="IFACE_top10.png" alt="traffic top10" /><br>
    <img src="IFACE_daily.png" alt="traffic per day" />
  </div>
EOT

done

cat >> ${TARGET}stats.html <<EOT
</body>
</html>
EOT
