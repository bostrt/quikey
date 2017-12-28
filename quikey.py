#!/usr/bin/env python

import click
import peewee
from terminaltables import AsciiTable
import humanize
from xdg import XDG_CACHE_HOME
import signal
import os

from models import PhraseStore

MARKER = '''
# Everything after this line will be ignored.
# Insert your quikey phrase into this file then save and close.
'''

@click.group()
@click.pass_context
def cli(ctx):
    pass
    
@cli.command()
@click.option('--name' ,'-n', required=True, help='Name of quikey phrase to add.')
@click.option('--tag', '-t', multiple=True, help='Optional tags for the phrase. You can specify this option multiple times.')
@click.option('--phrase', '-p', help='The full phrase to add. If this option is not specified then your default editor ($EDITOR) will be used.')
@click.pass_context
def add(ctx,name,phrase,tag):
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
    try:
        PhraseStore.put(name, contents, tag)
        click.echo('quikey phrase with key of %s added.' % name)
    except peewee.IntegrityError:
        click.echo('quikey phrase with key of %s already exists. Please choose another --name/-n value.' % name)

@cli.command()
@click.option('--name', '-n', required=True, help='Name of quikey phrase to edit.')
@click.pass_context
def edit(ctx,name):
    phrase = PhraseStore.get(name)
    if phrase is not None:
        contents = click.edit(phrase + '\n\n' + MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0].rstrip('\n')
            PhraseStore.update(name, contents)
            click.echo('quikey phrase with key of %s updated.' % name)
        else:
            click.echo('quikey phrase with key of %s not updated' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
        

@cli.command()
@click.option('--name', '-n', required=True, help='Name of quikey phrase to remove.')
@click.pass_context
def rm(ctx,name):
    # TODO: Support multiple.
    if PhraseStore.delete(name):
        click.echo('quikey phrase with key of %s has been deleted.' % name)
    else:
        click.echo('quikey phrase with key of %s does not exist.' % name)
    
@cli.command()
@click.option('--show-all', is_flag=True)
@click.pass_context
def ls(ctx, show_all):
    table = [['Name', 'Tags', 'Last Modified', 'Phrase']]
    phrases = PhraseStore.get_all()
    for phrase in phrases:
        tags = ', '.join([x.name for x in phrase.tags])
        value = (phrase.value[:40] + '...' if len(phrase.value) > 40  and not show_all else phrase.value)
        table.append([phrase.key, tags, humanize.naturalday(phrase.modified), value])
    output = AsciiTable(table)
    click.echo(output.table)
    
@cli.command()
@click.pass_context
def start(ctx):
    pass

@cli.command()
@click.pass_context
def stop(ctx):
    try:
        pidfile = XDG_CACHE_HOME + '/quikey/quikey.pid'    
        pid = open(pidfile, 'r').readline()
        os.kill(int(pid), signal.SIGTERM)
    except FileNotFoundError:
        click.echo('quikey is not running')

@cli.command()
@click.pass_context
def restart(ctx):
    pass

if __name__=='__main__':
    cli(obj={})
