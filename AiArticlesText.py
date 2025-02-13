import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import re

class HashtagTextEnhancer:
    class TextOutput(BaseModel):

        rewritten_text: str = Field(description="Testo riscritto in maniera piu discorsiva ")
        hashtags: list[str] = Field(description="Lista di hashtag popolari da aggiungere")
        title: str = Field(description="Titolo dell'articolo (max 10 caratteri)")
        subtitle: str = Field(description="Sottotitolo Breve dell'articolo (max 10 caratteri)")
        description: str = Field(description="parole chiave per ricerca di un immagine max 3 parole")


    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        load_dotenv()
        api_key = os.getenv("OPENAIKEY")
        self.llm = ChatOpenAI(model=model_name, openai_api_key=api_key,temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=self.TextOutput)

        self.prompt = PromptTemplate(
            template=(
                "Riscrivi il seguente articolo per un post instagram cerca di essere piu discorsivo  "
                "Poi, aggiungi gli hashtag più popolari e rilevanti.  "
                "Poi, Scrivimi anche un titolo (max 20 caratteri) e sottotitolo (max 10 caratteri)."
                "parole chiave per ricerca di un immagine max 3 parole"
                "Testo: {text}\n\n{format_instructions}"
            ),
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def enhance_text(self, text: str):
        response = self.chain.run(text=text)
        parsed_response = self.parser.parse(response)
        return parsed_response
        # Formatta il testo finale con gli hashtag




