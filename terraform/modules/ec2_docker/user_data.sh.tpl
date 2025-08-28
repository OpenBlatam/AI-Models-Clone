#!/bin/bash
apt-get update
apt-get install -y docker.io git curl
usermod -aG docker ubuntu
curl -L "${docker_compose_url}" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
git clone -b ${branch} ${repo_url} /srv/app
cd /srv/app/${feature_path}
docker-compose -f ${compose_file} up -d 