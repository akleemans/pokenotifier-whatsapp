import urllib2
import time
import json
import os
import subprocess

def download(url):
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()
    return data

def send_whatsapp(nr, msg):
    command = 'yowsup/yowsup-cli demos -l '+config['whatsapp']['sender']
    command += ':'+config['whatsapp']['sender_pw']+' -M -s ' + nr + ' "' + msg + '"'
    subprocess.call(command, shell=True)
    print 'Whatsapp sent.'
    time.sleep(2)

def load_config():
    global config, query_url
    # loading configuration
    with open('config.json', 'r') as data_file:
        config = json.load(data_file)

    ne = config['coords']['ne']
    sw = config['coords']['sw']
    query_url = config['server'] + '/raw_data?pokemon=true&pokestops=true&gyms=false&scanned=false&swLat='
    query_url += str(sw[0]) + '&swLng=' + str(sw[1]) + '&neLat=' + str(ne[0]) + '&neLng=' + str(ne[1])

def main():
    load_config()
    if not config['repetition']['repeat']:
        find_pokemon()
        print 'Finished.'
    else:
        while True:
            load_config()
            try:
                find_pokemon()
            except (urllib2.HTTPError, urllib2.URLError) as error:
                print 'Some error occured, trying again later: ', error.read()
            print 'Sleeping.'
            time.sleep(config['repetition']['delay_sec'])

def find_pokemon():
    print time.strftime("%H:%M:%S") + ' starting up...'
    # getting already found pokemon
    with open('found.json', 'r') as data_file:
        history = json.load(data_file)

    print 'Downloading...'
    found = []
    content = json.loads(download(query_url))
    encounters = content['pokemons']
    print 'Got', len(encounters), 'encounters.'

    print 'Searching for rare pokemon...'
    for pokemon in encounters:
        if pokemon['pokemon_id'] in config['rare_pokemon']:
            print 'Found a', pokemon['pokemon_name']
            now = time.strftime("%H:%M:%S")
            t = pokemon['disappear_time'] - int(time.time())*1000
            t = t/1000.0
            m = int(t/60.0)
            s = int(t - m*60.0)
            link = 'https://maps.google.com/maps?q=loc:' + str(pokemon['latitude']) + ',' + str(pokemon['longitude'])
            entry = {'pokemon_name': pokemon['pokemon_name'], 'pokemon_id': pokemon['pokemon_id'], 'lon': pokemon['longitude'], 'lat': pokemon['latitude'], 'encounter_id': pokemon['encounter_id']}

            if entry not in history:
                history.append(entry)
                with open('found.json', 'w') as outfile:
                    json.dump(history, outfile, indent=4)

                msg = str(now) + ' Found ' + pokemon['pokemon_name'].encode('ascii', 'ignore').decode('ascii') + ', stays another ' + str(m) + ' m ' + str(s) + 's' + '\n' + link
                print msg
                send_whatsapp(config['whatsapp']['recipient'], msg)

if __name__ == "__main__":
    main()
