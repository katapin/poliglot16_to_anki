#!/usr/bin/python

import sys, os
import argparse
from requests_html import HTMLSession


userwords_url   = 'https://poliglot16.ru/user/words/'
collectionlist_url = 'https://poliglot16.ru/user/group/'
profile_url = 'https://poliglot16.ru/user/'
sound_url = 'https://poliglot16.ru/audio/words/'


#Parent parser to share on between files
pparser = argparse.ArgumentParser(add_help=False)
pparser.add_argument('collection', nargs='*', help="Collection name or ID")
pparser.add_argument('--allwords', help="Grab all words from the user profile", action='store_true')
pparser.add_argument('--token', nargs='?', help="Token in the format USERID:SESSIONID")
pparser.add_argument('--login', nargs='?', help="Login to sign in to your account")
pparser.add_argument('--password', nargs='?', help="Password to sign in to your account", metavar='PASS')
    
  

def authorize(login, password):
    """Sign in to obtain session id."""
    session = HTMLSession()
    response = session.post(profile_url, {'email':login, 'password':password})
    if response.status_code != 200:
        raise Exception(f"Can't sign in. The server response is {response}")
    cookies = session.cookies.get_dict()
    token='{user}:{PHPSESSID}'.format(**cookies)
    print(f"Your token is '{token}'. Use it henceforth instead the login+password pair")
    return token

def save_result_csv(entries, outfile):
    with open(outfile,'w') as f:
        for entry in entries:
            f.write('{word}<br>{phonetic}\t{translated}\n'.format(**entry))
    print(f"The words have been successfully stored into '{outfile}'")
            
def do_request(url, session):
    response = session.get(url)
    if response.status_code != 200:
        raise Exception(f"Can't fetch the html page {url}: {response}")
    return response

def grab_collection(page_id: int, session):
    """Parse the table with words."""
    if page_id==0:
        url=userwords_url
    else:
        url=userwords_url+str(page_id)
    response = do_request(url,session)
    word_table = response.html.find('#tab')[0]
    nwords=len(word_table.element)-1    #The first element is the table caption
    if nwords < 1:
        print(f'Processing pageID={page_id}: there are no words in the collection')
        return 
    else:
        print(f'Processing pageID={page_id}: {nwords} words found')

    
    entries=[]
    for row in word_table.element[1:]:  #The first element is the table caption
        play_button = row[1]
        word_field  = row[2]
        trans_field = row[3]
        entries.append({'word':word_field[0].text,
            'phonetic':'[{}]'.format(word_field[1].text),
            'translated':trans_field[0].text,
            'sound':play_button[0].attrib['data-audio']})

    return entries    


            
def get_pageid_name_mapping(session):
    """Return the dict {name:pageid}."""
    response = do_request(collectionlist_url, session)
    rectangles = response.html.find('.col-xs-6.col-sm-4.col-md-3.item') # Colored rectangles in the page
    collections={}
    if len(rectangles) > 1:
        for i in range(1,len(rectangles)):     #The first rectangle is just an 'add button'
            #The last rectangle is the 'base group'. It doesn't have a settings button, 
            #which changes the order of the 'div' tags therein.
            if i+1 != len(rectangles):         
                a_tag = rectangles[i].element[1]
            else:
                a_tag = rectangles[i].element[0]  
            href = a_tag.attrib['href']
            collection_name = a_tag[0][3].text
            collections[collection_name.strip()] =  href.split('/')[3]
        
    return collections
            
def process_all_collectons(collections: list, session):
    """Loop through all the collections."""
    collection_ids={}
    all_words=[]
    for collection in collections:
        #Try to guess, is it an id or a name?
        if collection.isnumeric() and len(collection)>4:  #this is id
            all_words += grab_collection(collection, session)
        else:   #this is a name
            if not collection_ids:
                collection_ids = get_pageid_name_mapping(session)
            if collection not in collection_ids:
                print(f"Collection '{collection}' is not found. Skipping")
                continue
            else:
                print("Collection '{}' has pageID={}".format(collection, collection_ids[collection]))
                all_words += grab_collection(collection_ids[collection], session)
                
    return all_words
    
def check_argument_validity_and_prepare(argnspace, parser):
    if argnspace.allwords == False and len(argnspace.collection) == 0:
        parser.error("You should either give collecion IDs (or names) or use '--allwords' key "
            "to grab all words in the current user account")
    
    if argnspace.token:
        token=argnspace.token
    else:
        if argnspace.login == None or argnspace.password == None:
            parser.error("You must provide either the token or your login+password pair to sign in")
        token=authorize(argnspace.login,argnspace.password)
        
    if os.path.exists(argnspace.outfile[0]):
        print('Warning! The outfile will be overriden')
        
    #Prepare the session
    session = HTMLSession()
    userid, sessionid = token.split(':')
    session.cookies.set('agree','1')
    session.cookies.set('user',userid)
    session.cookies.set('PHPSESSID',sessionid)
    
    return session
    

if __name__ == '__main__': 
    ownparser = argparse.ArgumentParser(add_help=False)
    ownparser.add_argument('--outfile', nargs=1, help="Name of the output csv-file", required=True)
    
    combined_parser = argparse.ArgumentParser(description="Convert user's collections of words to csv format", 
        parents=[ownparser, pparser])
    
    argnspace=combined_parser.parse_args(sys.argv[1:])
    session=check_argument_validity_and_prepare(argnspace, combined_parser )
    
    
    if argnspace.allwords:
        all_entries = grab_collection(0, session)
    else:
        all_entries = process_all_collectons(argnspace.collection, session)
        
    if len(all_entries)>0:
        save_result_csv(all_entries, argnspace.outfile[0])
    else:
        print('Noting to do. Exiting...')
        

    
    
