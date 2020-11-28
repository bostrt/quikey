#!/usr/bin/env python

import click
from terminaltables import AsciiTable
import humanize
import signal
import os
import logging

from quikey.models import Database
from quikey.directories import AppDirectories
from quikey.version import __version__
from quikey.autostart import enableAutostart, disableAutostart
from quikey.importer import PhraseFind
from quikey import prompt
from xdg import BaseDirectory
import subprocess

MARKER = '''
# Everything below this line will be ignored.
# Insert your quikey phrase into this file then save and close.
'''

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_database():
    appDirs = AppDirectories() # XDG folders
    d = Database(appDirs)
    return d

@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    """A keyboard macro tool.
    
    Features, Feedback, and Bugs: https://github.com/bostrt/quikey
    """
    ctx.obj = {'database': get_database()}
    
@cli.command(help='Add a new phrase')
@click.option('--name' ,'-n', required=True, help='Name of quikey phrase to add.')
@click.option('--tag', '-t', multiple=True, help='Optional tags for the phrase. You can specify this option multiple times.')
@click.option('--phrase', '-p', help='The full phrase to add. If this option is not specified then your default editor ($EDITOR) will be used.')
@click.pass_context
def add(ctx,name,phrase,tag):
    db = ctx.obj['database']
    if not name or not name.strip():
        click.echo('quikey phrase cannot be empty')
        return

    contents = None
    if db.get(name) is not None:
        click.echo('quikey phrase with key of %s already exists' % name)
        return
    if phrase is not None:
        contents = phrase
    else:
        contents = click.edit(MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0]
        else:
            click.echo('quikey phrase with key of %s not added' % name)
            return
    db.put(name, contents, tag)
    click.echo('quikey phrase with key of %s added.' % name)

@cli.command(help='Edit an existing phrase')
@click.option('--name', '-n', help='Name of quikey phrase to edit.')
@click.pass_context
def edit(ctx,name):
    db = ctx.obj['database']
    if name is None:
        # Show user prompt with list of keys
        name = prompt.show(db, "edit")
        if name is None:
            click.echo('No phrases available to edit. Use "qk add" to create a new one.')
            return

    phrase = db.get(name)
    if phrase is not None:
        contents = click.edit(phrase + MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0]
            db.update(name, contents)
            click.echo('quikey phrase with key of %s updated.' % name)
        else:
            click.echo('quikey phrase with key of %s not updated' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
        

@cli.command(help='Remove a phrase')
@click.option('--name', '-n', help='Name of quikey phrase to remove.')
@click.pass_context
def rm(ctx,name):
    db = ctx.obj['database']
    # TODO: Support multiple.
    if name is None:
        # Show user prompt with list of keys
        name = prompt.show(db, "remove")
        if name is None:
            click.echo('No phrases available to remove.')
            return

    if db.delete(name):
        click.echo('quikey phrase with key of %s has been deleted.' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
    
@cli.command(help='List all phrases')
@click.option('--show-all', is_flag=True, help='Show the entire quikey phrase instead of a shortened version '
                                               'for long quikey phrases.')
@click.pass_context
def ls(ctx, show_all):
    db = ctx.obj['database']
    table = [['Name', 'Tags', 'Last Modified', 'Phrase']]
    phrases = db.all()
    for phrase in phrases:
        tags = ', '.join([x for x in phrase.get('tags')])
        v = phrase.get('value')
        value = (v[:40] + '...' if len(v) > 40  and not show_all else v)
        table.append([phrase.get('key'), tags, humanize.naturalday(phrase.get('updated')), value])
    output = AsciiTable(table)
    click.echo(output.table)

@cli.command(help='Import from AutoKey')
@click.option('--location', '-l', default=BaseDirectory.xdg_config_home+"/autokey/data/", show_default=True, help='Location of top level directory to import from autokey')
@click.pass_context
def keyimport(ctx,location):
    tags = ['autokey-imports']
    db = ctx.obj['database']
    importfiles = PhraseFind(location)
    for key in importfiles:
        contents = None
        if importfiles[key] is not None:
            if db.get(key) is not None:
                click.echo('quikey phrase with key of %s already exists' % key)
                continue
            else:
                contents = importfiles[key]
        else:
            if db.get(key) is not None:
                click.echo('quikey phrase with key of %s already exists' % key)
                continue
            else:
                contents = click.edit('\n\n'+MARKER)
                if contents is not None:
                    contents = contents.split(MARKER, 1)[0]
                else:
                    click.echo('quikey phrase with key of %s not added' % key)
                    continue
        db.put(key, contents, tags)
        click.echo('quikey phrase with key of %s added.' % key)

@cli.command(help='Display version')
def version():
    click.echo("quikey %s" % __version__)

@cli.group(help='Configure autostart of quikey')
def autostart():
    pass

@autostart.command()
def enable():
    "Enable autostart at login for quikey."
    enableAutostart()

@autostart.command()
def disable():
    "Disable autostart at login for quikey."
    disableAutostart()

@cli.command(help='Display status of quikey daemon')
@click.pass_context
def status(ctx):
    subprocess.run(['quikey-daemon', 'status'])
    click.echo("Database location: " + ctx.obj['database'].dbFile)

@cli.command(help='Start quikey daemon')
def start():
    subprocess.run(['quikey-daemon', 'start'])

@cli.command(help='Stop quikey daemon')
def stop():
    subprocess.run(['quikey-daemon', 'stop'])
