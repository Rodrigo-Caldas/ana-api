"""Módulo principal da aplicação src."""

import asyncio

import geopandas as gpd

from ana import ana, utils
from ana.loggit import console


def handler(data_inicio: str = "01-01-2019", data_fim: str = "") -> None:
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
    shp_agua_vermelha = gpd.read_file(
        "Mapas/sub-bacias-isoladas/grande/agua_vermelha.shp"
    )

    df_inventario = ana.mostrar_inventario()
    gdf_inventario_filtrado = utils.filtrar_postos_da_bacia(
        df_inventario, shp_agua_vermelha
    )

    # gdf_codigos = gdf_inventario_filtrado[gdf_inventario_filtrado["operando"] == "sim"]
    lista_codigo = gdf_inventario_filtrado["codigo"].tolist()

    asyncio.run(ana.obter_chuvas(lista_codigo, data_inicio, data_fim))

    console.rule("Fim do serviço!")


if __name__ == "__main__":

    handler()
