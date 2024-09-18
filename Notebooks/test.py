import gradio as gr
import openai

# Set your OpenAI API key
openai.api_key = "your-api-key-here"

def generate_poem(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You may need to use "gpt-3.5-turbo" instead
            messages=[
                {"role": "system", "content": "You are a creative poet. Create a short poem based on the given prompt."},
                {"role": "user", "content": f"Write a poem about: {prompt}"}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        poem = response.choices[0].message['content'].strip()
        return poem
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create Gradio interface
iface = gr.Interface(
    fn=generate_poem,
    inputs=gr.Textbox(lines=2, placeholder="Enter a prompt for your poem..."),
    outputs="text",
    title="Poem Generator",
    description="Enter a prompt, and the AI will generate a short poem based on it.",
)

# Launch the app
iface.launch()
