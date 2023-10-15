#! /bin/bash

# get docker per https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
apt-get update
apt-get install ca-certificates curl gnupg
install -m 0755 /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

# in a production environment, these would be version pinned
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

