#!/usr/bin/env python3

import time
import sys
import ast
import pwn
import os

pwn.context.log_level = 'DEBUG'
pwn.context.arch = 'amd64'

SHELL_SIMPLE = b"31c0b00231f6488d3d1a0000000f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0573656372657400"
SHELL_SIMPLE2 = b"31c0b00231f6488d3d1a0000000f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f05736563726574"
SHELL_NOH = b"31c0b00231f6eb215f0f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0531c0b03c0f05e8daffffff73656372657400"
SHELL_NOH2 = b"31c0b00231f6eb215f0f0531c031ff40b703545e31d2b2200f0531c0b00140b7010f0531c0b03c0f05e8daffffff736563726574"
SHELL_NO0f = b"fe052b00000031c0b00231f6488d3d21000000e81900000031c031ff40b703545e31d2b220e80700000031c0b00140b7010e05c373656372657400"
SHELL_AARCH64 = b"6eae8cd26e4caef2ae8ccef2ee0f1ff880f39fd2e0ffbff2e0ffdff2e0fffff2e1030091e2031faae3031faa080780d2010000d4e10300aa200080d2e2031faae3ff9fd2e3ffaff2e80880d2010000d4"

if os.getuid() != 0:
	CMD = "sudo --preserve-env=INITIAL_BLOCKED,VICTORY_TIMEOUT,TEAM_NAME python service.py".split()
else:
	CMD = "./service.py".split()

if os.path.exists("history.txt"):
	os.unlink("history.txt")
if os.path.exists("score"):
	os.unlink("score")

# initialize it with some shit
p = pwn.remote(sys.argv[1], int(sys.argv[2]))
p.clean()
p.sendline(SHELL_SIMPLE)
o = p.readall()
assert b"first" in o
assert b"CONGRAT" in o

# make sure double submissions are blocked
p = pwn.remote(sys.argv[1], int(sys.argv[2]))
o = p.readall()
assert b"already own" in o
assert b"CONGRAT" not in o
