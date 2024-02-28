from langchain.chains import create_tagging_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

class GetPostCategory:
    def __init__(self, categories: list[str], text):
        self.categories = categories
        self.text = text
        self.__llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        if not isinstance(value, list) and any(not isinstance(ins, str) for ins in value):
            raise ValueError('Category must be list of strings')
        self._categories = value

    @property
    def _schema(self):
        return {
            "properties": {
                "category": {
                    "type": "string",
                    "enum": self.categories,
                    "description": "best category for this text."
                }
            },
            "required": ["category", ],
        }

    def run(self):
        chain = create_tagging_chain(self._schema, self.__llm)
        result = chain.run(self.text)
        return result.get("category", None)
