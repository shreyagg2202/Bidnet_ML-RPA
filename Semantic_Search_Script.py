import openai

def semantic_search(input_dict):
    # Fixed API key and model for simplicity
    api_key = '***'
    model = 'gpt-3.5-turbo'

    # Extract content and description from input dictionary
    content = input_dict.get('content', '')
    description = input_dict.get('description', '')

    # Initialize the OpenAI client with the API key
    client = openai.OpenAI(api_key=api_key)

    # Create the chat completion request
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": f"Description - {description}"}
        ]
    )
    
    # Extract and return the response
    response = completion.choices[0].message.content
    return response