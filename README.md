# Discord-Bot
Repository for my discord bot Oumae Kumiko </br>
Developed using Python 3.12 </br>
Uses [uv](https://docs.astral.sh/uv/getting-started/) for Python 
package management </br>
Guides for installing uv and adding Python versions to uv can be found 
[here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) and 
[here](https://docs.astral.sh/uv/guides/install-python/#installing-a-specific-version)
respectively </br>

# Adding Your Bot Token
In the **project root**, make a new file `Token.py` with the token.
```py
token='<your token here>'
```

# Running the Bot Locally
From the **project root**, run the following.
```bash
uv run -m Kumiko.main
```

# Running on fly.io (free tier)
First setup a fly.io account and input your credit card information. </br>
Then let your terminal log into your fly.io account. </br>
**NOTE:** If you exceed the free tier, you will be charged for it.

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
The destruction of one of the machines on fly.io is to prevent messages from 
being sent twice, as explained in 
[this thread](https://community.fly.io/t/how-to-only-have-one-machine-running-at-once/13914/2)



In loving memory of the file `its-so-beautiful-let-me-save-it.json`
