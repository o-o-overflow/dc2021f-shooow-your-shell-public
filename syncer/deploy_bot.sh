#!/bin/bash

docker build -t shooow-your-shell-syncer . && docker tag shooow-your-shell-syncer registry.31337.ooo:5000/shooow-your-shell-syncer && docker push registry.31337.ooo:5000/shooow-your-shell-syncer

ssh -t master.admin.31337.ooo "sudo kubectl delete pod -l app=shooow-your-shell-syncer"
