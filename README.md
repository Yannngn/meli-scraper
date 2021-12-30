# meli-scraper

[en-EN]

A simple image scraper for Mercado Libre and OLX (Brazil) using Selenium, URLlib and Beautiful Soup

[pt-BR]

Scraper simples para Mercado Livre e OLX usando Selenium, URLLib e Beautiful Soup

## Usage
### Example cmd:

```
python main.py --site {site} --name {name} -maker {make} --year 2022 --output {output_path}
```

## Commands

[en-EN]

The ```--site``` option of the site to be searched, ```'meli'```, ```'olx'``` or ```'both'```. [Required] \
The ```--name``` name of the product, is also used to create the download directory and the prefix of every image. [Required] \
The ```--maker``` maker of the product, is also used to create the download directory and the prefix of every image. [Required] \
The ```--year``` year of the product, used to create the prefix of every image. [Required] \
The ```--output``` must be followed by the desired parent folder that will contain the download directory. [Required] \
The ```--folder``` superseeds the default one (which is made from the name and maker). \
The ```--prefix``` is used to name every single image downloaded, superseeds the default one (which is made from the name, maker and year). \
The ```--n_cars``` is the number of cars that the bot will search, if the opened page of the site has more cars than needed it will still be downloaded, but no futher pages will be searched [Optional - Default: 200]. \
The --fmt is the desired format of the images.



