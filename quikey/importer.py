import os
import logging
import json

def PhraseFind(location):
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
