## Setting up a development environment

Quikey is written using Python 3.x, virtualenv, and setuptools. Ensure those prerequisites are available before proceeding. If anything more is needed or missing, please open up [an issue](https://github.com/bostrt/quikey/issues/new) and the team will be happy to help!.

### Clone and setup

1. Clone the repository
```
# git clone https://github.com/bostrt/quikey.git
# cd quikey
```
2. Setup Python 3.x virtual environment
```
# virtualenv v
# source v/bin/activate
# python --version
Python 3.7.3
```
3. Install dependencies and prepare scripts in development mode (`editable`)
```
# pip install --editable .
```
4. Make sure you can run `qk` script:
```
# qk
Usage: qk [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.
...
```
5. Finally, make your changes and [submit a PR!](https://github.com/bostrt/quikey/compare)