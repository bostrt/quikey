# Quikey [![PyPI version](https://badge.fury.io/py/quikey.svg)](https://badge.fury.io/py/quikey)

A keyboard macro tool.

# Installation
```
# pip3 install --user quikey
```
or 
```
# python3 -m pip install --user quikey
```

Package above installs two available executables:
- `qk`
- `quikey-daemon`

Basically everything can be managed using just `qk` and examples are below.

# Usage

## Managing the daemon
There is a daemon process that must be running for Quikey's macro functionality to run. You can manage the daemon from the `qk` client:

#### Start daemon
```
# qk start
```

### Stop daemon
```
# qk stop
```

## Managing phrase entries
### Adding a new phrase
```
# qk add -n ':hello:' -p 'Hello, my name is John Doe.'
```

The `-p` flag is optional. If it is not included, your default editor (`$EDITOR`) will be used.

### Listing all phrases
```
# qk ls 
+---------+------+----------------------------+-----------------------------+
| Name    | Tags | Last Modified              | Phrase                      |
+---------+------+----------------------------+-----------------------------+
| :hello: |      | 2019-02-24T05:21:48.245440 | Hello, my name is John Doe. |
+---------+------+----------------------------+-----------------------------+

```
### Editing a phrase
```
# qk edit -n ':hello:'
```

This will drop into your default editor (`$EDITOR`) with the current phrase for the given name. 
### Removing a phrase
```
# qk rm -n ':hello:'
quikey phrase with key of :hello: has been deleted.
```
