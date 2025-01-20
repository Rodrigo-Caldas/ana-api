# ANA-API

![texto](https://img.shields.io/static/v1?label=linguagem&message=python&color=green&style=flat-square "linguagem")
![texto](https://img.shields.io/static/v1?label=ambiente&message=docker&color=blue&style=flat-square "linguagem")


Repositório para obtenção de dados pluviomátricos da ANA apartir dos contornos do ONS. Os contornos são respectivamente: bacias e sub-bacias.


## :world_map: Conteúdo
1. [O que faz](#sparkles-o-que-faz)  
2. [Como executar](#arrow_forward-como-executar) 
3. [Mamba-Conda](#snake-mamba-conda)
4. [Docker](#whale-docker)


## :dash: Bacias

![bacias_e_subbacias_targus](imagens/bacias.png?raw=true "Bacias utilizadas do ONS")

## :dash: Sub-bacias

![bacias_e_subbacias_targus](imagens/sub-bacias.png?raw=true "Subbacias utilizadas do ONS")

## :sparkles: O que faz

:heavy_check_mark: Busca os dados dos pluviômetros da ANA a partir do contorno escolhido.

:heavy_check_mark: Os dados são horários e o usuário escolhe o período de busca (ex: 01/01/2019 à 31/12/2019).

:heavy_check_mark: Os dados serão salvos no formato CSV na pasta ``dados``.

## :warning: Como executar

Há duas maneiras de executar este repositório, utilizando conda/mamba ou docker.

- [Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
- [Docker](https://docs.docker.com/engine/install/)

## :snake: Mamba/Conda

## :whale: Docker