#!/usr/bin/env python

import click
import peewee
from models import PhraseStore

MARKER = '''\n\n
# Everything after this line will be ignored.
# Insert your quikey phrase into this file then save and close.'''

@click.group()
@click.pass_context
def cli(ctx):
    pass
    
@cli.command()
@click.option('--name' ,'-n', required=True, help='Name of quikey phrase to add.')
@click.option('--phrase', '-p', help='The full phrase to add. If this option is not specified then your default editor ($EDITOR) will be used.')
@click.pass_context
def add(ctx,name,phrase):
    contents = None
    if phrase is not None:
        contents = phrase
    else:
        contents = click.edit(MARKER)
        if contents is not None:
            contents = contents.split(MARKER, 1)[0].rstrip('\n')
        else:
            click.echo('quikey phrase with key of %s not added' % name)
            return
    try:
        PhraseStore.put(name, contents)
        click.echo('quikey phrase with key of %s added.' % name)
    except peewee.IntegrityError:
        click.echo('quikey phrase with key of %s already exists. Please choose another --name/-n value.' % name)

@cli.command()
@click.option('--name', '-n', required=True, help='Name of quikey phrase to edit.')
@click.pass_context
def edit(ctx,name):
    phrase = PhraseStore.get(name)
    if phrase is not None:
        contents = click.edit(phrase + MARKER)
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
@click.pass_context
def ls(ctx):
    # TODO: Format into table or fixed width columns.
    phrases = PhraseStore.get_all()
    for phrase in phrases:
        print('%s => %s' % (phrase.key, phrase.value))

if __name__=='__main__':
    cli(obj={})
