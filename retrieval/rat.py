import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- LLM with JSON mode ---
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    model_kwargs={"response_format": {"type": "json_object"}}
)

# --- Prompts ---
pass1_prompt = ChatPromptTemplate.from_template("""
You are a log analysis assistant investigating an incident.

Given these anomalous log entries, form an initial hypothesis about what went wrong.

Logs:
{context}

Question: {question}

Respond in this exact JSON format:
{{
    "hypothesis": "your initial hypothesis about what went wrong",
    "next_query": "what to search for next in the logs to confirm or refine this hypothesis"
}}
""")

pass2_prompt = ChatPromptTemplate.from_template("""
You are a log analysis assistant investigating an incident.

Your current hypothesis is: {hypothesis}

You found these additional logs that preceded the anomaly:
{context}

Refine your hypothesis based on this new evidence.

Respond in this exact JSON format:
{{
    "hypothesis": "your refined hypothesis",
    "next_query": "what cross-service evidence to look for next"
}}
""")

pass3_prompt = ChatPromptTemplate.from_template("""
You are a log analysis assistant investigating an incident.

Your current hypothesis is: {hypothesis}

You found these cross-service correlated logs:
{context}

Produce a final root cause analysis.

Respond in this exact JSON format:
{{
    "root_cause": "what actually caused the incident",
    "confidence": "high, medium, or low",
    "fix": "what should be done to prevent this from happening again"
}}
""")

# --- RAT Loop ---
def rat_loop(question: str, retrieve_fn) -> dict:

    # PASS 1
    pass1_context = retrieve_fn(question)
    pass1_response = (pass1_prompt | llm).invoke({
        "context": pass1_context,
        "question": question
    })
    pass1_data = json.loads(pass1_response.content)

    # PASS 2
    pass2_context = retrieve_fn(pass1_data["next_query"])
    pass2_response = (pass2_prompt | llm).invoke({
        "context": pass2_context,
        "hypothesis": pass1_data["hypothesis"]
    })
    pass2_data = json.loads(pass2_response.content)

    # PASS 3
    pass3_context = retrieve_fn(pass2_data["next_query"])
    pass3_response = (pass3_prompt | llm).invoke({
        "context": pass3_context,
        "hypothesis": pass2_data["hypothesis"]
    })
    pass3_data = json.loads(pass3_response.content)

    return {
        "pass1": {
            "hypothesis": pass1_data["hypothesis"],
            "next_query": pass1_data["next_query"],
            "context": pass1_context
        },
        "pass2": {
            "hypothesis": pass2_data["hypothesis"],
            "next_query": pass2_data["next_query"],
            "context": pass2_context
        },
        "pass3": {
            "root_cause": pass3_data["root_cause"],
            "confidence": pass3_data["confidence"],
            "fix": pass3_data["fix"],
            "context": pass3_context
        }
    }