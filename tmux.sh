#!/data/data/com.termux/files/usr/bin/bash

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

install_library "${libraries[@]}"

echo "[Setup]: successfully."
