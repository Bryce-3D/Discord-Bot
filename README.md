# Discord-Bot
Repository for my discord bot Oumae Kumiko </br>
Requires at least **Python 3.10** to run properly due to the use of built in </br>
union type hinting (such as `int|None`) in some files.

# Installation
```bash
python3.12 -m venv venv
source venv/bin/activate
python3.12 -m pip install discord requests
```

# Adding of Token
From the **project root**, make a new file `Token.py` with one line in it.
```py
token='<your token here>'
```

# Running the Bot Locally
From the **project root**, run the following.
```bash
python3.12 -m Kumiko.main
```

# Running on fly.io (free tier)
First setup a fly.io account and input your credit card information. </br>
Then let your terminal log into your fly.io account.

From the **project root**, run the following
```bash
flyctl launch
#An existing fly.toml file was found for app oumae-kumiko-bot
#? Would you like to copy its configuration to the new app? Yes
#...
#? Do you want to tweak these settings before proceeding? No
#...
#Visit your newly deployed app at ...
fly m destroy one_of_the_two_machine_ids -a oumae-kumiko-bot --force
```
The destruction of one of the machines on fly.io is to prevent messages from being sent twice, </br>
as explained in [this thread](https://community.fly.io/t/how-to-only-have-one-machine-running-at-once/13914/2)


In loving memory of the file `its-so-beautiful-let-me-save-it.json`
