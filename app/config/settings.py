import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")   # deployment name

    base_url = f"{endpoint}/openai/deployments/{deployment}"

    return {
        "config_list": [{
            "model": deployment,         # Deployment name, required by Azure
            "api_key": api_key,
            "base_url": base_url,
            "default_query": {
                "api-version": api_version
            }
        }],
        "temperature": float(os.getenv("APP_TEMPERATURE", 0.2)),
    }


def get_runtime_config():
    return {
        "work_dir": os.getenv("APP_WORK_DIR", "./workspace"),
        "default_market": os.getenv("DEFAULT_MARKET", "IN")
    }