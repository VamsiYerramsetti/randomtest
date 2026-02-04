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

Architecture (summary)
The two main components of the chatbot—the frontend (Streamlit) and backend (FastAPI)—run in separate Azure Container Apps inside the same VNet‑integrated Container Apps Environment. 
The frontend exposes external ingress for a public HTTPS URL, while the backend uses internal ingress so it’s reachable only from within the environment. 

I began by creating the environment with my own VNet/subnet, then pushed both images to Azure Container Registry (ACR) and enabled system‑assigned managed identities on each app, those identities were granted the AcrPull role at the registry scope so the apps can pull images without stored credentials. 

Secrets are centralized in Azure Key Vault. I added a Private Endpoint and linked the privatelink.vaultcore.azure.net Private DNS zone to the VNet so runtime secret access stays private, then assigned the backend app’s managed identity the Key Vault Secrets User role to read the OpenAI API key at runtime. 

In the code, the frontend reads BACKEND_URL from an environment variable and issues a simple POST to /chat with the user’s message; the backend exposes /chat via FastAPI, uses DefaultAzureCredential with SecretClient to fetch AZURE_OPENAI_API_KEY from Key Vault, and constructs the OpenAI Python SDK client with base_url and api-version, then calls Chat Completions and returns the assistant’s text. For service‑to‑service networking, the frontend calls the backend by http://backend-app, keeping traffic inside the environment. Ingress at the environment edge terminates TLS and routes requests to the correct app. Operationally, I ship changes by building new images, tagging them (for example, moving from :1.0 to :2.0), pushing to ACR, and creating a new Container Apps revision per service that points at the new tag; this gives clean rollouts, optional canary traffic splitting, and instant rollback by shifting traffic back to the previous revision.
For a better understanding of the arcitecture please check out the diagram.

Azure Container Apps Environment (External) in a VNet. 
- frontend-app (Streamlit) with external ingress on 443.
- backend-app (FastAPI) with internal ingress (no public endpoint).

Frontend connection with Backend: http://backend-app remains inside the environment.
Key Vault: Private Endpoint + Private DNS; backend’s managed identity has Key Vault Secrets User.
ACR: Both app's identities have AcrPull on the registry; apps are configured to use Managed identity authentication for pulls.
Azure OpenAI: Backend calls the model deployment via Azure’s data‑plane endpoint with api-version.
