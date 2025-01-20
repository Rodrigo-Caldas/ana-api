# ANA-API

![texto](https://img.shields.io/static/v1?label=linguagem&message=python&color=green&style=flat-square "linguagem")
![texto](https://img.shields.io/static/v1?label=ambiente&message=docker&color=blue&style=flat-square "linguagem")


Repositório para obtenção de dados pluviomátricos da ANA apartir dos contornos do ONS. Os contornos são respectivamente: bacias e sub-bacias.


## :world_map: Conteúdo
1. [O que faz](#sparkles-o-que-faz)  
2. [Maneiras de executar](#:warning:-pre-requisitos)
3. [Como executar](#arrow_forward-como-executar)
4. [Desenvolvimento](#construction-desenvolvimento)


## :dash: Bacias

![bacias_e_subbacias_targus](imagens/bacias.png?raw=true "Bacias utilizadas do ONS")

## :dash: Sub-bacias

![bacias_e_subbacias_targus](imagens/sub-bacias.png?raw=true "Subbacias utilizadas do ONS")

## :sparkles: O que faz

:heavy_check_mark: Busca os dados dos pluviômetros da ANA a partir do contorno escolhido.

:heavy_check_mark: Os dados são horários e o usuário escolhe o período de busca (ex: 01/01/2019 à 31/12/2019).

:heavy_check_mark: Os dados serão salvos no formato CSV na pasta ``dados``.

## :warning: Pré-requisitos

- [Python](https://www.python.org/) (não obrigatório)
- [conda](https://www.anaconda.com/products/individual) (não obrigatório)
- [Docker]


## :arrow_forward: Como executar

A cada nova atualização de contornos pela fonte (ONS), o script deverá ser executado para a atualizar estas informações também no banco de dados e no s3. Certifique-se de que você está com a `AWS CLI` configurada para a conta desejada, `desenvolvimento` ou `produção`.
O passo a passo é descrito a seguir:

### 1. obtendo o shapefile
O contorno original deve ser obtido diretamente do SINTEGRE ou através dos analistas. Por vezes o Operador poderá enviar arquivos no formato .bln. Estes arquivos deverão ser convertidos para shapefile. Um exemplo é dado a seguir:

> Para executar o script abaixo, certifique-se de que o arquivo possui apenas duas colunas, uma com valores do tipo float de longitude e outra, também do tipo float, de latitude. Esta etapa poderá ser modificada de acordo com o arquivo recebido. Remova colunas extras e altere o tipo de coluna de acordo com a necessidade. Usualmente, arquivos bln vem com duas colunas, sendo a primeira longitude e a segunda latitude.

```python
import pandas as pd
from attcontornos.conversores import bln

# leia o arquivo bln.
arquivo_original = pd.read_csv("arquivo-bln.bln", names=["longitude", "latitude"])

# crie uma lista de coordenadas do tipo shapely.geometry.Point
coordenadas = bln.listar_coordenadas(arquivo_original)

# converta a lista de coordenadas para polígono do tipo shapely.geometry.polygon.Polygon
poligono = bln.poligono_de_pontos(coordenadas)

# exporte o polígono como um shapefile. 
# nesta etapa, é possível já passar as propriedades de acordo com o preconizado na seção de padrão de arquivos. A nível didático, neste exemplo apenas exportaremos o shapefile.
bln.exportar_shapefile(poligono, "arquivo-shapefile.shp") 
```

### 2. padronizando o shapefile
O contorno, de extensão shapefile, deve ser formatado de acordo com o seguinte padrão:

##### 2.1. **contornos de subbacias isoladas**
- composto de 1 arquivo por sub-bacia. 
- deverá conter as colunas `subbacia`, `bacia`, `psat`, `subsistema`, `lat`, `lon`, `geometry`, cujos valores deverão estar em gramática correta (sem normalização), exceto pelo `subsistema`, que deverá ser um entre: `seco` (sudeste/centro-oeste), `s` (sul), `ne` (nordeste), `n` (norte).
- o arquivo de cada subbacia deverá ser armazenado dentro da pasta `arquivos/shapefiles/sub-bacias-isoladas/{nome-da-bacia}`.

##### 2.2. **contornos de bacias com subbacias**
- composto de 1 arquivo por bacia.
- deverá conter as mesmas colunas do item 2.1, mas cada arquivo de bacia deverá conter, na tabela de atributos, uma linha por sub-bacia.
- o arquivo de cada bacia deverá ser armazenado dentro da pasta `arquivos/shapefiles/bacias-com-sub-bacias/`.

##### 2.3. **contornos de bacias sem subbacias**
- composto de 1 arquivo por bacia.
- deverá conter as colunas `bacia`, `subsistema`, `geometry`, cujos valores deverão estar em gramática correta (sem normalização), exceto pelo `subsistema`, que deverá ser um entre: `seco` (sudeste/centro-oeste), `s` (sul), `ne` (nordeste), `n` (norte).
- o arquivo de cada bacia deverá ser armazenado dentro da pasta `arquivos/shapefiles/bacias-sem-sub-bacias`.
- o contorno da bacia deverá corresponder à união dos contornos das sub-bacias dentro dela.
> Observação 1: Idealmente, trabalhe com as subbacias primeiro, e construa os arquivos de bacias baseados nas subbacias já trabalhadas. Isso poupa trabalho e garante a consistência entre arquivos. Um exemplo de criação de arquivo de bacias sem subbacias a partir do arquivo com subbacias é demonstrado abaixo.

```python
import geopandas as gpd

# leia o arquivo
gdf = gpd.read_file("arquivo-da-bacia-com-subs.shp")
# dissolva as linhas do geodataframe e exporte para um arquivo sem subs. Este geodataframe deverá conter apenas uma linha e as colunas "bacia" e "geometry". Caso existam outras linhas ou colunas, estas deverão ser removidas.
gdf.dissolve().to_file("arquivo-da-bacia-sem-subs.shp")
```

> Observação 2: para bacias que contém apenas 1 sub-bacia homônima, é possível usar um módulo de CLI dentro deste repositório. Exemplo de uso para a bacia Suíça, que contém a sub-bacia homônima Suíça.

```bash
# considerando que o arquivo original está no caminho "Bacia_Suica.shp"
python -m attcontornos.cli.subbacia_unica --bacia=Suíça --subbacia=Suíça --crs="WGS84" --subsistema=seco --psat=PSATSUIC --caminho_entrada="Bacia_Suica.shp" 
```

### 3. atualizando os contornos existentes

Uma vez que o contorno estiver devidamente formatado, este poderá ser inserido no banco de dados. A inserção pode ser realizada através da execução do script principal deste projeto, que abrange a inserção no banco de dados e no datalake hospedado no AWS S3. Para executar o script, siga os seguintes comandos:
```bash
# 1. entre no diretório do projeto, caso não esteja.
cd contornos

# 2. instale as dependências e ative o ambiente, caso ainda não tenha feito.
bash conda-install.bash
conda activate contornos

# 3. rode o script.
python -m attcontornos
```

Automaticamente, serão atualizados:
- O mapa de bacias armazenado neste repositório
- O arquivo delimitado por texto que elenca os códigos PSAT de cada subbacia, armazenado neste repositório.
- Os documentos do banco de dados de `hidrologia`, localizados nas coleções `bacias-com-subbacias`, `sub-bacias-isoladas` e `bacias-sem-subbacias`
- Os arquivos de contornos no AWS s3, localizados no diretório `hidrologia/contornos/bacias-com-subbacias`, `hidrologia/contornos/sub-bacias-isoladas` e `hidrologia/contornos/bacias-sem-subbacias`
- Assim que os arquivos do s3 forem atualizados, será desencadeado o microserviço `tg-grade-modelos`, que atualiza automaticamente os arquivos referentes ao ponto de grade de cada modelo que caem dentro das bacias e subbacias (localizados em `meteorologia/processados/internos/chuva/previsto/pontos_grade_modelos/`).

O resultado será a atualização dos arquivos do diretório no s3 e banco de dados. Garanta que os contornos estejam atualizados para que outros serviços possam utilizá-los.
Os contornos atualizados são enviados para o diretório `hidrologia/contornos/`, no s3.

### 4. outras etapas
Após a inserção do novo contorno,
- inserir manualmente o [registro do posto](https://github.com/targusenergia/tg-relacao-postos);
- verificar a inserção da [produtibilidade](https://github.com/targusenergia/tg-produtibilidade-att/) através do [webhook-ons](https://github.com/targusenergia/tg-produtibilidade-att/).
- assegurar a existência da bacia na [api de meteorologia](https://github.com/targusenergia/tg-meteorologia-api/).

**fluxo completo**
```mermaidflowchart LR
    subgraph banco de hidrologia
    bdhidrocontornos[(bacias\nbacias.subbacias\nbacias.subbacias.fracoes\nsubbacias\n)]
    bdhidropostos[(postos)]
    bdhidroprodutibilidade[(produtibilidade)]
    end
    subgraph banco de geodados
    bdgeodados[(estados)]
    end
    subgraph "AWS s3: tgprodutos-{ambiente}/hidrologia/contornos"
    awss3[(bacias-com-subbacias\nbacias-sem-subbacias\nsub-bacias-isoladas)]
    end
    subgraph api de meteorologia
     N[tg-meteorologia-api] --> O[services.contornos.ordem_das_bacias]
    end

    A([Usuário]) -- Dados gerais do processo de previsão de vazões --> C[tg-contornos]
    A --> N
    A -- Série histórica de vazões: *.pdf --> I[tg-relacao-postos] 
    J([Webhook ONS]) -- Relatório preliminar consistido de vazões semanais --> L[tg-produtibilidade-att]
    
    C --> bdhidrocontornos
    C --> bdgeodados
    C --> awss3
    I --> bdhidropostos
    L --> bdhidroprodutibilidade 
    awss3 --> M[tg-grade-modelos]
```

## :construction: Desenvolvimento

### :snake: Preparação do ambiente

> Com Anaconda, não há distinção entre dependências dev e prod.

```bash
# 1. entre no diretório do projeto
cd contornos

# 2. crie o ambiente virtual do projeto
bash conda-install.bash

# 3. ative o ambiente
conda activate contornos
```

### :rotating_light: Como rodar os testes

O serviço ainda não possui testes unitários.