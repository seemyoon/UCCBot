from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

import config
from rag.context_builder import ContextBuilder
from vector_db import VectorDB


class RAGPipline:
    def __init__(self):
        self.vectordb = VectorDB()
        self.context_builder = ContextBuilder()
        self.number_of_results_to_return = config.NUMBER_OF_RESULTS_TO_RETURN

        self.api_key = SecretStr(config.OPENAI_API_KEY)
        self.model_name = config.GPT_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0,
        )

        self.chat_history = []

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                    You are a legal assistant and expert in the Criminal Code of Ukraine.
                    Use the context below to answer the user's question.
                    Only answer questions related to the Criminal Code of Ukraine.
                    Provide precise answers in Ukrainian.
                    Do not answer questions outside the Criminal Code.
                    
                    Context: {context}
                """
            ),
            MessagesPlaceholder(
                variable_name="chat_history"
            ),
            (
                "human", "{query}"
            )
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def run_rag_pipline(self, query):
        retrieve_results_from_db = self.vectordb.similarity_search(query, self.number_of_results_to_return)

        context = self.context_builder.build(retrieve_results_from_db)

        response = self.chain.invoke({
            "context": context,
            "query": query,
            "chat_history": self.chat_history,
        })

        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.append(AIMessage(content=response))

        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        return response

    def clear_history(self):
        self.chat_history = []


if __name__ == "__main__":
    # python -m rag.rag_pipeline

    rag_pipline = RAGPipline()
    result = rag_pipline.run_rag_pipline("покарання за крадіжку")

    print(result)
