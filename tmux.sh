#!/data/data/com.termux/files/usr/bin/bash

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

eval "pkg update"

install_package "ffi" "pkg install -y libffi"
install_package "ssl" "pkg install -y opessl"
install_package "expat" "pkg install -y libexpat"
install_package "tsu" "pkg install -y tsu"
install_package "python" "pkg install -y python"
install_library "${libraries[@]}"

echo "[Setup]: successfully."
