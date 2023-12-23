#!/bin/bash

function install_package {
    local package_name="$1"
    local install_command="$2"

    if command -v "$package_name" &>/dev/null; then
        echo "[$package_name]: found successfully."
    else
        echo "[$package_name]: installing.."
        eval "$install_command"
        echo "Installation of $package_name complete."
    fi
}

function install_library {
    for library in "$@"; do
        if ! pip3 show "$library" &>/dev/null; then
            echo "[$library]: installing.."
            pip3 install "$library"
            echo "Installation of $library complete."
        else
            echo "[$library]: found successfully."
        fi
    done
}

libraries=("configparser" "psutil" "telethon" "aiohttp" "aiofiles" "prettytable" "PyYAML" "googletrans" "pyfiglet")

install_package "python3" "sudo apt update && sudo apt install -y python3"
install_package "pip3" "sudo apt install -y python3-pip"
install_library "${libraries[@]}"

echo "[Setup]: successfully."