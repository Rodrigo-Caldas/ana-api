FROM mambaorg/micromamba:latest

WORKDIR /home

COPY ana ana
COPY requirements.yaml .


