from ubuntu:20.04

run apt-get -qq update && apt-get install -qq --no-install-recommends xinetd socat python3 qemu-user-static

copy service.py /service.py
copy shuffl /
copy runner-x86_64 /
copy runner-aarch64 /
copy runner-riscv64 /

copy service.conf /
copy banner_fail /
copy wrapper /

run echo "[]" > /history.txt
run chmod 600 /history.txt
run echo 0 >> /score; echo X >> /score; echo Y >> /score
run chmod 600 /score

expose 9090


cmd chmod go-rw / && chmod go-rwx /proc && xinetd -filelog /dev/stderr -dontfork -f /service.conf
# ^^ Assuming that ps would be too revealing.
#    AFAIK, this also disables the built-in printf(%n) protection. Alternatively:
#cmd ["/usr/sbin/xinetd", "-filelog", "/dev/stderr", "-dontfork", "-f", "/service.conf"]
