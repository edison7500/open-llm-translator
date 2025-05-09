from decimal import Decimal
from typing import Annotated, List, Literal, Any

from fastapi import APIRouter
from fastapi import Query, Body
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from langdetect import detect_langs

from app.utils.module_loading import import_string

# from app.routers.translate.translators import GoogleTranslator

Translate_Engine_Map = {
    "google": "app.routers.translate.translators.GoogleTranslator",
    "deepl": "app.routers.translate.translators.DeeplTranslator",
    "ollama": "app.routers.translate.translators.OllamaTranslator",
    "cloudflare": "app.routers.translate.translators.CloudfalreLLMTranslator",
}


router = APIRouter()


def get_enginee(engine) -> Any:
    try:
        _enginee = Translate_Engine_Map[engine]
    except KeyError as err:
        raise Exception(
            f"{engine} translator engine can not be support"
        ) from err
    klass = import_string(_enginee)
    return klass


class TranslateParams(BaseModel):
    sl: Literal[
        "en",
    ] = Field(default="en")
    tl: Literal["es", "zh-hans", "zh-hant", "jp", "ko", "vi", "th"] = Field(
        default="es", description="target language"
    )
    engine: Literal["google", "deepl", "ollama", "cloudflare"] = Field(
        default="google", description="choose a engine for translate"
    )


class TranslateText(BaseModel):
    text: str = Field(max_length=5000)


class TranslatedResult(BaseModel):
    target_lang: str = Field()
    text: str = Field()


class DetectLangResult(BaseModel):
    lang: str = Field()
    prob: Decimal = Field()


@router.post("/translate/", tags=["translate"])
async def translate(
    query: Annotated[TranslateParams, Query()] = None,
    translate: Annotated[TranslateText, Body()] = None,
) -> TranslatedResult:

    try:
        engine = get_enginee(query.engine)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
    agent = engine(target=query.tl)
    _target_text = await agent.translate(text=translate.text)

    return TranslatedResult(target_lang=query.tl, text=_target_text)


@router.post("/langdetect/", tags=["langdetect"])
async def detect(
    translate: Annotated[TranslateText, Body()] = None,
) -> List[DetectLangResult]:
    langs = detect_langs(translate.text)
    return [DetectLangResult(lang=lang.lang, prob=lang.prob ) for lang in langs]
