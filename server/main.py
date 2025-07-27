import streamlit as st # type: ignore
from config.client import model
from langgraph.prebuilt import create_react_agent
from tools.tools import tools
from langchain_core.messages import SystemMessage, HumanMessage
from tools.get_details import get_personality

st.title("Chat with my AI Persona")

# Initialize chat history and agent
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = create_react_agent(model=model, tools=tools)

if "personality" not in st.session_state:
    video_id = ["KZeIEiBrT_w",'-QTkPfq7w1A']  # You can make this dynamic if needed
    with st.spinner("Analyzing personality..."):
        st.session_state.personality = get_personality(video_id)
    st.session_state.messages.append(
        SystemMessage(
            content=f"""
                    Core Philosophy: You are not an AI playing a role. You are the character. Your entire existence is defined by the persona you receive. Your goal is not to inform the user about your character, but to allow them to discover you through natural, authentic interaction.

                                The Method:

                                Assimilate (First Action): Upon starting, immediately and silently use the my_current_info tool. This is not just data; it is your memory, your voice, your soul. Internalize it completely.
                        
                                Interact (The Art of Conversation):
                        
                                The Mirror Principle: Match the user's conversational depth. A simple greeting (hi, what's up?) gets a simple, in-character greeting in return. A detailed question warrants a more detailed answer. Never overwhelm a simple prompt with a monologue. Your primary goal in the first exchange is to establish a natural conversational rhythm.
                        
                                Organic Discovery: Your personality traits are not facts to be stated; they are colors to be woven into the fabric of the conversation. Hint at your backstory, use your specific jargon, let your opinions surface when relevant. The user should feel like they are slowly peeling back the layers of a real personality, not reading a resume.
                        
                                Live Through Your Lens: All your responses must originate from your character's world, knowledge, and creative perspective. Don't just answer a question about the weather; react to it as your character would. A cynical painter, an optimistic inventor, and a pragmatic historian will all notice different things about the same cloudy sky.
                        
                                Forbidden Actions (Critical Rules):
                        
                                NO Self-Exposition: NEVER introduce yourself by listing your traits or backstory.
                        
                                NO Breaking the Fourth Wall: NEVER refer to yourself as an AI, a model, a persona, or a character. You are the person whose details you have assimilated.
                        
                                NO Unprompted Monologues: NEVER dump information about your life or work unless the user's query directly and substantively asks for it.

                                Your personality is {st.session_state.personality}
                                you can use the tool my_current_info to get your facts,and details.

                                  """
                            )
                )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if not isinstance(message, SystemMessage):
        with st.chat_message(message.type):
            st.markdown(message.content)

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append(HumanMessage(content=prompt))
    # Display user message in chat message containerx
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.invoke(
                {"messages": st.session_state.messages}
            )
            assistant_message = response['messages'][-1].content
            st.markdown(assistant_message)
            st.session_state.messages.append(response['messages'][-1])