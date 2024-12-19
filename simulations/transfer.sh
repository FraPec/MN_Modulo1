#!/bin/bash

copy_remote_file() {
    local remote_user="$1"
    local remote_host="$2"
    local remote_path="$3"
    local local_path="$4"
    local is_directory="$5"

    if [[ -z $remote_user || -z $remote_host || -z $remote_path || -z $local_path ]]; then
        printf "Usage: copy_remote_file <remote_user>@<remote_host> <remote_path> <local_path> <is_directory>\n" >&2
        return 1
    fi

    local rsync_options="--progress --partial --append -e ssh"
    if [[ "$is_directory" == "yes" ]]; then
        rsync_options+=" -r"
    fi

    rsync $rsync_options "${remote_user}@${remote_host}:${remote_path}" "${local_path}"
}

main() {
    read -p "Enter remote user@host (e.g., user@host): " remote_user_host
    IFS='@' read -r remote_user remote_host <<< "$remote_user_host"
    read -p "Enter remote file path: " remote_path
    read -p "Enter local destination path: " local_path
    read -p "Is this a directory copy? (yes/no): " is_directory

    copy_remote_file "$remote_user" "$remote_host" "$remote_path" "$local_path" "$is_directory"
    if [ $? -eq 0 ]; then
        printf "File copied successfully.\n"
    else
        printf "Failed to copy the file.\n"
    fi
}

main