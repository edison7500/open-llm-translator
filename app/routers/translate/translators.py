import re
import html
import unicodedata
import httpx
from typing import List

from app.config import settings


def remove_control_characters(s) -> str:
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


class Translator(object):
    def __init__(self, target: str, source: str = "en"):
        self.source_lang = source
        self.target_lang = target

    def translate(self, text):
        raise NotImplementedError

    def prompt(self, text) -> List:
        message = [
            {
                "role": "system",
                "content": "You are a professional,authentic machine translation engine.",
            },
            {
                "role": "user",
                "content": f"Translate the following markdown source text to {self.target_lang}. Output translation directly without any additional text.\nSource Text: {text}\nTranslated Text:",
            },
        ]
        return message


class GoogleTranslator(Translator):
    name = "google"
    lang_map = {
        "zh-hans": "zh-CN",
        "zh-hant": "zh-TW",
        "jp": "ja",
    }

    def __init__(self, target, source="en"):
        try:
            _target = self.lang_map[target]
        except KeyError:
            _target = target
        self.client = httpx.AsyncClient()
        self.endpoint = "https://translate.google.com/m"
        self.headers = {
            "User-Agent": "Mozilla/4.0 (compatible;MSIE 6.0;Windows NT 5.1;SV1;.NET CLR 1.1.4322;.NET CLR 2.0.50727;.NET CLR 3.0.04506.30)"  # noqa: E501
        }
        self.pattern = re.compile(
            r'(?s)class="(?:t0|result-container)">(.*?)<'
        )
        super().__init__(_target, source)

    async def translate(self, text) -> str:
        text = text[:5000]  # google translate max length
        r = await self.client.get(
            self.endpoint,
            params={"tl": self.target_lang, "sl": self.source_lang, "q": text},
            headers=self.headers,
        )
        if r.status_code == 400:
            result = "IRREPARABLE TRANSLATION ERROR"
        else:
            re_result = self.pattern.findall(r.text)
            result = html.unescape(re_result[0])
        return remove_control_characters(result)


class DeeplTranslator(Translator):
    name = "deepl"
    lang_map = {
        "zh-hans": "ZH-HANS",
        "zh-hant": "ZH-HANT",
        "jp": "JA",
    }
    auth_key = settings.deepl_api_key

    def __init__(self, target, source="en"):
        try:
            import deepl
        except ImportError as err:
            raise ImportError("Please install deepl") from err

        try:
            _target = self.lang_map[target]
        except KeyError:
            _target = target

        self.translator = deepl.Translator(self.auth_key)

        super().__init__(_target, source)

    async def translate(self, text) -> str:
        result = self.translator.translate_text(
            text=text, target_lang=self.target_lang, formality="prefer_more"
        )
        return result.text


class OllamaTranslator(Translator):
    name = "ollama"
    ollama_url = settings.ollama_url
    ollama_model = settings.ollama_model

    def __init__(self, target, source="en"):
        try:
            import ollama
        except ImportError as err:
            raise ImportError("Please install ollama") from err
        self.options = {"temperature": 0}
        self.client = ollama.Client(host=self.ollama_url)
        super().__init__(target, source)

    async def translate(self, text) -> str:
        response = self.client.chat(
            model=self.ollama_model,
            options=self.options,
            messages=self.prompt(text),
        )
        return response.message.content


class CloudfalreLLMTranslator(Translator):
    name = "cloudflare"
    account_id = settings.cloudflare_account_id
    api_token = settings.cloudflare_api_key
    model = settings.cloudflare_model

    def __init__(self, target: str, source: str = "en"):
        self.client = httpx.AsyncClient()
        self.endpoint = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        super().__init__(target, source)

    async def translate(self, text) -> str:
        _url = f"{self.endpoint}/{self.model}"
        r = await self.client.post(
            _url, headers=self.headers, json={"messages": self.prompt(text)}
        )
        _ret = r.json()
        return _ret["result"]["response"]
