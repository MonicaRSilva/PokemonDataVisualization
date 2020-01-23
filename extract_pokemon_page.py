''' Extract and save Pokemon data'''
from selenium import webdriver
from bs4 import BeautifulSoup
from pokedata import PokeData

 
# Starts the webdriver and opens the list of the list of all pokemons 
browser = webdriver.Chrome('webdriver/chromedriver')
browser.implicitly_wait(6)
rootsite = 'https://pokemondb.net'
browser.get(rootsite+'/pokedex/national')
 
# Gets the links of all pokemons

links = []
content = browser.page_source
soup = BeautifulSoup(content, 'html.parser')
for div in soup.findAll('div',{'class':'infocard-list infocard-list-pkmn-lg'}):
    for a in div.findAll('a',{'class':'ent-name'}): 
        links.append(rootsite+a['href'])


for link in links[:]:
    browser.get(link)

    content = browser.page_source
    pokemon = PokeData(content)
    pokemon.get_data()


    pokemon.save_to_file()
    