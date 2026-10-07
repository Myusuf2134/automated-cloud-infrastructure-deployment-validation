#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

install -d -m 0755 /opt/deployment-demo
echo '${app_py_base64}' | base64 --decode > /opt/deployment-demo/app.py
echo '${app_requirements_base64}' | base64 --decode > /opt/deployment-demo/requirements.txt
echo '${app_dockerfile_base64}' | base64 --decode > /opt/deployment-demo/Dockerfile

docker build -t deployment-demo:local /opt/deployment-demo
docker run --detach \
  --name deployment-demo \
  --restart unless-stopped \
  --publish ${application_port}:8080 \
  deployment-demo:local
