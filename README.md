# Open LLM Translator

- [x] support Google translate
- [x] support Ollama
- [x] support Deepl (need api key)
- [x] support Cloudflare (need account id & api key)
- [ ] support OpenAI


## Technologies

- 🐍 Python
- ⚡️ Fastapi
- 🦙 Ollama


## Install

```.shell

git clone https://github.com/edison7500/open-llm-tranlator.git
cd open-llm-tranlator

cp env.example .env

uv sync --lock

uv run fastapi dev

```
