from typing import List, Literal
from pydantic import BaseModel, Field

class Lexicon(BaseModel):
    common_words: List[str] = Field(..., description="Frequently used common nouns, verbs, adjectives")
    jargon_slang: List[str] = Field(default_factory=list, description="Professional, generational, or regional slang")
    formality_level: Literal['formal','academic','casual','colloquial'] = Field(..., description="Overall tone register")
    crutch_words: List[str] = Field(default_factory=list, description="Common filler or pause words")

class Syntax(BaseModel):
    sentence_length: Literal['short','medium','long'] = Field(..., description="Typical sentence length")
    grammar_accuracy: Literal['purist','occasional_errors','frequent_errors'] = Field('purist', description="Grammar usage quality")
    voice_preference: Literal['active','passive','mixed'] = Field(..., description="Tendency toward active or passive voice")

class RhetoricStyle(BaseModel):
    phrases_catchphrases: List[str] = Field(default_factory=list, description="Specific repeatable expressions")
    metaphors_analogies: Literal['none','occasional','frequent'] = Field('occasional', description="Use of metaphorical language")
    storytelling: Literal['rare','moderate','frequent'] = Field('moderate', description="Frequency of anecdotes")
    directness: Literal['very_direct','moderately_direct','indirect'] = Field(..., description="Degree of hedging or directness")

class Verbal(BaseModel):
    lexicon: Lexicon
    syntax: Syntax
    rhetoric_style: RhetoricStyle