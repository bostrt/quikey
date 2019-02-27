#!/usr/bin/env python

import click
from terminaltables import AsciiTable
import humanize
from xdg import XDG_CACHE_HOME
import signal
import os

from quikey.models import Database
from quikey.directories import AppDirectories
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
@click.option('--show-all', is_flag=True)
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
def start():
    subprocess.run(['quikey-daemon', 'start'])

def read_pid():
    pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'
    try:
        with open(pidfile, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

@cli.command()
def stop():
    subprocess.run(['quikey-daemon', 'stop'])
