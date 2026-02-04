# Azure OpenAI Chatbot on Azure Container Apps
Purpose: A minimal two‑service chatbot where a public Streamlit frontend calls a private FastAPI backend that invokes Azure OpenAI; secrets are read from Key Vault at runtime and container images are pulled from ACR using managed identities

## Features
Public frontend, private backend: The frontend exposes external ingress (public HTTPS) while the backend uses internal ingress (only reachable inside the Container Apps environment).
Service‑to‑service calls inside the environment: The frontend can call the backend by its URL:  http://backend-app. Traffic never leaves the environment.
Secrets with Key Vault + Managed Identity: The backend reads the Azure OpenAI API key at runtime using a system‑assigned managed identity granted Key Vault Secrets User RBAC on the vault (no secrets in code or app settings).
Image pulls without passwords: Both apps pull images from ACR using their managed identities assigned the AcrPull built‑in role; registry credentials aren’t stored with the app.
Azure OpenAI via the SDK: The backend uses the OpenAI Python SDK against Azure’s deployment endpoint and passes an explicit api‑version for the data‑plane.
Network isolation: The environment is VNet‑integrated; Key Vault uses a Private Endpoint and Private DNS (privatelink.vaultcore.azure.net) so calls stay on the Microsoft backbone.

Architecture (summary)

Azure Container Apps Environment (External) in a VNet. 
Subnet hosts two apps:
- frontend-app (Streamlit) with external ingress on 443.
- backend-app (FastAPI) with internal ingress (no public endpoint).

Frontend connection with Backend: http://backend-app remains inside the environment.
Key Vault: Private Endpoint + Private DNS; backend’s managed identity has Key Vault Secrets User.
ACR: Both app's identities have AcrPull on the registry; apps are configured to use Managed identity authentication for pulls.
Azure OpenAI: Backend calls the model deployment via Azure’s data‑plane endpoint with api-version.
