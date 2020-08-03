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
from xdg import BaseDirectory
import subprocess

MARKER = '''
# Everything after this line will be ignored.
# Insert your quikey phrase into this file then save and close.
'''

def get_database():
    appDirs = AppDirectories() # XDG folders
    d = Database(appDirs)
    return d

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {'database': get_database()}
    
@cli.command()
@click.option('--name' ,'-n', required=True, help='Name of quikey phrase to add.')
@click.option('--tag', '-t', multiple=True, help='Optional tags for the phrase. You can specify this option multiple times.')
@click.option('--phrase', '-p', help='The full phrase to add. If this option is not specified then your default editor ($EDITOR) will be used.')
@click.pass_context
def add(ctx,name,phrase,tag):
    db = ctx.obj['database']
    contents = None
    if db.get(name) is not None:
        click.echo('quikey phrase with key of %s already exists' % name)
        return
    if phrase is not None:
        contents = phrase
    else:
        contents = click.edit('\n\n'+MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0].rstrip('\n')
        else:
            click.echo('quikey phrase with key of %s not added' % name)
            return
    db.put(name, contents, tag)
    click.echo('quikey phrase with key of %s added.' % name)

@cli.command()
@click.option('--name', '-n', required=True, help='Name of quikey phrase to edit.')
@click.pass_context
def edit(ctx,name):
    db = ctx.obj['database']
    phrase = db.get(name)
    if phrase is not None:
        contents = click.edit(phrase + '\n\n' + MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0].rstrip('\n')
            db.update(name, contents)
            click.echo('quikey phrase with key of %s updated.' % name)
        else:
            click.echo('quikey phrase with key of %s not updated' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
        

@cli.command()
@click.option('--name', '-n', required=True, help='Name of quikey phrase to remove.')
@click.pass_context
def rm(ctx,name):
    db = ctx.obj['database']
    # TODO: Support multiple.
    if db.delete(name):
        click.echo('quikey phrase with key of %s has been deleted.' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
    
@cli.command()
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

@cli.command()
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
                    contents = contents.split(MARKER, 1)[0].rstrip('\n')
                else:
                    click.echo('quikey phrase with key of %s not added' % key)
                    continue
        db.put(key, contents, tags)
        click.echo('quikey phrase with key of %s added.' % key)

@cli.command()
def version():
    click.echo("quikey %s" % __version__)

@cli.group()
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

@cli.command()
@click.pass_context
def status(ctx):
    subprocess.run(['quikey-daemon', 'status'])
    click.echo("Database location: " + ctx.obj['database'].dbFile)

@cli.command()
def start():
    subprocess.run(['quikey-daemon', 'start'])

@cli.command()
def stop():
    subprocess.run(['quikey-daemon', 'stop'])
