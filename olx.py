import os, errno, json, bs4

from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from argparse import ArgumentParser

DEBUG = False


### Exemplos
# ------ ------ ----- https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{marca}/{carro}/{year}?q={carro}
# python olx.py --url https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/fiat/strada/2022?q=strada --name fiat_strada --prefix fiat_strada_2022 --output /MeLi_Scraper

class Scraper:
    def __init__(self, hparams) -> None:
        s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=s)
        self.output_path = hparams.output
        
        self.name = hparams.name.lower()
        
        if hparams.prefix:
            prefix = hparams.prefix.lower()
            
            if prefix[:-1] != '_': 
                prefix = f'{prefix}_'
            
            self.prefix = prefix
            
        else:
            self.prefix = f'{hparams.name.lower()}_'
            
        self.url = hparams.url
        self.max = hparams.n_cars
        
        self.targets = []
        self.image_links = []
        self.targets_dict = {}
        
        pass
            
    def drive(self, n_links) -> int:
        self.driver.execute_script('window.scrollTo(0,0);')

        page_html = self.driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
        # class that points to the containers of the ad page
        containers = pageSoup.findAll('a', {'class':'fnmrjs-0 fyjObc'})

        n_links += len(containers)
        
        
        for container in containers:
            self.targets.append(container.attrs['href'])
            
        return n_links
                
    def loop_drive(self) -> None:
        n_links = len(self.targets)
        
        self.driver.get(self.url)
        n_links = self.drive(n_links)
        
        while n_links < self.max:
            # XPATH that contains the buttom to the next page
            self.driver.find_element(By.XPATH, """//*[@id="listing-main-content-slot"]/div[12]/div/div/div[2]/div/div[1]/div/a""")
            n_links = self.drive(n_links)
        print(f'Found {n_links} unique cars on sale')
            
    def scraper(self) -> None:
        if DEBUG: self.targets = self.targets[:self.max]
        for link in self.targets:
            self.driver.get(link)
            
            page_html = self.driver.page_source
            pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
            ### class that contains the image source
            images = pageSoup.findAll('img', {'class':'image'})
            
            for image in images:
                ### atribute of the image that contains the source
                image = image.attrs['src']
                #image = f'{str(image[:-5])}.{self.fmt}'
                self.image_links.append(image)
            
            self.targets_dict[link] = [i for i in self.image_links]
        self.driver.close()
                
        print(f"A total of {len(self.image_links)} images was found.")
        
    def downloader(self) -> None:
        path = os.path.join(self.output_path, self.name)

        try:
           os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        with open(os.path.join(path, f'{self.prefix[:-1]}.json'), 'w') as fp:
            json.dump(self.targets_dict, fp)
         
        for i, link in enumerate(self.image_links):
            
            # How to make this loop use multiprocessing?
            
            req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            with open(os.path.join(path, f"olx_{self.prefix}{i:04d}.jpg"), 'wb') as f:
                f.write(webpage)    
           
        print('done!')
        
    @staticmethod
    def add_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser])

        parser.add_argument('--url', type=str, required=True)
        parser.add_argument('--name', type=str, required=True)
        parser.add_argument('--output', type=str, required=True)
        parser.add_argument('--n_cars', type=int, default=200)   
        parser.add_argument('--prefix', type=str)
        
        return parser
    

def main(hparams):
    scrap = Scraper(hparams)
    scrap.loop_drive()
    scrap.scraper()
    scrap.downloader()
    
if __name__ == '__main__':
    parent_parser = ArgumentParser(add_help=False)

    parser = Scraper.add_args(parent_parser)
    hparams = parser.parse_args()
    
    main(hparams)