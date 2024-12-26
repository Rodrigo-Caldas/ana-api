"""Configurações do serviço ana."""

import asyncio
from typing import List

from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    """Configurações e parâmetros do serviço."""

    url_base: str = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx"
    lista_ana: List[str] = [
        "Latitude",
        "Longitude",
        "Altitude",
        "Codigo",
        "Nome",
        "BaciaCodigo",
        "SubBaciaCodigo",
        "nmEstado",
        "TipoEstacao",
        "TipoEstacaoTelemetrica",
        "Operando",
    ]
    limitador_tarefas: asyncio.Semaphore = asyncio.Semaphore(5)

config = Configuracoes()