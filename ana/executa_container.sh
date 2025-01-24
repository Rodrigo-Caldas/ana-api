#!/bin/bash

### Executa o serviço de coleta de dados no container ###

micromamba run --name ana-api python -m ana

echo "Liberando permissão do diretório /home/dados.."

chmod -R 777 dados

echo "Permissões alteradas."
