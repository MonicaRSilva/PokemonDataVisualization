import csv
import os.path
from bs4 import BeautifulSoup
import re

class PokeData:

    # Constant used to define the columns order in the csv file
    COLUMNS = ['national_number', 'full_name', 'name', 'type1', 'type2', 'species'
                ,'abilities', 'hidden_ability', 'pre_evolution', 'evolution'
                ,'gender_ratio_male', 'gender_ratio_female', 'egg_group1', 'egg_group2'
                ,'egg_cycles', 'egg_cycles_steps', 'catch_rate', 'catch_rate_pct'
                ,'ev_yield',  'height', 'height_m', 'weight', 'weight_kg'
                ,'base_friendship', 'base_friendship_ds', 'base_exp', 'growth_rate'
                ,'name_jp','name_jp_ro','name_de','name_fr', 'local' 
                ,'base_stats', 'base_stats_min', 'base_stats_max'
                ,'base_stats_total']
    
    def __init__(self, soup):
        self.pokedict = None
        self.pokedicts = []
        #html = html.replace('&nbsp;', ' ')
        self.soup = soup

            
    def get_vitals(self, div_id):
        tab_div = self.soup.find('div',{'id':div_id})

        tds = tab_div.find('table',{'class':'vitals-table'}).findAll('td')
        self.pokedict['national_number'] = tds[0].text
        types = tds[1].text.split()
        if len(types) > 0:
            self.pokedict['type1'] = types[0]
        if len(types) > 1:
            self.pokedict['type2'] = tds[1].text.split()[1]
        self.pokedict['species'] = tds[2].text
        
        height = tds[3].text
        if height.strip() != '—':
            self.pokedict['height'] = height[height.index('(')+1:height.index(')')]
            self.pokedict['height_m'] = height[:height.index('(')].strip().replace(' ',' ')

        
        weight = tds[4].text
        if weight.strip() != '—':
            self.pokedict['weight'] = weight[weight.index('(')+1:weight.index(')')].replace(' ',' ')
            self.pokedict['weight_kg'] = weight[:weight.index('(')].strip().replace(' ',' ')
        
        abilities = []
        for span in tds[5].findAll('span'):
            a = span.find('a')
            abilities.append(a.text)
        self.pokedict['abilities'] = abilities
        
        ha = tds[5].findAll('small')
        if len(ha) == 1:
            self.pokedict['hidden_ability'] = ha[0].find('a').text
        
        for br in tds[6].find_all('br'):
            br.replace_with('\n')
        self.pokedict['local'] = tds[6].text.strip().split('\n')
 

    def get_training(self, div_id):
        tab_div = self.soup.find('div',{'id':div_id})
        tds = tab_div.find('h2',text='Training').parent.findAll('td')
        self.pokedict['ev_yield'] = tds[0].text.strip() if tds[0].text.strip() != '—' else ''
        if tds[1].text.strip() != '—':
            catch_rate = tds[1].text.split()[0].strip()
            catch_rate_pct = tds[1].find('small').text.strip()
            catch_rate_pct = catch_rate_pct[1:catch_rate_pct.index('%')]
            self.pokedict['catch_rate'] = catch_rate
            self.pokedict['catch_rate_pct'] = catch_rate_pct
        if tds[2].text.strip() != '—':
             self.pokedict['base_friendship'] = tds[2].text.split()[0]
             self.pokedict['base_friendship_ds'] = tds[2].find('small').text.strip()[1:-1]
        self.pokedict['base_exp'] = tds[3].text.strip() if tds[3].text.strip() != '—' else ''
        self.pokedict['growth_rate'] = tds[4].text.strip() if tds[4].text.strip() != '—' else ''

        
    def get_breeding(self, div_id):
        tab_div = self.soup.find('div',{'id':div_id})
        tds = tab_div.find('h2',text='Breeding').parent.findAll('td')
        if tds[0].text.strip() != '—':
            groups = tds[0].text.strip().split(', ')
            self.pokedict['egg_group1'] = groups[0]
            self.pokedict['egg_group2'] = groups[1] if len(groups)>1 else ''
            
        male_ratio = '0'
        female_ratio = '0'
        if tds[1].text.strip() != '—':
            for span in tds[1].find_all('span'):
                if '% male' in span.text:
                    male_ratio = span.text[:span.text.index('%')]
                elif '% female' in span.text:
                    female_ratio = span.text[:span.text.index('%')]
        self.pokedict['gender_ratio_male'] = male_ratio
        self.pokedict['gender_ratio_female'] = female_ratio
        
        if tds[2].text.strip() != '—':
            self.pokedict['egg_cycles'] = tds[2].text.split()[0]
            self.pokedict['egg_cycles_steps'] = tds[2].find('small').text.strip().split()[0][1:]
      
    
    def get_stats(self, div_id):
        tab_div = self.soup.find('div',{'id':div_id})
        trs = tab_div.find('h2',text='Base stats').parent.findAll('tr')
        att_names = ['hp','att','def','sp.atk','sp.def','speed']
        base_values = []
        min_values = []
        max_values = []
        for tr in trs[:-1]:
            tds = tr.find_all('td',{'class':'cell-num'})
            base_values.append(tds[0].text.strip())
            min_values.append(tds[1].text.strip())
            max_values.append(tds[2].text.strip())
        self.pokedict['base_stats'] = dict(zip(att_names,base_values))
        self.pokedict['base_stats_min'] = dict(zip(att_names,min_values))
        self.pokedict['base_stats_max'] = dict(zip(att_names,max_values))
        if len(trs) > 0:
            self.pokedict['base_stats_total'] = trs[-1].find('td').text.strip()
    
    
    def get_evolution_info(self):
        pre_evolution = ''
        evolution = []
        for div in self.soup.find_all('div',{'class':'infocard-list-evo'}):
            if div.parent.name != 'span':
                name_bf = '' 
            for infocard in div.find_all('div',{'class':'infocard'}): 
                a_ent_name = infocard.find('a',{'class':'ent-name'})
                smalls = a_ent_name.parent.find_all('small')
                
                if len(smalls) > 2:
                    name = smalls[1].text.strip()
                else:
                    name = a_ent_name.text.strip()
                
                if name == self.pokedict['full_name']:
                    pre_evolution = name_bf
                if name_bf == self.pokedict['full_name'] and name not in evolution:
                    evolution.append(name)
                if 'infocard-list-evo' not in infocard.parent.parent['class']:
                    name_bf = name
        self.pokedict['pre_evolution'] = pre_evolution
        self.pokedict['evolution'] = evolution
    

    def get_names(self, div_id):
        self.pokedict['name'] = self.soup.find('h1').text.strip()
        other_lang = self.soup.find('h2',text='Other languages')
        if other_lang != None:
            tds = other_lang.parent.find_all('td')   
            names_jp = tds[1].text.split()         
            self.pokedict['name_jp'] = names_jp[0].strip()
            self.pokedict['name_jp_ro'] = names_jp[1].strip()[1:-1] if len(names_jp) > 1 else ''
            self.pokedict['name_de'] = tds[2].text.strip()
            self.pokedict['name_fr'] = tds[3].text.strip()
            
        tabs = self.soup.find('div', {'class':'sv-tabs-tab-list'}).find_all('a')

        for tab in tabs:
            if div_id == tab['href'][1:]:
                self.pokedict['full_name'] = tab.text.strip()
      
    
    def get_data(self):
        tabs = self.soup.find('div', {'class':'sv-tabs-tab-list'}).find_all('a')

        for tab in tabs:
            div_id = tab['href'][1:]
            self.pokedict = dict.fromkeys(PokeData.COLUMNS,'')
            self.get_names(div_id)
            self.get_vitals(div_id)
            self.get_training(div_id)
            self.get_breeding(div_id)
            self.get_stats(div_id)
            self.get_evolution_info()
            self.pokedicts.append(self.pokedict)

    # Save to file
    def save_to_file(self, csv_file='pokemon.csv'):
        mode = 'a' if os.path.isfile(csv_file) else 'w'
        try:
            with open(csv_file,mode) as file:
                writer = csv.DictWriter(file, fieldnames=PokeData.COLUMNS)
                if mode == 'w':
                    writer.writeheader()
                for poke in self.pokedicts:
                    writer.writerow(poke)
        except IOError:
            print('I/O Error')