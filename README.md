# MARVEL : Mobile Augmented Reality with Viable Energy and Latency
[![Build Status](https://travis-ci.com/kaifeichen/MARVEL.svg?token=XjizLR77Z2rgJhyHZZ73&branch=master)](https://travis-ci.com/kaifeichen/MARVEL)

## What is MARVEL? 
MARVEL is a system that allows you to interact with smart building appliances by taking pictures of them.


## How to Run MARVEL server?

### Server Environment
The easiest way to run MARVEL server is using the prebuilt [docker image](https://hub.docker.com/r/kaifeichen/snaplink/). To get the docker image, run
```bash
docker pull kaifeichen/snaplink
```

If you want to build your own environment, follow the [install script](script/install.sh).

### Compile
Clone the MARVEL server repository
```bash
git clone https://github.com/kaifeichen/MARVEL
```
Use cmake and make to compile in the [build/](build) folder
```bash
cd build/
cmake ..
make -j $(nproc)
```


### Run

#### standalone
To run a MARVEL server
```bash
snaplink run [db_file...]
```

Here is an example that runs it with all data in *~/data/sensys18/*:
```bash
snaplink run `find ~/data/sensys18/ -iname *.db`
```


## SnapLink Server API

SnapLink server has a GRPC front end.

## Do you have MARVEL client?
Yes! There is an [Android client](https://github.com/SoftwareDefinedBuildings/MARVEL_Android). 
There are also python clients for both BOSSWAVE and HTTP in the [test/](test) folder.


## License

```
Copyright (c) 2016-2017, Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions 
are met:

 - Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 - Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Questions? 

Please Email Kaifei Chen <kaifei@berkeley.edu> or Tong Li <sasrwas@berkeley.edu>
