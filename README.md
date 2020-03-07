# Quikey [![PyPI version](https://badge.fury.io/py/quikey.svg)](https://badge.fury.io/py/quikey)

A keyboard macro tool.

----
* [Installation](#installation)
  * [Python 3](#python-3)
  * [Arch Linux (AUR)](#arch-linux-aur)
  * [Fedora (Copr)](#fedora-copr)
  * [Ubuntu, Debian, MXLinux, Mint, etc](#ubuntu-debian-mxlinux-mint-etc-ppa)
* [Usage](#usage)
  * [Quickstart](#quickstart)
  * [Managing the daemon](#managing-the-daemon)
  * [Managing phrase entries](#managing-phrase-entries)


# Installation

## Python 3
```shell
$ pip3 install --user quikey
```
or 
```shell
$ python3 -m pip install --user quikey
```

## Arch Linux (AUR)
```shell
$ curl -L -O https://aur.archlinux.org/cgit/aur.git/snapshot/quikey.tar.gz && tar -xvf quikey.tar.gz && cd quikey && makepkg -si
```

## Fedora (Copr)
```shell
$ dnf copr enable bostrt/quikey # Enable repo
$ dnf install quikey            # Install pkg
```

## Ubuntu, Debian, MXLinux, Mint, etc (PPA)
```shell
coming soon
```

The packages above install two executables:
- `qk`
- `quikey-daemon`

Everything can be managed using just `qk` and examples are below.

# Usage

## Quickstart



## Managing the daemon
There is a daemon process that must be running for Quikey's macro functionality to run. You can manage the daemon from the `qk` client:

#### Start daemon
```shell
$ qk start
```

### Stop daemon
```shell
$ qk stop
```

## Managing phrase entries
### Adding a new phrase
```shell
$ qk add -n ':hello:' -p 'Hello, my name is John Doe.'
```

The `-p` flag is optional. If it is not included, your default editor (`$EDITOR`) will be used.

### Listing all phrases
```shell
$ qk ls 
+---------+------+----------------------------+-----------------------------+
| Name    | Tags | Last Modified              | Phrase                      |
+---------+------+----------------------------+-----------------------------+
| :hello: |      | 2019-02-24T05:21:48.245440 | Hello, my name is John Doe. |
+---------+------+----------------------------+-----------------------------+

```
### Editing a phrase
```shell
$ qk edit -n ':hello:'
```

This will drop into your default editor (`$EDITOR`) with the current phrase for the given name. 
### Removing a phrase
```shell
$ qk rm -n ':hello:'
quikey phrase with key of :hello: has been deleted.
```

## Development

See [DEVELOP.md](DEVELOP.md) for help.