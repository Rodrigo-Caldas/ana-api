"""Funções de utilidades."""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def filtrar_postos_da_bacia(
    df: pd.DataFrame, shp: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Filtra os postos do inventário a partir do contorno shapefile desejado.

    Parameters
    ----------
    df : pd.Dataframe
        Dataframe do inventário ANA, vinda da função obter_inventario().
    shp : gpd.GeoDataFrame
        Contorno desejado.

    Returns
    -------
    gpd.GeoDataFrame
        Postos que estão dentro do contorno.
    """
    df_inventario = df.copy()

    geometria = [
        Point(xy) for xy in zip(df_inventario["longitude"], df_inventario["latitude"])
    ]
    gdf_inventario = gpd.GeoDataFrame(
        df_inventario, geometry=geometria, crs="EPSG:4326"
    )

    if shp.crs != gdf_inventario.crs:
        shp = shp.set_crs(gdf_inventario.crs, allow_override=True)

    gdf_inventario = gdf_inventario[
        gdf_inventario.geometry.within(shp.geometry.union_all())
    ]

    return gdf_inventario
