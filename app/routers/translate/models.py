from decimal import Decimal
from pydantic import BaseModel, Field


class TranslateText(BaseModel):
    text: str = Field(max_length=5000)


class TranslatedResult(BaseModel):
    target_lang: str = Field()
    text: str = Field()


class DetectLangResult(BaseModel):
    lang: str = Field()
    prob: Decimal = Field()
