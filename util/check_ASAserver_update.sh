#!/bin/bash
##
## Checks for available ASA server updates
##
STEAM_CMD="./steamcmd/steamcmd.sh +@ShutdownOnFailedCommand 1 +@NoPromptForPassword 1 +login anonymous +app_info_print 2430930 +quit"

function show_help() {
    cat <<EOF
Usage: $0 [OPTIONS]

Options:
    -g, --grace-period <arg>   Defines the grace period after which the server restart happens
                               Immediate restart without online players
                               Syntax follows syntax of "sleep" command
    -s, --server <arg>         Specifices the ASA server container
    -h, --help                 Show this help message and exit
EOF
}

function determine_current_version(){
    # current version
    CURRENT_VERSION=$(docker exec -t ${1} bash -c "grep buildid ./server-files/steamapps/appmanifest_2430930.acf | cut -d'\"' -f4 | xargs")
    if [[ -z "${CURRENT_VERSION}" ]]
    then
	echo "Current version could not be determined!"
	exit 1
    fi
    echo "Installed ASA server (2430930) buildid: ${CURRENT_VERSION}"
}

function determine_upstream_version(){
    # upstream version
    UPSTREAM_VERSION=$(docker exec -t ${1} bash -c "${STEAM_CMD} | grep -A 3 '\"public\"' | grep buildid | cut -d'\"' -f4 | xargs")
    if [[ -z "${UPSTREAM_VERSION}" ]]
    then
	echo "Upstream version could not be determined!"
	exit 1
    fi
    echo "Available ASA server (2430930) buildid: ${UPSTREAM_VERSION}"

}

function compare_versions(){
    # comparison $1 -> CURRENT_VERSION, $2 -> UPSTREAM_VERSION
    if [[ "${1}" == "${2}" ]]
    then
	echo "Installed ASA server (2430930) is current!"
        exit 0
    else
	echo "ASA server (2430930) update available!"
    fi
}

function update(){
    # check upon online players
    # $1 -> SERVER $2 -> PERIOD
    if [[ $(docker exec -t ${1} bash -c "asa-ctrl rcon --exec 'listplayers'" | xargs) == "No Players Connected" ]]
    then
	echo "Restarting server ${1} immediately without online players..."
	docker restart ${1}
    else
	echo "Initiated restart in ${2} due to online players..."
	docker exec -t ${1} bash -c "asa-ctrl rcon --exec 'serverchat Server is restarting in ${2} due to updates...'"
	sleep ${2}
	echo "Restarting server ${1} now (after grace period)..."
	docker exec -t ${1} bash -c "asa-ctrl rcon --exec 'serverchat Server is restarting NOW due to updates...'"
	docker restart ${1}
    fi
}


while [[ $# -gt 0 ]]; do
    case "$1" in
        -g|--grace-period)
            PERIOD="$2"
            shift 2
            ;;
        -s|--server)
            SERVER="$2"
            shift 2
            ;;
        -h|--help)
            help=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [[ "$help" = true ]]; then
    show_help
    exit 0
fi
determine_current_version ${SERVER}
determine_upstream_version ${SERVER}
compare_versions ${CURRENT_VERSION} ${UPSTREAM_VERSION}
update ${SERVER} ${PERIOD}
