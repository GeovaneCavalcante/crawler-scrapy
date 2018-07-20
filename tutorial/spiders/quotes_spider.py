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


class QuotesSpider(scrapy.Spider, CrawlerAnimes):

    name = "quotes"
       
    def start_requests(self):

        self.getAnimes()
        self.getAnimesEpList()
        
        for anime in self.animesAll:

            yield scrapy.Request(
                url=self.animesAll[anime]['linkEpDescription'], 
                callback=self.parse_animesDublados, 
                meta={'anime': anime}
            )
        
         
            
    @callback_args
    def parse_animesDublados(self, response, anime):

        liste = Selector(response=response).xpath('//strong/text()').extract()
        del(liste[0])
        
        generos = []

        for genero in liste[1].split(":")[1].split(","):
            generos.append(self.removerAcentosECaracteresEspeciais(genero))

        self.animesAll[anime]['genero'] = generos
       
        self.animesAll[anime]["sinopse"] = liste = Selector(response=response).xpath('//div[@class="sinopse"]/text()').extract()
        print(json.dumps(self.animesAll[anime], sort_keys=True, indent=4, separators=(',', ': ')))   
        self.db.animes_dublados.insert_one(self.animesAll[anime]).inserted_id
        #print(liste)


    def removerAcentosECaracteresEspeciais(self, palavra):

        # Unicode normalize transforma um caracter em seu equivalente em latin.
        return normalize('NFKD', palavra).encode('ASCII', 'ignore').decode('ASCII').lower().strip(" ")
 
    
       