#! /bin/bash
touch release/apt-get.sh
chmod +x release/apt-get.sh
echo "#! /bin/bash" > release/apt-get.sh
echo sudo apt-get install --assume-yes $(comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n 's/^Package: //p' | sort -u)) >> release/apt-get.sh

