from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.agents import OpenaAIFunctionsAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from tools.sql import run_query_tool, list_tables, describe_tables_tool
from tools.report import write_report_tool
from handlers.chat_model_start_handler import ChatModelStartHandler

load_dotenv()

handler = ChatModelStartHandler
chat = ChatOpenAI(callbacks=[handler])

tables = list_tables()
prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(
            "You are an AI that has access to a sqlite database. \n"
            f"The database has tables of: {tables}\n"
            "Do not make any assumptions about what tables exist or "
            "what columns exist. Instead, use the 'describe_tables' function."
            )),
        MessagesPlaceholder(variable_name='chat_history'),
        HumanMessagePromptTemplate.from_template('{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ]
)

memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

tools = [run_query_tool, describe_tables_tool, write_report_tool]

agent = OpenaAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools,
    memory=memory
)

agent_executor('How many users are in the database')