# ARK: Survival Ascended - Dedicated Linux Server - Docker Image

This repository provides a step by step guide for Linux administrators to host ARK: Survival Ascended servers on Linux using a docker image.

## Installation

In theory, you can use these steps on any Linux system where Docker is installed.

### 1. Install Docker & Docker Compose

Debian/Ubuntu:

```
sudo apt-get install -y docker-ce docker-ce-cli docker-compose-plugin
```

openSUSE:
```
zypper in docker docker-compose
```

### 2. Start docker daemon

```
systemctl start docker
systemctl enable docker
```

### 3. Pull the docker image

```
docker pull mschnitzer/asa-linux-server
```

### 4. Create the Docker Compose config

Now create a directory at the location of your choice and create a file called `docker-compose.yml`. In that file, copy the contents of [my docker-compose.yml](invalid) example.

### 5. First server start

Now start the server for the first time. It will install Steam, Proton, and downloads the ARK: Survival Ascended server files.

Go to the directory of your `docker-compose.yml` file and execute the following command:

```
docker-compose up -d
```

It will start a container called `asa-server` (defined in `docker-compose.yml`). You can follow the installation and the start of your server by running:

```
docker logs -f asa-server
```

(Note: You can safely run `CTRL + C` to exit the log window again without causing the server to stop)

Once the log shows the following line:

```
Starting the ARK: Survival Ascended dedicated server now...
```

In some minutes, the server should be reachable and discoverable through the server browser. Usually for me it didn't take more than 2 minutes (maximum). You can try to connect to it by opening the console in ARK: Survival Ascended and enter `open your_server_ip`.

Once you confirmed you can connect to it, please run the following command to stop the server:

```
docker-compose stop server
```

### 6. Server configuration

The `docker-compose.yml` config defines three docker volumes. They should be created at `/var/lib/docker/volumes`. They are named by the directory name of where your `docker-compose.yml` is located at and then followed by the following names `_server-files`, `_steam`, `_steamcmd`.

Since my `docker-compose.yml` file is in a directory called `asa-server`, for me the volume names are:

```
asa-server_server-files/
asa-server_steam/
asa-server_steamcmd/
```

You can ignore `asa-server_steam` and `asa-server_steamcmd`. All server files including all config files, are located at `asa-server_server-files`.

The `GameUserSettings.ini` and `Game.ini` file can be found at `/var/lib/docker/volumes/asa-server_server-files/_data/ShooterGame/Saved/Config/WindowsServer`. The `Game.ini` file is not there by default, so you might want to create it yourself. However I noticed it gets created over time (probably once a player connects for the first time).

Do any adjustments you like.

PS: You don't need to worry about file permissions. The `docker-compose.yml` is running a container before starting the ARK server container to adjust the file permissions to `25000:25000` which is the user id and group id the server launches from within the container.

### 7. Changing the start parameters AND the player limit

The start parameters can be configured by editing the file `/var/lib/docker/volumes/asa-server_server-files/_data/start-parameters`. By default the server launches with a player limit of 35. You can change that by adjusting `-WinLiveMaxPlayers` to the number you like. There's an example in the `start-parameters` file that the startup script from me generates.

**IMPORTANT**: This file is evaluated by the start script. Do NOT put any line breaks in that file, otherwise the server will not be able to launch.

## Port forwarding?

On a cloud server there should not be any port forwarding needed. This is because docker configures `iptable` itself. In a home setup where a route is in between, it is very likely that you need to forward ports.

In any case, you ONLY need to forward the following ports:

```
7777 (UDP only - This is the game port to allow players to connect to the server)
27020 (TCP only - This is the port to connect through RCON and is therefore optional to forward)
```

As of today, there's no query, so you won't be able to discover the server through Steam's server list. That was different for ARK: Survival Evolved.

## Start/Restart/Stop

To perform any of the actions, execute the following commands (you need to be in the directory of the `docker-compose.yml` file):

```
docker-compose start server
docker-compose restart server
docker-compose stop server
```

You could also use the native docker commands, but this time you need to use the container name `asa-server`:
```
docker start/restart/stop asa-server
```

## Found an Issue or Bug?

Create a ticket on GitHub, I will do my best to fix it. Feel free to open a pull request as well.

## Credits

* Glorius Eggroll - For his version of Proton to run the ARK Windows binaries on Linux ([click](https://github.com/GloriousEggroll/proton-ge-custom))
* cdp1337 - For his Linux guide of installing Proton and running ARK on Linux ([click](https://github.com/cdp1337/ARKSurvivalAscended-Linux))

