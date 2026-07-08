import os
import json

CONFIG_PATH = "config.json"



def salvar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def carregar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"planilha": "", "pasta_raiz": ""}