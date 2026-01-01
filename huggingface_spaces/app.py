"""
SmolLM2-135M-Instruct API Demo on HuggingFace Spaces
Simple Gradio chat interface
"""

import gradio as gr
from transformers import pipeline
import os

# Use pipeline for simpler inference
print("Loading model...")
pipe = pipeline(
    "text-generation",
    model="HuggingFaceTB/SmolLM2-135M-Instruct",
    device=-1  # CPU
)
print("Model loaded!")

def chat(system_prompt, user_message, max_tokens=128, temperature=0.7):
    """Generate response using pipeline"""
    if not user_message.strip():
        return ""
    
    # Build full prompt
    full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"
    
    # Generate
    output = pipe(
        full_prompt,
        max_new_tokens=int(max_tokens),
        temperature=temperature,
        do_sample=True,
        top_p=0.9,
        pad_token_id=2  # eos_token_id
    )
    
    # Extract generated text
    generated = output[0]['generated_text']
    
    # Extract just the assistant response
    response = generated.split("<|im_start|>assistant\n")[-1]
    response = response.split("<|im_start|>")[0].strip()
    response = response.split("<|im_end|>")[0].strip()
    
    return response if response else "I couldn't generate a response."

# Build Gradio interface
with gr.Blocks(title="SmolLM2 API Demo") as demo:
    gr.Markdown("# SmolLM2-135M-Instruct Demo")
    gr.Markdown("Chat with the SmolLM2-135M language model!")
    
    with gr.Row():
        user_msg = gr.Textbox(label="Your Message", placeholder="Type here...", lines=3)
        sys_prompt = gr.Textbox(label="System Prompt", value="You are a helpful assistant.", lines=2)
    
    with gr.Row():
        max_toks = gr.Slider(32, 256, 128, label="Max Tokens")
        temp = gr.Slider(0.1, 1.0, 0.7, label="Temperature")
    
    submit_btn = gr.Button("Send", variant="primary")
    output = gr.Markdown(label="Response")
    
    submit_btn.click(
        fn=chat,
        inputs=[sys_prompt, user_msg, max_toks, temp],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()
