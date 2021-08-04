---
layout: post
title: Filestore (Google CTF 2021)
date: 2021-07-24
tags:
- ctf
---

On July 16-17, I participated in the annual [Google CTF](https://capturetheflag.withgoogle.com/) competition. This was my first "real" CTF[^1], so my goal was simply to make it on the [scoreboard](https://capturetheflag.withgoogle.com/scoreboard/) by solving at least one of the challenges. After a few hours tinkering with rusty Python, I managed to solve the Filestore challenge and meet my goal (and had a lot of fun doing it). The original problem description and files are hosted on [GitHub](https://github.com/google/google-ctf/tree/master/2021/quals/misc-filestore). The remainder of this post describes the problem and my solution in detail.

## Problem

We are given a Python program, `filestore.py`, which appears to be capable of running some sort of file storage server. We are also given an address and port number for connecting to a running instance of the server.

Connecting to the server presents a menu of actions we can perform on the server:

```text
$ nc filestore.2021.ctfcompetition.com 1337
Welcome to our file storage solution.

Menu:
- load
- store
- status
- exit
```

1. `load` asks for a file ID and retrieves the file with the requested ID.
2. `store` asks for a line of data and returns a new randomly-generated file ID which may be used to retrieve the data.
3. `status` prints a user name, the current time, the amount of storage used, and the number of files stored:
   ```text
   User: ctfplayer
   Time: Sat Jul 17 13:15:05 2021
   Quota: 0.026kB/64.000kB
   Files: 1
   ```
  
Cracking open `filestore.py` reveals how the server works:

- It loads the flag into the file store automatically upon starting up. (This is why the initial status output shows "1" file stored.)
  ```python
  print("Welcome to our file storage solution.")

  # Store the flag as one of the files.
  store(bytes(flag, "utf-8"))
  ```
- The server's state consists of a blob of file data, a map of file IDs to file metadata, and a counter of used bytes:
  ```python
  blob = bytearray(2**16)
  files = {}
  used = 0
  ```
- The store function is a little complicated. Instead of simply storing the data contiguously in the `bytearray`, it partitions the data into variable size blocks so that it can re-use blocks which are the same between multiple files. This is presumably an optimization to save space. As it partitions the data into blocks, it constructs an ordered list of the indices and sizes of each block so that the original data may be recovered later. Finally, it generates a random ID for the file and maps the ID to the list of block indices and sizes.
  ```python
  # Use deduplication to save space.
  def store(data):
    nonlocal used
    MINIMUM_BLOCK = 16
    MAXIMUM_BLOCK = 1024
    part_list = []
    while data:
      prefix = data[:MINIMUM_BLOCK]
      ind = -1
      bestlen, bestind = 0, -1
      while True:
        ind = blob.find(prefix, ind+1)
        if ind == -1: break
        length = len(os.path.commonprefix([data, bytes(blob[ind:ind+MAXIMUM_BLOCK])]))
        if length > bestlen:
          bestlen, bestind = length, ind

      if bestind != -1:
        part, data = data[:bestlen], data[bestlen:]
        part_list.append((bestind, bestlen))
      else:
        part, data = data[:MINIMUM_BLOCK], data[MINIMUM_BLOCK:]
        blob[used:used+len(part)] = part
        part_list.append((used, len(part)))
        used += len(part)
        assert used <= len(blob)

      fid = "".join(secrets.choice(string.ascii_letters+string.digits) for i in range(16))
      files[fid] = part_list
      return fid
  ```
- The load function simply reconstructs the original file data by concatenating all of the blocks:
  ```python
  def load(fid):
    data = []
    for ind, length in files[fid]:
      data.append(blob[ind:ind+length])
    return b"".join(data)
  ```

## Solution

A key observation is that the "Quota" value returned in the output of the "status" action *leaks information about the data stored in the file store*. For example, if we see that the Quota value does not increase after storing some data, then we know that this data was already present in the file store. This gives us a basic strategy for finding the flag: Guess a portion of the flag value, store this value in the file store, and check whether the flag contains this value by noticing whether the Quota value changed after we stored the value.

As a first step, it is very helpful to be able to run the file store server locally for testing and debugging since communicating with the remote server over the network can be slow. All it takes to run `filestore.py` locally is to create a new file, `flag.py`, with a fake flag variable:

```python
flag = "CTF{abcdefghijklmnopqrstuv}"
```

I chose this value for the fake flag based on the following observations:

- I determined that the real flag had 27 characters by creating my own fake flags and comparing the Quota value obtained locally to the Quota value on the remote server.
- I also determined (by manually guessing) that the real flag started with "CTF{" and ended with "}".

A simple brute-force solution would involve storing every permutation of 27 ASCII characters until a permutation is found which does not change the Quota value. I felt this would be far too slow, so I used some heuristics to speed up the search. At a high level, my solution involves the following four steps:

1. Store each of the ASCII letters and numbers one at a time, noting when the Quota value remains the same. This gives the set of characters used in the flag. Use this set of characters for the following two steps.
2. Starting with `CTF{`, add one character to the end, store the value, and check the Quota value. Repeat using a different ending character until one is found which does not change the Quota value. When such a character is found, start from the beginning of Step 2 with this character on the end. Stop when the length is 16.
   - Why not stop when the length is 27? Only the first 16 bytes of the file is guaranteed to be stored sequentially (this is the prefix length in the `store` function). Thus, the 17th character of the guessed value is not guaranteed to be at the correct index.
3. Starting with `}`, do the same as in Step 2 except work backwards and stop when the length is 11.
4. Combine the values found in steps 2 and 3 to recover the flag.

The Python code for my solution is [here](). It uses the [pwntools](https://github.com/Gallopsled/pwntools) library for easily interacting with the remote server.

Running my solution on the remote server prints the flag as shown below:

```text
$ REMOTE=1 ./x.py
Finding the characters used in the flag...
['c', 'd', 'f', 'i', 'n', 'p', 't', 'u', 'C', 'F', 'M', 'R', 'T', 'X', '0', '1', '3', '4', '_', '{', '}']

Finding the left part of the flag...
CTF{C
CTF{CR
CTF{CR1
CTF{CR1M
CTF{CR1M3
CTF{CR1M3_
CTF{CR1M3_0
CTF{CR1M3_0f
CTF{CR1M3_0f_
CTF{CR1M3_0f_d
CTF{CR1M3_0f_d3
CTF{CR1M3_0f_d3d

Finding the right part of the flag...
n}
0n}
i0n}
ti0n}
4ti0n}
c4ti0n}
ic4ti0n}
1ic4ti0n}
p1ic4ti0n}
up1ic4ti0n}

Flag:
CTF{CR1M3_0f_d3dup1ic4ti0n}
```

Thanks to all of the Google CTF organizers for developing this challenge and many others!

[^1]: A CTF, or "Capture the Flag", is a type of computer security competition where teams of participants race to earn points by finding digital "flags" hidden on computer systems.
