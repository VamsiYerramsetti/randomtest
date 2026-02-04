# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import OpenAI

app = FastAPI()

# ---- Config via env vars (set in Container Apps) ----
KEYVAULT_URI = os.getenv("KEYVAULT_URI")  # e.g., https://kv-aca-chat.vault.azure.net/
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://<resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")  # e.g., gpt-4o-mini
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

# ---- Create Azure credentials (enable VS Code + interactive for local dev) ----
credential = DefaultAzureCredential(
    exclude_visual_studio_code_credential=False,
    exclude_interactive_browser_credential=False
)  # order described in docs; enabling VS Code & browser aids local dev. [11](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python)

# ---- Key Vault client ----
if not KEYVAULT_URI:
    raise RuntimeError("KEYVAULT_URI is not set.")
kv_client = SecretClient(vault_url=KEYVAULT_URI, credential=credential)  # [13](https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python)

def get_aoai_key():
    # Read secret at runtime
    secret = kv_client.get_secret("AZURE_OPENAI_API_KEY")  # name you created in Key Vault
    return secret.value  # [13](https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        api_key = get_aoai_key()

        # Configure OpenAI SDK for Azure endpoint & deployment
        client = OpenAI(
            api_key=api_key,
            base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}",
            # Azure uses api-version as a query param:
            default_query={"api-version": AZURE_OPENAI_API_VERSION},
        )  # path & versioning per Azure OpenAI data-plane reference. [8](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference?view=foundry-classic)

        completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,  # deployment name (not the raw model slug)
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": req.message},
            ],
            temperature=0.2,
        )  # GPT‑4o‑mini supported on chat completions. [8](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference?view=foundry-classic)[1](https://azure.microsoft.com/en-us/blog/openais-fastest-model-gpt-4o-mini-is-now-available-on-azure-ai/)

        answer = completion.choices[0].message["content"]
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))