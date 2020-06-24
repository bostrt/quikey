#!/usr/bin/env python

import click
from terminaltables import AsciiTable
import humanize
import signal
import os
import json
import logging

from quikey.models import Database
from quikey.directories import AppDirectories
from quikey.version import __version__
from quikey.autostart import enableAutostart, disableAutostart
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

def phrasefind(location):
    filedict = {}
    for r, d, f in os.walk(location):
        for file in f:
            if ".txt" in file:
                filepath = os.path.join(r, file)
                filejson = os.path.join(r, "." + file[:-4] + ".json")
                #if filejson doesn't exist, skip that file on import
                if not os.path.isfile(filejson):
                    logging.error("json config file does not exist for %s ... Skipping import on this key!" % filepath)
                    continue
                else:
                    with open(filejson) as openfile:
                        try:
                            filedata = json.load(openfile)
                        except json.JSONDecodeError:
                            logging.error("Invalid json detected on %s. Skipping import on this key." % filejson)
                            continue
                    #check if the 'type' setting is a phrase. If it isn't then skip it
                    if (filedata.get('type') == "phrase"):
                        modes = filedata.get('modes')
                        #modes in autohotkey are 1 for abbreviation, 3 for hotkey. Use this to check what we want to message
                        if sum(modes) == 1:
                            abbreviation = filedata.get('abbreviation', {}).get('abbreviations')
                            logging.info('Importing %s.' % (filepath))
                        elif sum(modes) == 4:
                            abbreviation = filedata.get('abbreviation', {}).get('abbreviations')
                            logging.warning('Modes for %s are both abbreviation and hotkey. Using abbreviation for import' % filepath)
                        elif sum(modes) == 3:
                            #there are too many invalid hotkeys, such as F keys. Skip these for now
                            logging.warning('Mode for %s is hotkey. Please manually add this phrase with an abbreviation, or change from hotkey to abbreviation.' % filepath)
                            continue
                        else:
                            logging.error('Could not auto-detect mode for %s - please manually import this phrase.' % filepath)
                            continue
                        with open(filepath) as phrasefile:
                            value = phrasefile.read()
                        if len(abbreviation) > 1:
                            print("Multiple abbreviations were found. Please select which number you would like to use and hit enter.\n")
                            for entry in abbreviation:
                                print(1 + abbreviation.index(entry), end=" ")
                                print(entry)
                            while True:
                                try:
                                    abbreviationselection = int(input("Your selection: ")) - 1
                                    key = abbreviation[abbreviationselection]
                                except IndexError:
                                    print("%s is not a valid selection, please pick a valid entry number." % abbreviationselection)
                                    continue
                                except ValueError:
                                    print("Selection must be a number, please try again.")
                                    continue
                                else:
                                    break
                        else:
                            key = abbreviation[0]
                        filedict[key] = value
                    else:
                        print("%s is not a 'phrase' type. Skipping import on this key!" % filepath)
                        continue
    return filedict

@cli.command()
@click.option('--location', '-l', default=os.getenv("HOME")+"/.config/autokey", show_default=True, help='Location of top level directory to import from autokey')
@click.pass_context
def keyimport(ctx,location):
    print(ctx)
    tags = ['autokey-imports']
    db = ctx.obj['database']
    importfiles = phrasefind(location)
    for key in importfiles:
        contents = None
        if importfiles[key] is not None:  
            contents = importfiles[key]
        else:
            contents = click.edit('\n\n'+MARKER)
            if contents is not None:
                contents = contents.split(MARKER, 1)[0].rstrip('\n')
            else:
                click.echo('quikey phrase with key of %s not added' % key)
                return
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
