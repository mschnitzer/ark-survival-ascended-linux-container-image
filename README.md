# ARK: Survival Ascended - Dedicated Linux Server - Docker Image

This repository provides a step by step guide for Linux administrators to host ARK: Survival Ascended servers on Linux using a docker image.

## Table of Contents

* [Hardware Requirements](#hardware-requirements)
* [Installation](#installation)
  * [Install Docker & Docker Compose](#1-install-docker--docker-compose)
  * [Start docker daemon](#2-start-docker-daemon)
  * [Create the Docker Compose config](#3-create-the-docker-compose-config)
  * [First server start](#4-first-server-start)
  * [Server configuration](#5-server-configuration)
  * [Changing the start parameters AND the player limit](#6-changing-the-start-parameters-and-the-player-limit)
* [Port forwarding?](#port-forwarding)
* [Changing the game port and RCON port](#changing-the-game-port-and-rcon-port)
* [Start/Restart/Stop](#startrestartstop)
* [Setting up a second server](#setting-up-a-second-server)
* [Found an Issue or Bug?](#found-an-issue-or-bug)
* [Credits](#credits)

## Hardware Requirements

The hardware requirements might change over time, but as of today you can expect:

* ~11 GB RAM usage per server instance
* ~9.1 GB disk space (the server files alone, without any savegames)

I cannot tell you what CPU to use, as I didn't do any testing on this, but this is the hardware I'm running one ASA server on:

* Intel Xeon E3-1275v5
* 2x SSD M.2 NVMe 512 GB
* 4x RAM 16384 MB DDR4 ECC

The server runs next to other services and it runs pretty well.

## Installation

Required Linux experience: **Beginner**

In theory, you can use these steps on any Linux system where Docker is installed. It has been tested with:

* openSUSE Leap 15.5
* Debian 12 (bookworm)
* Ubuntu 22.04.3 LTS (Jammy Jellyfish)
* Ubuntu 23.10 (Mantic Minotaur)

You need to be root user (`su root`) to perform these steps, but don't worry, the ASA server itself will run rootless.

### 1. Install Docker & Docker Compose

#### openSUSE Leap 15.5:

```
zypper in -y docker docker-compose
```

#### Debian 12

```
apt-get install -y docker docker-compose
```

#### Ubuntu (22.04.x):

```
apt-get install -y docker docker-compose
```

#### Ubuntu (23.x):

The default repositories of Ubuntu 23.x do no longer serve the docker engine. Thus you need to add the official docker repository manually to proceed. Please refer to
[this guide](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and follow the steps outlined in the "Install using the apt repository" section.

Additionally to the steps of the official docker guide, you need to install `docker-compose` as well:

```
apt-get install -y docker-compose
```

### 2. Start docker daemon

```
systemctl start docker
systemctl enable docker
```

### 3. Create the Docker Compose config

Create a directory called `asa-server` wherever you like and download [my docker-compose.yml](https://github.com/mschnitzer/ark-survival-ascended-linux-container-image/blob/main/docker-compose.yml) example.

```
mkdir asa-server
cd asa-server
wget https://raw.githubusercontent.com/mschnitzer/ark-survival-ascended-linux-container-image/main/docker-compose.yml
```

### 4. First server start

Now start the server for the first time. It will install Steam, Proton, and downloads the ARK: Survival Ascended server files.

Go to the directory of your `docker-compose.yml` file and execute the following command:

```
docker-compose up -d
```

It will download my docker image and then spins up a container called `asa-server-1` (defined in `docker-compose.yml`). You can follow the installation and the start of your server by running:

```
docker logs -f asa-server-1
```

(Note: You can safely run `CTRL + C` to exit the log window again without causing the server to stop)

Once the log shows the following line:

```
Starting the ARK: Survival Ascended dedicated server...
```

... the server should be reachable and discoverable through the server browser in ~2-5 minutes.

The server name is randomly generated upon the first start. Please execute the following command to see under which name the server is discoverable in the server browser:
```
docker exec asa-server-1 cat server-files/ShooterGame/Saved/Config/WindowsServer/GameUserSettings.ini | grep SessionName
```

If the command fails in execution and reports an `No such file or directory` error, just wait some more minutes and it should eventually work. Once the command executed successfully, it should output something like this:
```
SessionName=ARK #334850
```

Now try to find the server by its name. Just search in the "Unofficial" section in ASA for the number of the server. In my case it is `334850`. If you are not able to connect to it right away, wait up to 5 more minutes and
try it again. If it's still not possible, [open an issue on GitHub](https://github.com/mschnitzer/ark-survival-ascended-linux-container-image/issues/new) to get help.

Once confirmed that you are able to connect, stop the server again:

```
docker stop asa-server-1
```

### 5. Server configuration

The `docker-compose.yml` config defines three docker volumes, which serve as a storage for your server files, Steam, and Proton. They are directly mounted to the docker container and can be edited outside of the container. The
location of these volumes is `/var/lib/docker/volumes`. If you followed the steps 1:1, then you should find the following directories at that location:

```
asa-server_server-files-1/
asa-server_steam-1/
asa-server_steamcmd-1/
```

The prefix `asa-server` is defined by the directory name of your `docker-compose.yml` file.

You can ignore `asa-server_steam-1` and `asa-server_steamcmd-1`, these volumes are being used by the container to avoid setting up `Steam` and `steamcmd` on every launch again. Server files including config files are stored at `asa-server_server-files-1`.

The `GameUserSettings.ini` and `Game.ini` file can be found at `/var/lib/docker/volumes/asa-server_server-files-1/_data/ShooterGame/Saved/Config/WindowsServer`. The `Game.ini` file is not there by default, so you might want to create it yourself.

You don't need to worry about file permissions. The `docker-compose.yml` is running a container before starting the ASA server and adjusts the file permissions to `25000:25000`, which is the user id and group id the server starts with. These ids are not bound to any user on your system and that's fine and not an issue.

### 6. Changing the start parameters AND the player limit

Start parameters are defined in the `docker-compose.yml`:

```yml
...
    environment:
      - ASA_START_PARAMS=TheIsland_WP?listen?Port=7777?RCONPort=27020?RCONEnabled=True -WinLiveMaxPlayers=50
...
```

Please note:
* The value before `?listen` is the name of the map the server launches with.
* Please do not remove `?listen` from the parameters, otherwise the server is not binding ports
* `?Port=` is the server port players connect to
* `?RCONPort=` is the port of the RCON server that allows remote administration of the server
* The player limit is set by `-WinLiveMaxPlayers`. Please note that for ASA servers, editing the player limit via `GameUserSettings.ini` is not working.

## Port forwarding?

There should not be the need to forward any ports if your server runs in a public cloud. This is because docker configures `iptables` by itself. In a home setup, where a router is in between, it is very likely that you need to forward ports.

In any case, you ONLY need to forward the following ports:

```
7777 (UDP only - This is the game port to allow players to connect to the server)
27020 (TCP only - This is the port to connect through RCON and is therefore optional to forward)
```

As of today, ASA does no longer offer a way to query the server, so there's no query port and you won't be able to find your server through the Steam server browser, only via the ingame browser.

## Changing the game port and RCON port

You already learned that ports are defined by `ASA_START_PARAMS` in the `docker-compose.yml` file. This just tells the ASA server what ports to bind, but this alone is not enough and you need to apply
the following changes as well.

Open the `docker-compose.yml` file again and edit the lines where the container ports are defined:

```yml
...
    ports:
      # Game port for player connections through the server browser
      - 0.0.0.0:7777:7777/udp
      # RCON port for remote server administration
      - 0.0.0.0:27020:27020/tcp
...
```

Adjust the port to your liking, but make sure that you change both numbers (the one before and after the `:`). e.g. if you want to change the game port to `7755`, then this would be the result:

```yml
...
    ports:
      # Game port for player connections through the server browser
      - 0.0.0.0:7755:7755/udp
      # RCON port for remote server administration
      - 0.0.0.0:27020:27020/tcp
...
```

## Start/Restart/Stop

To perform any of the actions, execute the following commands (you need to be in the directory of the `docker-compose.yml` file):

```
docker-compose start asa-server-1
docker-compose restart asa-server-1
docker-compose stop asa-server-1
```

You can also use the native docker commands, where you do not need to be in the directory of the `docker-compose.yml` file. However using this method would not check for changes in your `docker-compose.yml` file.
So in case you edited the `docker-compose.yml` file (e.g. because you adjusted the start parameters), you need to use `docker-compose` commands instead.
```
docker start/restart/stop asa-server-1
```

## Setting up a second server

Setting up a second server is quite easy and you can easily add more if you want (given that your hardware is capable of running multiple instances). There's already a definition for a second server in the `docker-compose.yml` file,
but the definition is commented out by a leading `#`. If you remove these `#`, and run `docker-compose up -d` again, then the second server should start and it will listen on the game port `7778` and the query port `27021`. Please note that
the server files, as well as Steam, and steamcmd will be downloaded again and the first start can take a while.

You can edit the start parameters in the same way like for the first server and the files of the second server are located at the same location, except that the second server has its suffix changed from `-1` to `-2`. The directories will therefore,
named like this:

```
asa-server_server-files-2/
asa-server_steam-2/
asa-server_steamcmd-2/
```

That's it! Your second server is now running.

If you want to spin up more servers, you need to add more entries to the `docker-compose.yml` file. The following sections need to be edited: `services` and `volumes`. Make sure that you adjust all suffixes and replace them with a new one
(e.g. `-3` now) for the newly added entries.

## Found an Issue or Bug?

Create a ticket on GitHub, I will do my best to fix it. Feel free to open a pull request as well.

## Credits

* Glorius Eggroll - For his version of Proton to run the ARK Windows binaries on Linux ([click](https://github.com/GloriousEggroll/proton-ge-custom))
* cdp1337 - For his Linux guide of installing Proton and running ARK on Linux ([click](https://github.com/cdp1337/ARKSurvivalAscended-Linux))

