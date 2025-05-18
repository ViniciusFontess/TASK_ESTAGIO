# imports necessários

import requests
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import torch
import warnings
from bs4 import BeautifulSoup
import time
import json
import base64        
import io             

warnings.filterwarnings("ignore", category=FutureWarning)

print("Iniciando a avaliação técnica...") #teste 

# inicialização básica

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
MODEL_NAME = "microsoft/Florence-2-large"
AUTH_TOKEN = "dyoFzEmiEqKa9CzY3SUWR7Sytb2rw8Ph"  # senha do e-mail
MAX_REQUESTS = 50
REQUEST_COUNT = 0

SCRAPE_URL = "https://intern.aiaxuropenings.com/scrape/575889b1-f4c3-4ece-899e-b2a997d9579b" #imagem de teste
API_MODEL_URL = "https://intern.aiaxuropenings.com/v1/chat/completions"
API_SUBMIT_URL = "https://intern.aiaxuropenings.com/api/submit-response" 

# URL pdo modelo
# URL para submeter resposta



# tentar executar o modelo
# e fazer scraping da imagem
try:
    print(f"Usando dispositivo: {DEVICE}")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=TORCH_DTYPE, trust_remote_code=True
    ).to(DEVICE)
    processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
    print(f"Modelo carregado em {time.time() - t0:.2f}s")
except Exception as e:
    print(f"Erro crítico ao carregar o modelo: {e}")
    print("Verifique conexão e o nome do modelo.")
    exit(1)


# função para fazer requisições à API
def make_api_request(url, headers, data, method="POST"):
    global REQUEST_COUNT
    if REQUEST_COUNT >= MAX_REQUESTS:
        raise RuntimeError("Limite de requisições atingido")

    print(f"\nRequisição {REQUEST_COUNT+1}/{MAX_REQUESTS} -> {url}")
    REQUEST_COUNT += 1
    try:
        if method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            resp = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {resp.status_code}")
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"Erro na requisição: {e}")
        raise

# função para fazer scraping da imagem 
# e fazer download (usando BeautifulSoup)
# e requests 
def scrape_and_download_image(page_url):
    print(f"\nFazendo scraping em: {page_url}")
    resp = requests.get(page_url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    img = soup.find("img")
    if not img or not img.get("src"):
        raise RuntimeError("Imagem não encontrada no HTML")
    img_url = img["src"]
    print("URL da imagem:", img_url[:100], "…")

    if img_url.startswith("data:image"):
        header, b64 = img_url.split(",", 1)
        img_data = base64.b64decode(b64)
        return Image.open(io.BytesIO(img_data))
    else:
        resp2 = requests.get(img_url, stream=True, timeout=15)
        resp2.raise_for_status()
        return Image.open(resp2.raw)

# função para converter imagem para base64
def image_to_base64(pil_img, fmt="PNG"):
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    # converte corretamente em base64
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# função para rodar tudo
def run():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1) Scraping e download da imagem
    img = scrape_and_download_image(SCRAPE_URL)

    # 2) Preparar payload no padrão OpenAI para imagem + prompt
    prompt = "<DETAILED_CAPTION>"
    b64 = image_to_base64(img, fmt="PNG")
    payload_model = {
        "model": "microsoft-florence-2-large",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }
        ],
        "max_tokens": 1024
    }

    # 3) Inferência via API do modelo
    resp_model = make_api_request(API_MODEL_URL, headers, payload_model)
    model_json = resp_model.json()
    print("\nResposta do modelo:", json.dumps(model_json, indent=2))

    # 4) Submissão da resposta bruta
    resp_submit = make_api_request(API_SUBMIT_URL, headers, model_json)
    print("\nStatus de submissão:", resp_submit.status_code)
    try:
        print("Corpo de resposta:", json.dumps(resp_submit.json(), indent=2))
    except:
        print("Resposta não é JSON:", resp_submit.text)

    print(f"\nTotal requisições: {REQUEST_COUNT}/{MAX_REQUESTS}")


if __name__ == "__main__":
    run()