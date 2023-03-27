#!/usr/bin/python

import sys, os, shutil
import argparse
import json
from anki.collection import Collection
from anki.exporting import AnkiPackageExporter
from anki.notes import Note
import poliglot2csv as main

def download_sound(path : str, filename : str, char, session):
    url = main.sound_url + f'{char}/{filename}'
    responce = session.get(url, stream=True)
    if responce.status_code == 200:
        with open(path+filename, 'wb') as f:
            responce.raw.decode_content = True
            shutil.copyfileobj(responce.raw, f)    
    else:
        print(f"Warning! Cannot downdload sound file '{filename}'. "
              f"The server responce: is {responce}")

def save_result_apkg(entries, outfile, deckname, session, without_sound=False):
    tmproot='tmp{}'.format(os.getpid())
    tmp_anki2 = tmproot+'.anki2'        #Temp file for anti db
    tmp_media = './'+tmproot+'.media/'   #The folder that will be created by anki to cache media
    col = Collection(tmp_anki2)
    
    #Create a custom deck
    newdeck=col.decks.new_deck()
    newdeck.name=deckname
    col.decks.add_deck(newdeck)
    did=col.decks.by_name(deckname)['id']  #deck id in anki notation
    
    #Load custom model
    model_dict = json.load(open('model.json'))
    col.models.add_dict(model_dict)
    mdl = col.models.by_name('poliglot16')
    mdl['did']=did
    
    for entry in entries:
        curnote = Note(col, mdl)
        curnote['Word'] = entry['word']
        # print(entry['word'])
        # print(entry)
        if entry['sound'] != '' and without_sound == False:
            curnote['Phonetic'] = '{}<br>[sound:{}]'.format(entry['phonetic'],entry['sound'])
            download_sound(tmp_media, entry['sound'], entry['word'][0].lower(), session)
        else:
            curnote['Phonetic'] = entry['phonetic']
        curnote['Translated'] = entry['translated']
        col.add_note(curnote,did)
        
    # col.save()
    exporter = AnkiPackageExporter(col)
    exporter.exportInto(outfile)
    
    #remove temp files
    del col
    os.remove(tmp_anki2)
    shutil.rmtree(tmp_media)
    
    if os.path.exists(outfile):
        print(f"The word collection have been successfully exported into '{outfile}'")
    else:
        print("Something is going wrong. Anki-pack hasn't been created.")
        

if __name__ == '__main__': 
    ownparser = argparse.ArgumentParser(add_help=False)
    ownparser.add_argument('--outfile', nargs=1, help="Name of the output Anki-package file", required=True)
    ownparser.add_argument('--deckname', nargs='?', help="Custom name of the deck", default='poliglot16', metavar='NAME')
    ownparser.add_argument('--without-sound', help="Don't store pronounces", action='store_true')
    
    combined_parser = argparse.ArgumentParser(description="Convert user's collections of words to Anki package", 
        parents=[ownparser, main.pparser])
    
    argnspace=combined_parser.parse_args(sys.argv[1:])
    session=main.check_argument_validity_and_prepare(argnspace, combined_parser )
    
    
    if argnspace.allwords:
        all_entries = main.grab_collection(0, session)
    else:
        all_entries = main.process_all_collectons(argnspace.collection, session)
        
    if len(all_entries)>0:
        save_result_apkg(all_entries, argnspace.outfile[0], argnspace.deckname, session, argnspace.without_sound)
    else:
        print('Noting to do. Exiting...')
        

    
    
