import openai
import os

# Load the API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY") # SA: ToDo: modify


def chatgpt_query_to_text(prompt,
                          engine="davinci",
                          max_tokens=1000,
                          n=1,
                          stop=None,
                          temperature=0):
    # Call the OpenAI API to generate answers
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        temperature=temperature)
    response.choices[0].text
