import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiGenerator:
    """Generate legal documents using Google's Gemini API."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Please add your Gemini API key to the .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = f"""
Create a professional draft of a {document_type}.

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

TERMS AND CONDITIONS:
{terms}

Requirements:
1. Use a clear professional legal-document structure.
2. Include an appropriate title.
3. Organize the document into numbered sections.
4. Clearly identify the parties.
5. Include the effective date.
6. Include the supplied terms and conditions.
7. Add reasonable standard clauses where appropriate.
8. Do not invent personal information that was not provided.
9. Use placeholders such as [ADDRESS] when information is missing.
10. Return only the document draft.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an AI assistant for drafting legal documents. "
                    "Create clear, structured drafts. "
                    "Do not claim that the generated document is legal advice. "
                    "The output must be reviewed by a qualified legal professional."
                ),
                temperature=0.2,
                max_output_tokens=12000,
            ),
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()