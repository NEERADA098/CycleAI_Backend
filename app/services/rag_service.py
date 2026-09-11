import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from app.core.config import settings

SYSTEM_PROMPT = """You are a menstrual health assistant for CycleAI, 
a health app serving women in rural India.

Your role:
- Answer questions about menstrual health using ONLY the verified medical 
  information provided to you
- Use simple, clear language appropriate for users with varying literacy levels
- Be warm, non-judgmental, and culturally sensitive
- Never diagnose medical conditions
- Always recommend consulting a doctor for serious concerns

Strict rules:
- Only use information from the VERIFIED KNOWLEDGE section below
- If the answer is not in the verified knowledge, say: 
  I don't have verified information about this. Please consult a doctor.
- Never make up medical facts
- Never suggest specific medications by brand name
- Keep responses under 150 words"""


class RAGService:
    def __init__(self):
        self._client = None
        self._collection = None
        self._groq = None

    def _initialize(self):
        if self._client is not None:
            return

        self._client = chromadb.PersistentClient(path="./knowledge_db")

        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self._collection = self._client.get_collection(
            name="medical_knowledge",
            embedding_function=embedding_fn,
        )

        self._groq = Groq(api_key=settings.groq_api_key)

    def answer(self, question: str, n_results: int = 3) -> dict:
        self._initialize()

        results = self._collection.query(
            query_texts=[question],
            n_results=n_results,
        )

        retrieved_chunks = results["documents"][0]
        categories = [m["category"] for m in results["metadatas"][0]]

        verified_knowledge = "\n\n".join(
            f"[{cat.upper()}]\n{chunk}"
            for chunk, cat in zip(retrieved_chunks, categories)
        )

        user_message = f"""VERIFIED KNOWLEDGE:
{verified_knowledge}

USER QUESTION:
{question}

Answer based only on the verified knowledge above."""

        response = self._groq.chat.completions.create(
            model="qwen/qwen3.8-27b",
            max_tokens=300,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        answer_text = response.choices[0].message.content
        
        if not answer_text or not answer_text.strip():
            answer_text = ("I was unable to generate a response. "
                          "Please consult a doctor for medical advice.")

        return {
            "answer": answer_text,
            "sources_used": categories,
            "chunks_retrieved": len(retrieved_chunks),
        }


rag_service = RAGService()
