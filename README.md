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


# Installation and Upgrade


The following packages will install two commands:

- `qk`
- `quikey-daemon`

Everything can be managed using just `qk` and examples are [further below](#usage).


## Python 3
```shell
$ pip3 install --user quikey 
$ pip3 install --user -U quikey #<-- Upgrade
```
or 
```shell
$ python3 -m pip install --user quikey
$ python3 -m pip install --user -U quikey #<-- Upgrade
```

## Arch Linux (AUR)
```shell
$ curl -L -O https://aur.archlinux.org/cgit/aur.git/snapshot/quikey.tar.gz && tar -xvf quikey.tar.gz && cd quikey && makepkg -si
```

## Fedora (Copr)
```shell
$ dnf copr enable bostrt/quikey # Enable repo
$ dnf install quikey            # Install pkg
$ dnf update quikey             # Update pkg
```

## Ubuntu, Debian, MXLinux, Mint, etc (PPA)
```shell
coming soon
```

# Usage

## Managing the daemon
There is a daemon process that must be running for Quikey's macro functionality to run. You can manage the daemon from the `qk` client:

### Start daemon
```shell
$ qk start
```

### Autostart on Login
```shell
$ qk autostart enable
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

### Interactive editing
Use interactive menus to edit and remove phrases:
```
$ qk edit
$ qk rm
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
