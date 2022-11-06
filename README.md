## What's this?
Automatically fxxk the health report of NEU.

## How to use?
### Use Github Actions
1. Fork or import (if you want it to be private) this repository.
2. Go to `Settings` -> `Secrets` -> `New repository secret`.
3. Add a secret named `USERNAME` and set your username as its value.
4. Add a secret named `PASSWORD` and set your password as its value.
5. [Optional] Add a secret named `IP` and set an IP as its value.  **This will no longer work after a recent server-side update.**
6. [Optional] If you want to bypass IP restriction, add a secret named `USE_WEBVPN` and set any non-empty value as its value.  **It's recommended to set it to something that's not likely to appear in logs.**
7. [Optional] If you don't want to be notified when the action fails, add a secret named `NO_ERROR` and set any non-empty value as its value. **It's recommended to set it to something that's not likely to appear in logs.**
8. [Not recommended] If you want to see more details, add a secret named `DEBUG` and set any non-empty value as its value. **Note that this might expose your personal information if used in a public repo.**
9. Go to `Actions` -> `I understand my workflows, go ahead and enable them`.
10. Wait for the action to be triggered.  **It will be triggered every day at 7:10 AM.** You can also manually trigger it by making a commit, for example, by editing this file.

### Manually
1. Install Python 3.10 or above.
2. Clone this repo.
3. [Optional but recommended] Create a virtual environment and activate it. `python -m venv venv` and `source venv/bin/activate`.
4. Install dependencies. `pip install -r requirements.txt`.
5. Run `python main.py [parameters]`. Remember to replace `[parameters]` with your parameters. For details about parameters, see `python main.py -h` or the following section.

### Parameters
```plaintext
usage: main.py [-h] [-i IP] [--no-error] [--use-webvpn] [--debug] userid password

positional arguments:
  userid          user id
  password        password

options:
  -h, --help      show this help message and exit
  -i IP, --ip IP  ip address for 'X-Forwarded-For' header
  --no-error      If true, print error message and exit with code 0 when error occurs. If you don't want to be disturbed by Github's email, set it to True.
  --use-webvpn    If true, will use webvpn to bypass ip restriction.
  --debug         If true, will print debug message. Don't use it in public repository.
```


