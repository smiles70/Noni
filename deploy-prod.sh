#!/usr/bin/env bash
set -e
cd /home/hazbyn/Noni
railway up \
  --project 2e666ec8-c007-4054-b763-0d45d30759a2 \
  --service 3f9c0c51-c82d-4d92-b159-09d5f0509c4d \
  --environment 61bd7eea-6471-4ba2-b3d8-23e1c35f8dc1 \
  -y
