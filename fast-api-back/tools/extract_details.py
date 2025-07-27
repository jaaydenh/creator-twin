from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from config.client import model
from tools.transcript import get_script


def get_chain():
    
    # Create the system prompt template with detailed instructions
    prompt_template = """You are an AI assistant that analyzes communication styles and creates detailed profiles.
    Your task is to analyze the given script and create a comprehensive communication profile.

    you can check out the speech of the person by using the tool get_script.
    the length of the script is length:{length} and its 0 indexed. 

    u are allowed to use the tool get_script 6 times.You can randomly pick the index from 0 to length-1

    Provide a structured profile following this format:

    {format_instructions}

    Make sure to support your analysis with specific examples from the script."""

    # Create the prompt with system and human messages
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        ("human", "Please analyze the script and create a detailed communication profile.")
    ])

    # Create the agent with tools
    agent = create_react_agent(
        model=model,
        tools=[get_script]
    )


    chain = prompt | agent 
    return chain



