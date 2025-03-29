# === core/langgraph_runner.py ===
import os
from langchain_community.vectorstores import FAISS
import pickle
from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories.sql import SQLChatMessageHistory
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import TextLoader
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
import dotenv

dotenv.load_dotenv()

# === Load and split docs ===
loader = TextLoader("./data/info.txt")
docs = loader.load()
sentences = [s.strip() for doc in docs for s in doc.page_content.split("\n") if s.strip()]

# === Embedding model ===
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.environ["GEMINI_API_KEY"]
)

# === FAISS: Load or build index ===
faiss_dir = "faiss_index"
if os.path.exists(os.path.join(faiss_dir, "index.faiss")):
    vectorstore = FAISS.load_local(
        faiss_dir,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True  # ✅ Add this flag
    )
else:
    vectorstore = FAISS.from_texts(sentences, embedding_model)
    vectorstore.save_local(faiss_dir)

# === LangGraph State ===
class GraphState(TypedDict):
    query: str
    facts: list[str]
    output: str
    chat_history: List[BaseMessage]
    suggested_questions: List[str]

# === Node: Semantic Retrieval using FAISS ===
def retrieve(state: GraphState) -> GraphState:
    results = vectorstore.similarity_search(state["query"], k=3)
    facts = [doc.page_content for doc in results]
    return {**state, "facts": facts}

# === Node: Gemini LLM with Follow-Up Suggestions ===
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    max_output_tokens=2048,
    google_api_key=os.environ["GEMINI_API_KEY"]
)

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the user's question using the chat history and retrieved facts.

Chat History:
{chat_history}

Facts:
{facts}

User Question:
{query}

Answer clearly first, then suggest 2-3 intelligent follow-up questions that the user might ask next.
""")
chain = prompt | llm

def generate_response(state: GraphState) -> GraphState:
    response = chain.invoke({
        "query": state["query"],
        "facts": "\n".join(state["facts"]),
        "chat_history": "\n".join([m.content for m in state.get("chat_history", [])]),
    })

    full_text = response.content

    # === Extract follow-ups
    if "\n\n" in full_text:
        main, last_block = full_text.strip().rsplit("\n\n", 1)
        lines = last_block.strip().split("\n")
        suggestions = [
            line.lstrip("1234567890.:-• ").strip()
            for line in lines if len(line.split()) > 2
        ][:3]
        if not suggestions:
            main = full_text
    else:
        main = full_text
        suggestions = []

    updated_history = state.get("chat_history", []) + [
        HumanMessage(content=state["query"]),
        AIMessage(content=main)
    ]

    return {
        **state,
        "output": main,
        "chat_history": updated_history,
        "suggested_questions": suggestions
    }

# === LangGraph DAG ===
graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate_response)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.set_finish_point("generate")
rag_chain = graph.compile()

# === Memory Wrapper ===
runnable_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: SQLChatMessageHistory(
        session_id=session_id,
        connection="sqlite:///memory.db"
    ),
    input_messages_key="query",
    history_messages_key="chat_history"
)
