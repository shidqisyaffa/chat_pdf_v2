import openai
import requests
from typing import Tuple, List

class LMStudioManager:
    def __init__(self, base_url="http://127.0.0.1:1234/v1", timeout=5):
        self.base_url = base_url
        self.timeout = timeout
        self.client = None
        
    def setup_client(self):
        """Set up OpenAI client with custom base URL"""
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key="not-needed"
        )
        return self.client
        
    def check_connection(self) -> Tuple[bool, str]:
        """Check if LM Studio API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=self.timeout)
            if response.status_code == 200:
                return True, "Connected"
            else:
                return False, f"Failed to connect: {response.status_code} - {response.text}"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - Is LM Studio running?"
        except requests.exceptions.Timeout:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def get_available_models(self) -> Tuple[bool, List[str]]:
        """Get list of available models from LM Studio API"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=self.timeout)
            if response.status_code == 200:
                models_data = response.json()
                return True, [model["id"] for model in models_data.get("data", [])]
            else:
                return False, f"Failed to fetch models: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Error connecting to LM Studio server: {e}"
            
    def get_response(self, context: str, question: str, model_name: str, temperature: float, max_tokens: int) -> Tuple[bool, str]:
        """Get response from OpenAI API based on context and question"""
        prompt = f"""You are a helpful and informative bot that answers questions using text from the reference context included below. Be sure to respond in a complete sentence, providing in depth, in detail information and including all relevant background information. However, you are talking to a non-technical audience, so be sure to break down complicated concepts and strike a friendly and conversational tone. If the passage is irrelevant to the answer, you may ignore it.

Context: {context}

Question: {question}"""

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(temperature),
                max_tokens=int(max_tokens)
            )
            return True, response.choices[0].message.content.strip()
        except Exception as e:
            return False, f"Error generating response: {e}"
            
    def summarize_document(self, chunks: List[dict], model_name: str, temperature: float) -> Tuple[bool, str]:
        """Generate a summary of the document"""
        sample_chunks = chunks[:min(5, len(chunks))]
        sample_text = "\n\n".join([chunk["content"] for chunk in sample_chunks])
        
        prompt = f"""Please provide a concise summary of the following document. Focus on the main topics and key information.

Document excerpt:
{sample_text}

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes documents accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(temperature),
                max_tokens=300
            )
            return True, response.choices[0].message.content.strip()
        except Exception as e:
            return False, f"Error generating summary: {e}"
