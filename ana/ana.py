"""Funções relacionadas a API da ANA."""

import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

import httpx
import pandas as pd

from ana.config import config
from ana.loggit import log


def requisitar_inventario() -> ET.Element:
    """
    Requisita o inventário das estações pluviométricas da ANA.

    Returns
    -------
    ET.Element
        Raiz do XML da requisição.
    """
    log.info("Requisitando inventário ANA..")

    try:
        tipo_estacao = 2
        codigo = ""
        telemetrica = ""
        url_requisicao = (
            f"{config.url_base}/HidroInventario?codEstDE={codigo}&codEstATE=&tpEst={tipo_estacao}"
            f"&nmEst=&nmRio=&codSubBacia=&codBacia=&nmMunicipio=&nmEstado=&sgResp=&sgOper=&"
            f"telemetrica={telemetrica}"
        )

        resposta = httpx.get(url_requisicao, timeout=None)
        conteudo = resposta.content
        conteudo_et = ET.fromstring(conteudo)
        arvore = ET.ElementTree(conteudo_et)
        raiz = arvore.getroot()
        log.info("[bright_green]Requisição do inventário com sucesso!")

    except Exception as e:
        log.info(f"[bright_red]Falha na requisição do inventário: {e}")
        raise e

    return raiz


def parsear_inventario_xml(
    raiz: ET.Element, lista_ana: List[str] = config.lista_ana
) -> List[Dict[str, Any]]:
    """
    Parseia os elementos XML da requisição de inventario.

    Parameters
    ----------
    raiz : ET.Element
        Raiz da requisição.
    lista_ana : List[str], optional
        Lista com os parâmetros que queremos buscar, by default config.lista_ana.

    Returns
    -------
    List[Dict[str, Any]]
        Lista de dicionário com os parâmetros que buscamos.
    """
    lista = []

    for i in raiz.iter("Table"):
        dados_estacao = {}
        for variavel in lista_ana:
            nova_variavel = i.find(variavel)
            if nova_variavel is not None:
                dados_estacao.update({variavel: nova_variavel.text})
        lista.append(dados_estacao)

    return lista


def mostrar_inventario() -> pd.DataFrame:
    """
    Apresenta o inventário completo de estações pluviométricas da ANA.

    Returns
    -------
    pd.DataFrame
        DataFrame com o inventário da ANA.
    """
    raiz = requisitar_inventario()
    dados = parsear_inventario_xml(raiz)
    df_inventario = pd.DataFrame(dados)

    df_inventario = df_inventario.set_axis(
        [
            "latitude",
            "longitude",
            "altitude",
            "codigo",
            "nome",
            "subbacia",
            "bacia",
            "estado",
            "tipo_de_estacao",
            "telemetrica",
            "operando",
        ],
        axis="columns",
    )

    convert_dict = {
        "latitude": float,
        "longitude": float,
        "altitude": float,
        "codigo": "string",
        "nome": "string",
        "subbacia": "string",
        "bacia": "string",
        "estado": "string",
        "tipo_de_estacao": "string",
        "telemetrica": "string",
        "operando": "string",
    }

    df_inventario = df_inventario.astype(convert_dict)
    df_inventario["nome"] = df_inventario["nome"].str.lower()
    df_inventario["estado"] = df_inventario["estado"].str.lower()

    df_inventario = (
        df_inventario.replace({"tipo_de_estacao": {"2": "pluviômetro"}})
        .replace({"telemetrica": {"0": "não"}})
        .replace({"telemetrica": {"1": "sim"}})
        .replace({"operando": {"0": "não"}})
        .replace({"operando": {"1": "sim"}})
    )

    df_inventario = df_inventario.drop_duplicates()

    return df_inventario


def requisitar_serie(codigo: str, data_inicio: str, data_fim: str = "") -> ET.Element:
    """
    Requisita a série de dados meteorológicos de uma estação.

    Parameters
    ----------
    codigo : str
        Código da estação.
    data_inicio : str
        Data de início da requisição.
    data_fim : str, optional
        Data final da requisição dos dados, by default "".

    Returns
    -------
    ET.Element
        Raiz do XML da requisição.
    """
    url_requisicao = (
        f"{config.url_base}/DadosHidrometeorologicos?codEstacao={codigo}"
        f"&dataInicio={data_inicio}&dataFim={data_fim}"
    )

    resposta = httpx.get(url_requisicao)
    conteudo = resposta.content
    conteudo_et = ET.fromstring(conteudo)
    arvore = ET.ElementTree(conteudo_et)
    raiz = arvore.getroot()

    return raiz


def parsear_serie_xml(raiz: ET.Element) -> pd.DataFrame:
    """
    Parseia os elementos XML da requisição da serie.

    Parameters
    ----------
    raiz : ET.Element
        Raiz do XML da requisição.

    Returns
    -------
    pd.DataFrame
        DataFrame contendo a data, nº da estação e a chuva.
    """
    serie = pd.DataFrame()

    for i, item in enumerate(raiz.iter("DadosHidrometereologicos"), 1):
        data = item.find("DataHora")
        cod_estacao = item.find("CodEstacao")
        chuva = item.find("Chuva")

        if (data is not None) and (cod_estacao is not None) and (chuva is not None):
            serie.at[i, "data"] = data.text
            serie.at[i, "codigo"] = cod_estacao.text
            serie.at[i, "chuva"] = chuva.text

    return serie


def transformar_csv(df: pd.DataFrame, codigo: str, caminho_csv: Path) -> None:
    """
    Transforma o DataFrame dos dados meteorológicos em csv.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contendo os dados gerais das estações.
    codigo : str
        Código da estação.
    caminho_csv : Path
        Caminho onde os dados csv serão guardados.
    """
    df["data"] = pd.to_datetime(df["data"])
    df = df.astype({"chuva": "float", "codigo": "int"})

    df2 = df.resample("h", on="data").sum(numeric_only=True)
    df2.reset_index(inplace=True)
    df2["hora"] = pd.to_datetime(df2["data"])
    df2["data"] = df2["data"].dt.normalize()
    df2.iloc[0::, 1] = df.iloc[0, 1]

    df2.to_csv(f"{caminho_csv}/{codigo}.csv")


async def obter_chuva(
    codigo: str, caminho_csv, data_inicio: str, data_fim: str = ""
) -> None:
    """
    Busca os dados de chuva de uma estação de maneira assíncrona e salva em csv.

    Parameters
    ----------
    codigo : str
        Código da estação.
    caminho_csv : Path
        Caminho onde os dados csv serão guardados.
    data_inicio : str
        Data de início da requisição dos dados.
    data_fim : str, optional
        Data final da requisição dos dados, by default "".
    """
    async with config.limitador_tarefas:
        async with httpx.AsyncClient() as cliente:
            url_requisicao = (
                f"{config.url_base}/DadosHidrometeorologicos?codEstacao={codigo}"
                f"&dataInicio={data_inicio}&dataFim={data_fim}"
            )

            try:
                await asyncio.sleep(2)
                resposta = await cliente.get(url_requisicao, timeout=None)

                while resposta.status_code == 429:
                    await asyncio.sleep(2)
                    log.warning(f"Nova tentativa da estação {codigo}..")
                    resposta = await cliente.get(url_requisicao, timeout=None)

                conteudo = resposta.content
                conteudo_et = ET.fromstring(conteudo)
                arvore = ET.ElementTree(conteudo_et)
                raiz = arvore.getroot()
                df = parsear_serie_xml(raiz)

                if not df.shape[0] > 0 or df["chuva"].isnull().all():
                    log.info(f"Estação {codigo} sem dados!")

                else:
                    transformar_csv(df, codigo, caminho_csv)
                    log.info(f"[bright_green]Estação {codigo} ok!")

            except Exception as e:
                log.error(f"[bright_red]Falha na requisição: {e} {codigo}")
                raise e


async def obter_chuvas(
    estacoes: List[str], caminho_csv: Path, data_inicio: str, data_fim: str = ""
) -> None:
    """
    Busca os dados de chuva de uma lista de estações de maneira assíncrona.

    Parameters
    ----------
    estacoes : List[str]
        Lista com os códigos das estações metereológicas.
    caminho_csv : Path
        Caminho onde os dados csv serão guardados.
    data_inicio : str
        Data de início da requisição dos dados.
    data_fim : str, optional
        Data final da requisição dos dados, by default "".
    """
    agendadas = set()

    for posto in estacoes:
        task = obter_chuva(posto, caminho_csv, data_inicio, data_fim)
        agendadas.add(task)

    await asyncio.gather(*agendadas)
