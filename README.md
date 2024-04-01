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
* [Server Administration](#server-administration)
  * [Debug Mode](#debug-mode)
  * [Applying server updates](#applying-server-updates)
  * [Daily restarts](#daily-restarts)
  * [Executing RCON commands](#executing-rcon-commands)
* [Setting up a second server](#setting-up-a-second-server)
* [Adding Mods](#adding-mods)
  * [Adding Mod Maps](#adding-mod-maps)
* [Common Issues](#common-issues)
  * [Server is not visible in server browser](#server-is-not-visible-in-server-browser)
* [Addressing "Connection Timeout" issues](#addressing-connection-timeout-issues)
  * [Your server has multiple IPv4 addresses](#your-server-has-multiple-ipv4-addresses)
    * [Debugging with curl](#debugging-with-curl)
    * [How to customize your routing?](#how-to-customize-your-routing)
    * [Making your iptable rules persistent](#making-your-iptable-rules-persistent)
* [Found an Issue or Bug?](#found-an-issue-or-bug)
* [Credits](#credits)

## Hardware Requirements

The hardware requirements might change over time, but as of today you can expect:

* ~11 GB RAM usage per server instance
* ~6.2 GB disk space (the server files alone, without any savegames)

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
asa-server_cluster-shared/
asa-server_server-files-1/
asa-server_steam-1/
asa-server_steamcmd-1/
```

The prefix `asa-server` is defined by the directory name of your `docker-compose.yml` file.

You can ignore `asa-server_steam-1` and `asa-server_steamcmd-1`, these volumes are being used by the container to avoid setting up `Steam` and `steamcmd` on every launch again. Server files including config files are stored at `asa-server_server-files-1`. `asa-server_cluster-shared` provides support for server clusters, so that survivors can travel between your servers with their characters and dinos.

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

## Server Administration

### Debug Mode

Sometimes you want to test something inside the container without starting the ASA server. The debug mode can be enabled by changing `- ENABLE_DEBUG=0` to `1` in the `docker-compose.yml` file.
Once done, the result will look like this:

```yml
...
version: "3.3"
services:
  asa-server-1:
    container_name: asa-server-1
    hostname: asa-server-1
    entrypoint: "/usr/bin/start_server"
    user: gameserver
    image: "mschnitzer/asa-linux-server:latest"
    environment:
      - ASA_START_PARAMS=TheIsland_WP?listen?Port=7777?RCONPort=27020?RCONEnabled=True -WinLiveMaxPlayers=50
      - ENABLE_DEBUG=1
...
```

Now run `docker-compose up -d` and the container will just start without launching the server or validating server files.

Check if the container launched in debug mode by running `docker logs -f asa-server-1` and check whether it's saying "Entering debug mode...". If that's the case, you are good.

You can enter the shell of your server by running

```
docker exec -ti asa-server-1 bash
```

If you need root access run

```
docker exec -ti -u root asa-server-1 bash
```

### Applying server updates

Updates will be automatically downloaded or applied once you restart the container with ...

```
docker restart asa-server-1
```

It is totally possible that after a restart and applying all updates, the client is still one or more versions ahead. This is because Wildcard does sometimes run client-only updates, since not all
updates are affecting the server software. This is not a problem at all. As long as you can connect to your server, everything is fine. The server software checks for incompatible client
versions anyway.

In general you can check when the latest server update was published by Wildcard, by checking [this link](https://steamdb.info/app/2430930/depots/). The section mentioning the last update of the `public` branch
tells you when the last update was rolled out for the server software.

If you have any doubts on this, open a GitHub issue.

### Daily restarts

As `root` user of your server (or any other user that is member of the `docker` group) open your crontab configuration:

```
crontab -e
```

Add the following lines to it:
```
30 3 * * * docker exec asa-server-1 asa-ctrl rcon --exec 'serverchat Server restart in 30 minutes'
50 3 * * * docker exec asa-server-1 asa-ctrl rcon --exec 'serverchat Server restart in 10 minutes'
57 3 * * * docker exec asa-server-1 asa-ctrl rcon --exec 'serverchat Server restart in 3 minutes'
58 3 * * * docker exec asa-server-1 asa-ctrl rcon --exec 'saveworld'
0 4 * * * docker restart asa-server-1
```

Explanation:
* Line 1: Every day at 03:30am of your server's timezone, a message will be sent to all players announcing a restart in 30 minutes.
* Line 2: Every day at 03:50am of your server's timezone, a message will be sent to all players announcing a restart in 10 minutes.
* Line 3: Every day at 03:57am of your server's timezone, a message will be sent to all players announcing a restart in 3 minutes.
* Line 4: Every day at 03:58am of your server's timezone, the server saves the world before the restart happens.
* Line 5: Every day at 04:00am of your server's timezone, the ASA server gets restarted and installs pending updates from Steam.

Read more about the crontab syntax [here](https://www.adminschoice.com/crontab-quick-reference).

**NOTE:** The first 4 lines execute RCON commands, which requires you to have a working RCON setup. Please follow the instructions in section "[Executing RCON commands](#executing-rcon-commands)" to
ensure you can execute RCON commands.

### Executing RCON commands

You can run RCON commands by accessing the `rcon` subcommand of the `asa-ctrl` tool which is shipped with the container image. There's no need to enter your server password, IP, or RCON port manually. As long as
you have set your RCON password and port, either as a start parameter or in the `GameUserSettings.ini` file of your server, `asa-ctrl` is able to figure those details out by itself.

The following variables need to be present either as start parameter or in `GameUserSettings.ini` under the `[ServerSettings]` section:

```
RCONEnabled=True
ServerAdminPassword=mysecretpass
RCONPort=27020
```

Example:

```
docker exec -t asa-server-1 asa-ctrl rcon --exec 'saveworld'
```

**NOTE:** As opposed to ingame cheat commands, you must not put `admincheat` or `cheat` in front of the command.

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

## Adding Mods

Mods can be added by adjusting the `docker-compose.yml` file and adding a `-mods` option to the start parameters.

e.g.

```
[...]
- ASA_START_PARAMS=TheIsland_WP?listen?Port=7777?RCONPort=27020?RCONEnabled=True -WinLiveMaxPlayers=50 -mods=12345,67891
[...]
```

Once done, restart the server using `docker-compose up -d`. It might take longer until the server comes up, because the server has to download the mods first.

Mod IDs are usually somewhere listed on the mod page of a mod on curseforge.com.

### Adding Mod Maps

Search for a map on curseforge.com and find out what mod id the map has and what the map name is. For the map [Svartalfheim](https://www.curseforge.com/ark-survival-ascended/mods/svartalfheim) the map name
is `Svartalfheim_WP` and the mod id is `893657`.

Once you found out the information you need, you need to adjust your start parameters in the `docker-compose.yml` file and add the map name, as well as the `-mods` option.

e.g.

```
[...]
- ASA_START_PARAMS=Svartalfheim_WP?listen?Port=7777?RCONPort=27020?RCONEnabled=True -WinLiveMaxPlayers=50 -mods=893657
[...]
```

Restart your server using `docker-compose up -d`. It may take a while, as the server has to download the map, so be patient.

## Common Issues

### Server is not visible in server browser

If you cannot discover your server in the server browser, it's most likely due to at least one of the following reasons:

* Your server is still booting up, give it ~5 minutes
* You are not looking at the "Unofficial" server browser list
* Your filter settings in the server browser exclude your server
* You forgot clicking the "Show player server settings". ([view screenshot](https://raw.githubusercontent.com/mschnitzer/ark-survival-ascended-linux-container-image/dev/assets/show-player-servers.jpg)) By default, only Nitrado servers are shown to players when searching for unofficial servers, unfortunately.

## Addressing "Connection Timeout" issues

First of all, try to connect through the ingame console to your server. In many cases this works, but only connecting through the server browser causes an issue. Try to run the command `open $IP:$PORT` and test whether you
can connect to it.

If that is NOT working and you are having a home setup and not a VPS cloud setup, make sure your ports are REALLY open. This needs to be configured on your router. The ports that need to be opened are listed above in this README.
Please refer to the documentation of your router how to configure port forwarding properly.

If you can connect to your server through the console command, but not via the sever browser, it is very likely that you are running into one of these issues:

### Your server has multiple IPv4 addresses

If your server has multiple IPv4 addresses and you bound your ASA server to one of the secondary ones, by default, docker routes your traffic always through your primary network interface, which would cause the server browser to list your
server under the wrong IP address.

For example:

Your primary IP is: `255.255.300.300`
Your secondary one is: `255.255.400.400`

You adjusted the `docker-compose.yml` file in a way where it binds the ports on interface `255.255.400.400`. However, if your ASA server communicates with the internet and announces itself to the ASA server list, the ASA master server that manages the
server browser entries, would see the requests coming from `255.255.300.300` as this is your primary network interface.

This issue can be solved by forcing the traffic to be routed manually through your secondary network interface.

But before we start fixing it, you should make sure that this is really the issue.

#### Debugging with curl

1. Log in to the container `docker exec -ti -u root asa-server-1 bash`
2. Run `zypper --no-gpg-checks ref`
3. Install curl `zypper in -y curl`
4. Run `curl icanhazip.com` (`icanhazip.com` is a service that tells you from what ip address it received traffic from)

If the service responds with an IP that you have not assigned to the ASA server in the `docker-compose.yml` file, then it's very likely that this is the reason why you are getting a "Connection Timeout" error.
Please continue following the instructions below.

#### How to customize your routing?

You need to adjust the `docker-compose.yml` file and add `com.docker.network.bridge.enable_ip_masquerade: 'false'` to the `networks` section, so that it looks like this:

```yml
networks:
  asa-network:
    attachable: true
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: 'asanet'
      com.docker.network.bridge.enable_ip_masquerade: 'false'
```

Now stop the ASA server if it's running:

```
docker stop asa-server-1
```

Delete the docker network interface and the container, so that they can be recreated:

```
docker rm asa-server-1
docker network rm asa-server_asa-network
```

Now run `docker-compose up -d` from within the directory where your `docker-compose.yml` is located at.

Once done and the container is up again, inspect the network to find its subnet:

```
docker network inspect asa-server_asa-network | grep Subnet
```

Now customize the routing of the container through `iptables`, where `$SUBNET` needs to be replaced with the subnet from the previous command (including the `/24` or `/16` - whatever it is in your case):

```
iptables -t nat -A POSTROUTING -s $SUBNET ! -o asanet -j SNAT --to-source $YOUR_SECONDARY_IP_USED_BY_ASA
```

Once done, connect to your container and test that the remote IP is the right one, by following the steps with `curl` again.

Now try to connect to your server through the server browser. If that is not solving your problem or if the IP is still the wrong one, open a GitHub issue. If it solves your problem, continue with the
next section to make the `iptables` adjustments persistent after reboot.

#### Making your iptable rules persistent

Changes to the `iptables` will get reverted after reboot. You can make them persistent by saving the current state:

```
iptables-save > /root/iptables
```

Now run `crontab -e` and add the following entry:

```
@reboot /bin/bash -c 'sleep 15 ; /usr/sbin/iptables-restore < /root/iptables'
```

Save the cronjob and test it by rebooting your system. You can test whether it has worked by following the `curl` steps from above again.

## Found an Issue or Bug?

Create a ticket on GitHub, I will do my best to fix it. Feel free to open a pull request as well.

## Credits

* Glorius Eggroll - For his version of Proton to run the ARK Windows binaries on Linux ([click](https://github.com/GloriousEggroll/proton-ge-custom))
* cdp1337 - For his Linux guide of installing Proton and running ARK on Linux ([click](https://github.com/cdp1337/ARKSurvivalAscended-Linux))
* tesfabpel - For his Valve RCON implementation in Ruby ([click](https://github.com/tesfabpel/srcon-rb))
