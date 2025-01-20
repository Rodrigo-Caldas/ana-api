"""Módulo principal da aplicação src."""

import asyncio
from pathlib import Path

import geopandas as gpd

from ana import ana, utils
from ana.config import config
from ana.logit import console


async def handler(
    data_inicio: str = "01-01-2024",
    data_fim: str = "",
    caminho_contorno: Path = Path(
        "mapas", "sub-bacias-isoladas", "paranapanema", "capivara.shp"
    ),
) -> None:
    """
    Execução do serviço de coleta da chuva horária dos postos em operação da ANA.

    Parameters
    ----------
    data_inicio : str, optional
        Data de início da requisição dos dados, by default '01-01-2024'.
    data_fim : str, optional
        Data final da requisição dos dados, by default "".
    caminho_contorno : Path, optional
        Caminho do shapefile ou do diretório contendo shapefiles, by default Path("mapas", "sub-bacias-isoladas", "grande", "agua_vermelha.shp").
    """
    console.rule("Iniciando serviço de coleta de chuva horária da ANA.")

    df_inventario = ana.mostrar_inventario()

    if caminho_contorno.is_file():
        caminhos = []
        caminhos.append(caminho_contorno)

    elif caminho_contorno.is_dir():
        caminhos = list(caminho_contorno.rglob("*.shp"))

    for shp in caminhos:
        console.rule(f"Obtendo dados de {shp.name}")

        caminho_csv = Path(config.diretorio_dados, shp.name)
        caminho_csv.mkdir(parents=True, exist_ok=True)

        gdf = gpd.read_file(shp)
        gdf_inventario_filtrado = utils.filtrar_postos_da_bacia(df_inventario, gdf)

        lista_codigo = gdf_inventario_filtrado["codigo"].tolist()

        await ana.obter_chuvas(lista_codigo, caminho_csv, data_inicio, data_fim)

    console.rule("Fim do serviço!")


if __name__ == "__main__":

    asyncio.run(handler())
