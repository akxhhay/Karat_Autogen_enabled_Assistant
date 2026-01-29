from openai import AzureOpenAI
print(
    AzureOpenAI(
        api_key="mxobY4fiJ9MbGOHNxTm4s1GhBBaiHLtPythqoG21u0iMOecD8nkUJQQJ99BAACHrzpqXJ3w3AAABACOGDTVW",
        azure_endpoint="https://agenticaiuniliver.openai.azure.com/",
        api_version="2024-08-01-preview"
    )
    .chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "ping"}]
    )
    .choices[0].message.content
)