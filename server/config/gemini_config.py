from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

load_dotenv()
userdata = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
}


def generate(text):
    client = genai.Client(
         api_key= userdata.get('GOOGLE_API_KEY'),
    )
    model = "gemini-2.5-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text = text),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

    generated_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_text += chunk.text
    return generated_text
