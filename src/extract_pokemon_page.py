''' Extract and save Pokemon data'''
from bs4 import BeautifulSoup
import requests
from pokedata import PokeData

 

rootsite = 'https://pokemondb.net'
response = requests.get(rootsite+'/pokedex/national')
 
# Gets the links of all pokemons
if response.status_code == 200:
    links = []
    soup = BeautifulSoup(response.text, 'html5lib')
    for div in soup.findAll('div',{'class':'infocard-list infocard-list-pkmn-lg'}):
        for a in div.findAll('a',{'class':'ent-name'}): 
            links.append(rootsite+a['href'])


    for link in links[898:]:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html5lib')
        pokemon = PokeData(soup)
        pokemon.get_data()


        pokemon.save_to_file()
else:
    print("Failed to retrieve the web page")
    