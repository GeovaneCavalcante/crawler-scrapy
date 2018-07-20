import requests
from bs4 import BeautifulSoup as bs
import pprint
import json
from pymongo import MongoClient


class CrawlerAnimes(object):

    animesAll = {}
    epListDescription = []
    epListFrame = []
    animes = []
    conection = MongoClient()
    db  = conection['api_animes']

    #Busca todos animes da pagina 1
    def getAnimes(self):
  
        r  = requests.get('https://www.animesorion.tv/animes-dublados')  
        soup = bs(r.content, 'html.parser')
        
        divAnimesDublados = soup.find_all("div", class_="contentBox")

        for link in divAnimesDublados[0].find_all('div', class_='thumb'):

            link1 = link.find('a')
            if link.get('class') == ['number']:
                self.getAnimesList(link.get('href'))
            else:
                self.animes.append(link1)   

        ''' Comenta isso pra fazer uma requisição pequena
        for link in divAnimesDublados[0].find_all('a'):
            if link.get('class') == ['number']:
                self.getAnimesList(link.get('href'))
        '''        

        a = 1
        for ani in self.animes:
            a += 1
            anime = {}
            anime['title'] = ani['title']
            anime['linkEpDescription'] = ani['href']
            anime['imgAnime'] = ani.find_all('img')[0]['src']
            ##print(json.dumps(anime, sort_keys=True, indent=4, separators=(',', ': ')))
            self.animesAll[a] = anime
     


    #Busca os demais animes das paginação
    def getAnimesList(self, url):

        r  = requests.get(url)
        soup = bs(r.content, 'html.parser')
        divAnimesDublados = soup.find_all("div", class_="contentBox")

        for link in divAnimesDublados[0].find_all('div', class_='thumb'):
            link = link.find('a')

            if link.get('class') != ['number']:
                self.animes.append(link)


    #Busca os lista de episódios de um anime
    def getAnimesEpList(self):

        a = 0

        for anime in self.animesAll:

            r  = requests.get(self.animesAll[anime]['linkEpDescription'])
            soup = bs(r.content, 'html.parser')

            ul = soup.find_all("ul", id="lcp_instance_0")

            listEp = []

            for li in ul[0].find_all('a'):
                ep = {}
                ep['frame'] = self.getAnimesEpFrame(li.get('href'))
                ep['titleEp'] = li.get('title')
                listEp.append(ep)
          
            self.animesAll[anime]['Epsodios'] = listEp
        
        
    #Busca o poster e o link do frame do episódios
    def getAnimesEpFrame(self, link):

        r  = requests.get(link)
        soup = bs(r.content, 'html.parser')

        ep={
            'linkFrame': soup.find_all("source")[0]['src'],
            'posterEp': soup.find_all("video")[0]['poster']
        }

        return ep


    def insertAnimes(self):

        for anime in self.animesAll:
            self.db.animes.insert_one(self.animesAll[anime]).inserted_id


    def printJson(self):

        for x in self.db.animes.find():
            pprint.pprint(x)
