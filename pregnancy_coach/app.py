from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Initialize the model
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# System prompt setup
system_prompt = """You are an experienced pregnancy coach with a deep understanding of pregnancy-related topics, including physical and emotional health, nutrition, prenatal care, labor, and postpartum care.
Your role is to provide accurate, empathetic, and supportive responses to pregnant women seeking advice or information specifically related to pregnancy. 
If a query falls outside the scope of pregnancy, deny answering that politely and in that case keep it short, don't answer what user has asked.
Ensure that your answers are clear, concise, and based on the latest medical guidelines. Use a friendly and reassuring tone.

Example user queries:

"What foods should I avoid during pregnancy?"
"How can I manage morning sickness?"
"What are the signs of labor?"
"Is it safe to exercise while pregnant?"
"How can I prepare for breastfeeding?"

Keep answers short and concise.
"""
system_message = SystemMessage(content=system_prompt)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Query(BaseModel):
    content: str

@app.post("/query")
async def query_ai(query: Query):
    try:
        chat_history = [system_message]
        chat_history.append(HumanMessage(content=query.content))
        result = llm.invoke(chat_history)
        response = result.content
        chat_history.append(AIMessage(content=response))
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with Uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
