# HayesUB - Userbot Installation Guide

HayesUB is a userbot for Telegram, designed to provide additional functionality and automation features. Follow the steps below to install, configure, and set up HayesUB on your machine.

## Prerequisites

Make sure you have the following prerequisites installed on your system:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) [3.7+]

### For Termux:

- [Termux](https://termux.com/)


## Installation Steps

1. Clone the HayesUB repository to your local machine:

    ```bash
    git clone https://github.com/reslaid/hayesUB.git 
    ```
    ```bash
    cd hayesUB
    ```

2. **For Windows:**

    Run the setup script:

    ```bash
    setup.bat
    ```
    
3. **For Linux:**

    Run the setup script:

    ```bash
    ./setup.sh
    ```

    This script will install the necessary dependencies.

4. **For Termux:**

    ```bash
    pkg install -y libffi openssl libexpat python clang make openssl-dev rust
    ```
    ```bash
    pip3 install telethon psutil aiohttp aiofiles prettytable PyYAML openai googletrans pyfiglet
    ```
    
5. Wait for the dependencies to be installed. Once the installation is complete, you're ready to configure HayesUB.

## Configuring HayesUB

-    **First way**
1. Open the `config.cfg` file with any editor convenient for you

2. Change the following parameters according to your Telegram account:
    - `api_id`: Your Telegram API ID (get it from [my.telegram.org](https://my.telegram.org/))
    - `api_hash`: Your Telegram API Hash (get it from [my.telegram.org](https://my.telegram.org/))
    - `api_token`: Your Telegram API Token (get it from [BotFather](https://core.telegram.org/bots#botfather))
    - `admin_id`: Your Telegram User ID (get it from [GetMyIdBot](https://t.me/getmyid_bot))

-    **Second way**
1. Use auth module

**For Windows:**
   
   ```bash
   python -m auth
   ```

**For Liunx/Termux:**
   
   ```bash
   python3 -m auth
   ```

## Getting Your Telegram User ID

To get your Telegram User ID, follow these steps:

1. Start a chat with [GetMyIdBot](https://t.me/getmyid_bot) on Telegram.

2. Click on the "Start" button.

3. The bot will provide you with your User ID.

Now that you've configured HayesUB and obtained your Telegram User ID, you're ready to run the userbot.

## Running HayesUB

Before running HayesUB, make sure to navigate to the installation directory:

```bash
cd path\to\hayesUB
```

Now, you can run HayesUB:

- **For Windows:**

    ```bash
    python -m run
    ```

- **For Linux/Termux:**

    ```bash
    python3 -m run
    ```

## Updating HayesUB

To update HayesUB to the latest version, use the following commands:

Before updating, navigate to the installation directory:

```bash
cd path\to\hayesUB
```

To check for updates, run the following command:

- **For Windows:**

    ```bash
    python -m update --check
    ```

- **For Linux/Termux:**

    ```bash
    python3 -m update --check
    ```

Then, run the update command:

- **For Windows:**

    ```bash
    python -m update
    ```

- **For Linux/Termux:**

    ```bash
    python3 -m update
    ```
     
Now, HayesUB should be up and running on your machine. You can explore the additional functionality provided by the userbot.

Feel free to check out the [HayesUB GitHub repository](https://github.com/reslaid/hayesUB) for more details and updates.
