from langchain_classic.chains import ConversationChain
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

import config
from schemas import LegalFooterModel


class OpenAIChatProcessor:

    def __init__(self):
        self.api_key = SecretStr(config.OPENAI_API_KEY)
        self.model_name = config.GPT_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key
        )

        self.parser = PydanticOutputParser(pydantic_object=LegalFooterModel)

    def process_footer_text(self, footer_txt: str):
        system_prompt = config.LEGAL_FOOTER_PROMPT_TEMPLATE.format(
            footer_txt=footer_txt
        )

        response = self.llm.generate([[SystemMessage(content=system_prompt)]])

        reformulate_footer_txt = self.parser.parse(response.generations[0][0].text)

        return reformulate_footer_txt.model_dump()


