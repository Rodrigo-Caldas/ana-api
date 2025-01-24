FROM mambaorg/micromamba:latest

WORKDIR /home

COPY ana ana
COPY mapas mapas
COPY requirements.yaml .

VOLUME ["/home/dados"]

USER root

RUN chmod +x /home/ana/executa_container.sh
RUN micromamba env create -f requirements.yaml && micromamba clean --all --yes
RUN echo "micromamba activate ana-api" >> ~/.bashrc

CMD ["./ana/executa_container.sh"]
