# This container is built on top of the patched-service ones
FROM ubuntu:20.04

run apt-get update && apt-get -qq --no-install-recommends install python3-pip build-essential
run pip install pwntools
run apt-get -qq --no-install-recommends install binutils-multiarch

copy test.py /
