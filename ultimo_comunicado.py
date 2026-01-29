# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 17:42:06 2026

@author: Luis
"""

####################
import requests
from pydantic import BaseModel
import pandas as pd
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Suas classes e funções de limpeza (mantidas) ---
from pydantic import BaseModel, Field
from typing import List, Optional

class AtaDetalhe(BaseModel):
    # Usamos alias para converter o 'nro_reuniao' do JSON para o padrão Python
    nroReuniao: int = Field(alias="nro_reuniao")
    dataReferencia: str
    titulo: str
    textoComunicado: Optional[str] = None

    class Config:
        # Permite que você popule a classe usando tanto 'nro_reuniao' quanto 'nroReuniao'
        populate_by_name = True

class RespostaCopom(BaseModel):
    conteudo: List[AtaDetalhe]
class Ata(BaseModel):
    conteudo: list[AtaDetalhe]

def limpar_html(html):
    if not html: return ""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(separator=" ", strip=True)
    texto = re.sub(r"\s+", " ", texto)
    return texto

# --- Função de processamento individual ---

try:
    url_ata_detalhe = "https://www.bcb.gov.br/api/servico/sitebcb/copom/comunicados?quantidade=1"

    response = requests.get(url_ata_detalhe,  timeout=15)
    response.raise_for_status()
    text = response.json()
    ultima_reuniao=text["conteudo"][0]["nro_reuniao"]

except:
    print("erro ao descobrir a ultima reunião, Input manualmente:")
    ultima_reuniao=input()
    ultima_reuniao=int(ultima_reuniao)



def baixar_ata(nro_reuniao):
    url_ata_detalhe = f"https://www.bcb.gov.br/api/servico/sitebcb/copom/comunicados_detalhes?nro_reuniao={nro_reuniao}"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url_ata_detalhe, headers=headers, timeout=15)
        response.raise_for_status()
        
        text = response.json()
        if not text.get("conteudo"):
            return None, nro_reuniao, "Sem conteúdo"

        textoAta = text["conteudo"][0]["textoComunicado"]
        dataPublicacao = text["conteudo"][0]["dataReferencia"]
        
        textos_limpos = limpar_html(textoAta)
        
        titulo=text["conteudo"][0]["titulo"]
        return {
            "reuniao": nro_reuniao,
            "titulo": titulo,
            "data_publi": dataPublicacao, 
            "texto": textos_limpos
        }, None, None
        
    except Exception as e:
        return None, nro_reuniao, str(e)

        
        
        
comunicado_atual=baixar_ata(ultima_reuniao)[0]
