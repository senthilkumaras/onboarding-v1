from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

llama = ChatGroq(model="llama-3.1-8b-instant")

try:
    response = llama.invoke("Reply with just: OK")
    print("🟢 LLaMA is alive:", response.content)
except Exception as e:
    print("🔴 LLaMA error:", e)