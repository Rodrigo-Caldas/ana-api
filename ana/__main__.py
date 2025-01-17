"""Módulo principal da aplicação src."""

import asyncio
from pathlib import Path

import geopandas as gpd

from ana import ana, utils
from ana.config import config
from TCC.ana.logit import console


async def handler(data_inicio: str = "01-01-2019", data_fim: str = "") -> None:
    """
    Execução do serviço de coleta da chuva horária dos postos em operação da ANA.

    Parameters
    ----------
    data_inicio : str, optional
        Data de início da requisição dos dados, by default '01-01-2019'.
    data_fim : str, optional
        Data final da requisição dos dados, by default "".
    """
    console.rule("Iniciando serviço de coleta de chuva horária da ANA.")

    df_inventario = ana.mostrar_inventario()

    caminho_base = Path("mapas", "sub-bacias-isoladas")
    caminhos = list(caminho_base.rglob("*.shp"))

    for bacia in caminhos:
        console.rule(f"Obtendo dados de {bacia.name}")

        caminho_csv = Path(config.diretorio_dados, bacia.name)
        caminho_csv.mkdir(parents=True, exist_ok=True)

        shp = gpd.read_file(bacia)
        gdf_inventario_filtrado = utils.filtrar_postos_da_bacia(df_inventario, shp)

        lista_codigo = gdf_inventario_filtrado["codigo"].tolist()

        await ana.obter_chuvas(lista_codigo, caminho_csv, data_inicio, data_fim)

    console.rule("Fim do serviço!")


if __name__ == "__main__":

    asyncio.run(handler())
