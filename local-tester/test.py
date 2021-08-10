#!/usr/bin/env python3

import stat
import time
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

assert not (os.stat("score").st_mode & stat.S_IROTH)
assert not (os.stat("history.txt").st_mode & stat.S_IROTH)

# test the default block list
p = pwn.process(CMD, env={"INITIAL_BLOCKED": "31c0", "TEAM_NAME": "A"})
p.clean()
p.sendline(SHELL_SIMPLE)
o = p.readall()
assert b"contains blocked bytes: 31 c0" in o
assert b"pass the constraints" in o
assert not ast.literal_eval(open("score").read())

# initialize it with some shit
p = pwn.process(CMD, env={"TEAM_NAME": "A"})
p.clean()
p.sendline(SHELL_SIMPLE)
o = p.readall()
assert b"first" in o
assert b"CONGRAT" in o
assert ast.literal_eval(open("score").readlines()[-1]) == [ "A" ]

# try that again (should fail)
p = pwn.process(CMD, env={"TEAM_NAME": "B"})
p.clean()
p.sendline(SHELL_SIMPLE)
assert b"Alas" in p.readall()
assert ast.literal_eval(open("score").readlines()[-1]) == [ "A" ]

# make sure double submissions are blocked
p = pwn.process(CMD, env={"TEAM_NAME": "A"})
o = p.readall()
assert b"already own" in o
assert b"CONGRAT" not in o

# try it shorter
p = pwn.process(CMD, env={"TEAM_NAME": "C"})
p.clean()
p.sendline(SHELL_SIMPLE2)
o = p.readall()
assert b"elegance" in o
assert b"CONGRAT" in o
assert ast.literal_eval(open("score").readlines()[-1]) == [ "C", "A" ]

# try it shorter again
p = pwn.process(CMD)
p.clean()
p.sendline(SHELL_SIMPLE2)
assert b"Alas" in p.readall()

# try the non-H
p = pwn.process(CMD, env={"TEAM_NAME": "D"})
p.clean()
p.sendline(SHELL_NOH)
o = p.readall()
assert b"CONGRAT" in o
assert b"evolved" in o
assert b"immune" in o
assert b"48" in o.split(b"immune")[-1]
assert ast.literal_eval(open("score").readlines()[-1]) == [ "D", "C", "A" ]

# try a blocked byte
p = pwn.process(CMD)
p.clean()
p.sendline(SHELL_SIMPLE2)
o = p.readall()
assert b"contains blocked" in o
assert b"pass the constraints" in o

# try it shorter
p = pwn.process(CMD, env={"TEAM_NAME": "C"})
p.clean()
p.sendline(SHELL_NOH2)
o = p.readall()
assert b"CONGRAT" in o
assert b"evolved" in o
assert b"immune" in o
assert b"00" in o.split(b"immune")[-1]
assert ast.literal_eval(open("score").readlines()[-1]) == [ "C", "D", "A" ]

# wait for the timout
time.sleep(2)
p = pwn.process(CMD, env={"VICTORY_TIMEOUT": "1", "TEAM_NAME": "E"})
prompt = p.readrepeat(timeout=0.5)
p.sendline(SHELL_NO0f)
o = p.readall()
assert (b"with " + SHELL_NOH2) in prompt
assert b"CONGRAT" in o
assert ast.literal_eval(open("score").readlines()[-1]) == [ "E", "C" ]

# let's see how good pwntools is
for i in range(10):
	p = pwn.process(CMD, env={"TEAM_NAME": f"WARRIOR_{i}"})
	prompt = p.readuntil(b"Blocked bytes: ")
	blocked = list(bytes.fromhex(p.readline().replace(b" ", b"").strip().decode('latin1')).decode('latin1'))
	print(blocked)
	shellcode = pwn.encode(pwn.asm(pwn.shellcraft.cat("secret")), avoid=blocked, force=True)
	if set(shellcode.decode('latin1')) & set(blocked):
		print(f"pwntools encoder FAILED after {i} successes")
		break
	p.sendline(shellcode.hex())
	o = p.readall()
	assert b"CONGRAT" in o

# make sure aarch64 works
os.unlink("history.txt")
p = pwn.process(CMD, env={"TEAM_NAME": "F"})
prompt = p.readrepeat(timeout=0.5)
p.sendline(SHELL_AARCH64)
o = p.readall()
assert b"CONGRAT" in o
assert ast.literal_eval(open("score").readlines()[-1]) == [ "F" ]
