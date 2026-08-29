"""
Gradio front-end. Run with: python app.py
"""
import gradio as gr
from src.agent.agent import answer_query

DEFAULT_USER_ID = "demo_user"  # replace with a real session/user id in production


def respond(message, chat_history):
    answer = answer_query(DEFAULT_USER_ID, message)
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": answer})
    return "", chat_history


with gr.Blocks(title="Business Assistant") as demo:
    gr.Markdown("# Business Assistant (Arabic / English)")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask about policies, sales, or anything else...")
    clear = gr.Button("Clear")

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch()
