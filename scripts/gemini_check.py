# scripts/azure_check.py
import os
from openai import OpenAI

api_key = os.getenv("mxobY4fiJ9MbGOHNxTm4s1GhBBaiHLtPythqoG21u0iMOecD8nkUJQQJ99BAACHrzpqXJ3w3AAABACOGDTVW")
base_url = os.getenv("https://agenticaiuniliver.openai.azure.com/")  # https://{resource}.openai.azure.com/openai/v1/
deployment = os.getenv("gpt-4o")   # your deployment name

print("BASE_URL:", base_url)
print("DEPLOYMENT:", deployment)
print("Has KEY:", bool(api_key))

client = OpenAI(api_key=api_key, base_url=base_url)
resp = client.chat.completions.create(
    model=deployment,   # deployment name
    messages=[{"role": "user", "content": "Say hello from Azure OpenAI."}],
    max_tokens=16,
)
print("OK:", resp.choices[0].message)