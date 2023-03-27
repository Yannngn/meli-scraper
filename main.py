import os, errno, json, bs4

from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
import tqdm
from argparse import ArgumentParser

### Exemplos
# python main.py -s olx -n ranger -m ford -y 2022 -o /data 

DEBUG = True

class MeLi:
    def __init__(self) -> None:
        # https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes/fiat/strada/fiat-strada-2022_YearRange_2022-2022
        self.targets = []
        self.image_links = []
        self.targets_dict = {}
        
        self.page = 1
        self.increment = 48
        
        self.container = {'class':'ui-search-result__content ui-search-link'}
        #self.next_page = """//*[@id="root-app"]/div/div/section/div[3]/ul/li[3]/a"""
        self.image_container = {'class':'ui-pdp-image ui-pdp-gallery__figure__image'}        
        self.fmt_len = 5 #.webm
        
        self.update_url()
        
    def update_url(self) -> None:
        self.url = f'https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes/{self.maker}/{self.name}/{self.name}-{self.maker}-{self.year}_Desde_{self.page}_YearRange_{self.year}-{self.year}_NoIndex_True'

class OLX:
    def __init__(self) -> None:
        # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/fiat/strada/2022?q=fiat%20strada
        self.targets = []
        self.image_links = []
        self.targets_dict = {}
        
        self.page = 1
        self.increment = 1
        
        self.fmt = 'jpg'
         
        self.container = {'class':'fnmrjs-0 fyjObc'}
        #self.next_page = """//*[@id="listing-main-content-slot"]/div[12]/div/div/div[2]/div/div[1]/div[1]/a""" #//*[@id="listing-main-content-slot"]/div[12]/div/div/div[2]/div/div[1]/div[1]/a
        self.image_container = {'class':'image'}  
        self.fmt_len = 4 #.jpg
        
        self.update_url()
    
    def update_url(self):
        self.url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{self.maker}/{self.name}/{self.year}?o={self.page}&q={self.name}%20{self.maker}%20{self.year}'
        
class Scraper:
    def __init__(self, hparams) -> None:
        self.site_name = hparams.site.lower()
        self.name = hparams.name.lower()
        self.maker = hparams.maker.lower()
        self.year = hparams.year
        
        self.output_path = hparams.output
        self.force_name = hparams.force_name
        
        if hparams.folder:
            self.folder = hparams.folder
        else:
            self.folder = f'{self.maker}_{self.name}'
        
        if hparams.prefix:
            prefix = hparams.prefix.lower()
            if prefix[:-1] == '_': 
                prefix = prefix[:-1]
            
            self.prefix = prefix
        else:
            self.prefix = f'{self.maker}_{self.name}_{self.year}'
            
        self.max = hparams.n_cars
        self.fmt = hparams.fmt
    
    def start(self) -> None:
        s = Service(ChromeDriverManager().install())
        
        is_olx = False
        is_meli = False
        
        try:
            if self.site == 'olx': is_olx = True
                
            elif self.site == 'meli': is_meli = True
                              
            elif self.site == 'both': is_meli, is_olx = True, True
                
        except KeyError as e:
            print(f"{e}: self.site site not found. Use 'olx', 'meli' or 'both'")
            
        if is_olx:
            print('=> Starting OLX scraper')
            olx = OLX()
            self.driver = webdriver.Chrome(service=s)
            self.loop_drive(olx)
            self.scraper(olx)
            self.downloader(olx)
            
        if is_meli:
            print('=> Starting Mercado Libre scraper')
            meli = MeLi()
            self.driver = webdriver.Chrome(service=s)
            self.loop_drive(meli)
            self.scraper(meli)
            self.downloader(meli)
                       
    def drive(self, site) -> None:
        ### method that gets all item links of the page
        page_html = self.driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
        # class that points to the containers of the ad page
        containers = pageSoup.findAll('a', site.container)
       
        for container in containers:
            site.targets.append(container.attrs['href'])
        
        # unique list of links
        self.n_links = len(list(set(site.targets)))
                
    def loop_drive(self, site) -> None:
        self.n_links = len(site.targets)
        
        self.driver.get(site.url)
        self.drive(site)
        
        while self.n_links < self.max:
            # XPATH that contains the buttom to the next page
            try:
                site.page += site.increment
                site.update_url()
                self.driver.get(site.url)
                self.drive()
            except Exception as e:
                print(f'{site.url}: No more items on this site.')
            
        if self.n_links > self.max: 
            self.n_links = self.max
            site.targets = site.targets[:self.max]
        
        print(f'Found {self.n_links} of {self.max} unique items')
            
    def scraper(self, site) -> None:
        
        site.targets = list(set(site.targets))
        
        for link in tqdm.tqdm(site.targets):
            self.driver.get(link)
            
            page_html = self.driver.page_source
            try:
                if self.force_name:
                    assert self.name in self.driver.title.lower()
                
                pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
                ### class that contains the image source
                images = pageSoup.findAll('img', site.image_container)
                
                for image in images:
                    ### atribute of the image that contains the source
                    image = image.attrs['src']
                    image = f'{str(image[:-site.fmt_len])}.{self.fmt}'
                    site.image_links.append(image)
                
                site.targets_dict[link] = [i for i in site.image_links]
                
            except AssertionError as ae:
                print(f'{ae}: {self.driver.title} doesn\'t match query {self.name}')

        self.driver.close()
                
        print(f"A total of {len(site.image_links)} images was found.")
        
    def downloader(self, site) -> None:
        path = os.path.join(self.output_path, f'{self.maker}_{self.name}')

        try:
           os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        with open(os.path.join(path, f'{self.site_name}_{self.prefix}.json'), 'w') as fp:
            json.dump(site.targets_dict, fp)
         
        for i, link in tqdm.tqdm(enumerate(site.image_links)):
            
            # How to make this loop use multiprocessing?
            
            req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            with open(os.path.join(path, f"{self.site_name}_{self.prefix}_{i:04d}.{self.fmt}"), 'wb') as f:
                f.write(webpage)    
           
        print('done!')
        
    @staticmethod
    def add_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser])

        parser.add_argument('--site', '-s', type=str, required=True)
        parser.add_argument('--name', '-n', type=str, required=True)
        parser.add_argument('--maker', '-m', type=str, required=True)
        parser.add_argument('--year', '-y', type=int, required=True)
        parser.add_argument('--output', '-o', type=str, required=True)
        parser.add_argument('--fmt', type=str, default='jpg')
        parser.add_argument('--n_max', type=int, default=200)
        parser.add_argument('--force_name', type=bool, default=False)
        parser.add_argument('--folder', type=str)
        parser.add_argument('--prefix', type=str)
        
        return parser

def main(hparams):
    scrap = Scraper(hparams)
    scrap.start()
    
if __name__ == '__main__':
    parent_parser = ArgumentParser(add_help=False)

    parser = Scraper.add_args(parent_parser)
    hparams = parser.parse_args()
    
    main(hparams)