import os
from groq import AsyncGroq
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def ask_llm(context: str, question: str) -> str:

    try:
        system_prompt = (
            "You are a helpful assistant analyzing documents. "
            "Answer the user's question strictly based on the provided context below."
        )
        user_message = f"Context:\n{context}\n\nQuestion:\n{question}"

        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        logger.error(f"LLM Query failed: {e}")
        return "Error processing the question."