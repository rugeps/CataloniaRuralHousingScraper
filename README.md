# Catalonia Rural Housing Web Scraping

# Pràctica 1: Web scraping

## Descripció

Aquesta pràctica forma part de la asignatura _Tipología y cicle de vida de los dates_, dal *Màster en Ciència de Dades* de la *[Universitat Oberta de Catalunya](https://www.uoc.edu/)*. S'apliquen tècniques de _web scraping_ mitjançant el llenguatge de programació Python per extreure dades de la web [_EscapadaRural_](https://www.escapadarural.com/) i generar un _dataset_.

## Membres de l'equip

* **Roger Peris Serrano** - *Estudiant* - [UOC](https://www.uoc.edu)
* **Albert Cámara Viñals** - *Estudiant* - [UOC](https://www.uoc.edu)

## Contingut del repositori

* **src/:** (scripts en Python)
* **data/:** (dataset)
* **docs/:** (documentació del projecte i respostes a les preguntes de la pràctica)

## Començant

### Prerequisits

Per executar l'script *"webscraping.py"* són necesàries les següents dependències:

* Requests
* BeautifulSoup
* Builtwith
* Whois

Aquestes dependències es poden instal·lar amb les següents comandes

```python
pip install requests
pip install beautifulsoup4
pip install python-whois
pip install builtwith
```

### Instal·lació i ús

Clonar el repositori, accedir al directori i executar l'script *"webscraping.py"*.

```python
git clone git@github.com:rugeps/CataloniaRuralHousingScraper.git
cd cd CataloniaRuralHousingScraper/src/
python webscraping.py 
```

Aquest script està preparat per buscar i extreure dades de la web [_EscapadaRural_](https://www.escapadarural.com/) i generar un _dataset_. Una vegada finalitzi l'execució al directori *data* podrem trobar un *CSV* 'catalonia_rural_houses_*timestamp*.csv', amb totes les dades extretes.  

## Dataset

El dataset generat es troba publicat a Zenodo (DOI: 10.5281/zenodo.4164777), i es pot consultar a: 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4164777.svg)](https://doi.org/10.5281/zenodo.4164777)

## Llicencia: 

Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
