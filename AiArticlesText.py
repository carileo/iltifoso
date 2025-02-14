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
        title: str = Field(description="Titolo dell'articolo  max 2 parole ")
        subtitle: str = Field(description="Sottotitolo  dell'articolo max 2 parole dove centra il bari o biancorossi")
        description: str = Field(description="parole chiave per ricerca di un immagine SSC Bari e altre due parole chiavi ")


    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        if os.path.exists('.env'):
            print("Ambiente locale rilevato: Caricamento delle variabili d'ambiente...")
            load_dotenv()
        else:
            print("Ambiente di produzione rilevato: Nessun caricamento di .env.")

        api_key = os.getenv("OPENAIKEY")
        self.llm = ChatOpenAI(model=model_name, openai_api_key=api_key,temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=self.TextOutput)

        self.prompt = PromptTemplate(
            template=(
                "Riscrivi il seguente articolo per un post instagram cerca di essere piu discorsivo  "
                "Poi, aggiungi gli hashtag più popolari e rilevanti.  "
                "Poi, Scrivimi anche un titolo di due parole e sottotitolo di due parole."
                "parole chiave per ricerca di un immagine max 3 parole tra cui SSC Bari e altre due parole chiavi dell'articolo "
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




