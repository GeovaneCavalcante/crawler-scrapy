import scrapy
from scrapy.selector import Selector
from .crawller import CrawlerAnimes
import json
from scrapy.utils.python import get_func_args
from functools import wraps
from unicodedata import normalize



def callback_args(f):
    args = get_func_args(f)[2:]
    @wraps(f)
    def wrapper(spider, response):
        return f(spider, response, 
            **{k:response.meta[k] for k in args if k in response.meta})
    return wrapper


class QuotesSpider(scrapy.Spider):

    name = "quotes"
       
    def start_requests(self):

        #Animes Dublados
        """
        url = 'https://www.animesorion.tv/animes-dublados'
        modelAnime = CrawlerAnimes()
        
        modelAnime.getAnimes(url)
        modelAnime.getAnimesEpList()

        
        for anime in modelAnime.animesAll:

            yield scrapy.Request(
                url=modelAnime.animesAll[anime]['linkEpDescription'], 
                callback=self.parse_animesDublados, 
                meta={'anime': anime, 'modelAnime': modelAnime}
            )
               
        #Animes Legendados
        """
        url = 'https://www.animesorion.tv/todos-os-animes-onlines'
        modelAnime2 = CrawlerAnimes()
        modelAnime2.getAnimes(url)
        modelAnime2.getAnimesEpList()
        
        for anime in modelAnime2.animesAll:

            yield scrapy.Request(
                url=modelAnime2.animesAll[anime]['linkEpDescription'], 
                callback=self.parse_animesLegendados, 
                meta={'anime': anime, 'modelAnime': modelAnime2}
            )    
     

    @callback_args
    def parse_animesDublados(self, response, anime, modelAnime):

        liste = Selector(response=response).xpath('//strong/text()').extract()
        del(liste[0])
        
        generos = []

        for genero in liste[1].split(":")[1].split(","):
            generos.append(self.removerAcentosECaracteresEspeciais(genero))

        modelAnime.animesAll[anime]['genero'] = generos
        modelAnime.animesAll[anime]["sinopse"] = liste = Selector(response=response).xpath('//div[@class="sinopse"]/text()').extract()
        modelAnime.db.animes_dublados.delete_many({'title': modelAnime.animesAll[anime]['title']})
        modelAnime.db.animes_dublados.insert_one(modelAnime.animesAll[anime]).inserted_id
      

    @callback_args
    def parse_animesLegendados(self, response, anime, modelAnime):

        liste = Selector(response=response).xpath('//strong/text()').extract()
        del(liste[0])
        
        generos = []

        for genero in liste[1].split(":")[1].split(","):
            generos.append(self.removerAcentosECaracteresEspeciais(genero))

        modelAnime.animesAll[anime]['genero'] = generos
        modelAnime.animesAll[anime]["sinopse"] = liste = Selector(response=response).xpath('//div[@class="sinopse"]/text()').extract()
        modelAnime.db.animes_legendados.delete_many({'title': modelAnime.animesAll[anime]['title']})
        modelAnime.db.animes_legendados.insert_one(modelAnime.animesAll[anime]).inserted_id


    def removerAcentosECaracteresEspeciais(self, palavra):

        # Unicode normalize transforma um caracter em seu equivalente em latin.
        return normalize('NFKD', palavra).encode('ASCII', 'ignore').decode('ASCII').lower().strip(" ")
    
