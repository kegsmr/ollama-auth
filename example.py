import os
from pprint import pprint

import ollama


OLLAMA_HOST = os.getenv('OLLAMA_HOST')
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')

client = ollama.Client(
	OLLAMA_HOST,
	headers={
		'X-API-Key': OLLAMA_API_KEY
	}
)

response = client.chat(
    model="llama3.1",
    messages=[{"role":"user","content":"Hello Ollama!"}]
)

pprint(response)
