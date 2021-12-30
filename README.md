# meli-scraper

[en-EN]

A simple image scraper for Mercado Libre and OLX (Brazil) using Selenium, URLlib and Beautiful Soup

[pt-BR]

Scraper simples para Mercado Livre e OLX usando Selenium, URLLib e Beautiful Soup

## Usage
### OLX
**Example cmd**:

```
python olx.py --url https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{car}/{manufacturer}/{year}?q={car} --name {manufacturer}_{car} --prefix {manufacturer}_{car}_{year} --output {output_path}
```

**Example link**:

https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/argo/fiat/2022?q=argo

### MeLi
**Example cmd**:
```
python meli.py --url https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes/{car}_YearRange_{year}-{year} --name fiat_argo --name {manufacturer}_{car} --prefix {manufacturer}_{car}_{year} --output {output_path}
```
**Example link**:
https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes/argo_YearRange_2022-2022

## Commands

The ```--name``` parameter is utilized to create the download directory and to filter the results (They have to contain the manufacturer and car in the title {manufaturer}_{car}). [Required] \
The ```--prefix``` is used to name every single image downloaded. [Required] \
The ```--output``` must be followed by the desired parent folder that will contain the download directory. [Required] \
The ```--n_cars``` is the number of cars that the bot will search, if the opened page of the site has more cars than needed it will still be downloaded, but no futher pages will be searched [Optional - Default: 200] \
The --fmt is the desired format of the images [Only for Mercado Libre] [Optional - Default: 'jpg']



