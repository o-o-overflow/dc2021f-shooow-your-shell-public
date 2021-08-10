# This container is built on top of the patched-service ones
ARG SERVICE=build--this--with--a--build-arg
FROM $SERVICE

run apt-get -qq --no-install-recommends install python3-pip
run pip install pwntools
run apt-get -qq --no-install-recommends install binutils-multiarch build-essential

copy test.py /
