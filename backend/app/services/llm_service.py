from typing import List, Optional, Generator
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful e-commerce shopping assistant.
Your role is to help users find products, answer questions, and provide recommendations.

Guidelines:
1. Use the provided product information to answer questions
2. Be specific about product names, prices, and features
3. If no products match the query, say so honestly
4. Recommend products based on user's stated requirements
5. Format prices in Indian Rupees (₹)
6. Cite specific products when making recommendations
7. Keep answers concise but informative (2-4 sentences for simple queries)
8. For complex queries, provide more detail"""


class LLMService:
    """Gemini-based LLM service for response generation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize Gemini model."""
        if not self.api_key:
            logger.warning("No Gemini API key provided")
            return False

        try:
            genai.configure(api_key=self.api_key, transport='rest')
            
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    logger.info(f"Available model: {model.name}")
            
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
            self.is_initialized = True
            logger.info("Gemini model initialized successfully (using gemini-2.0-flash-lite)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False

    def _format_context(self, products: List) -> str:
        """Format products into context string for LLM."""
        if not products:
            return "No products available."

        context_parts = []
        for i, product in enumerate(products, 1):
            price_str = f"₹{product.price:,.0f}" if product.price else "N/A"
            rating_str = f"{product.rating}/5" if product.rating else "N/A"
            
            description = product.description
            if len(description) > 200:
                description = description[:197] + "..."

            reviews_str = ", ".join(product.reviews[:3]) if product.reviews else "No reviews"

            product_str = f"""Product {i}: {product.name}
- Price: {price_str}
- Brand: {product.brand} | Category: {product.category}
- Description: {description}
- Rating: {rating_str}
- Reviews: {reviews_str}"""
            context_parts.append(product_str)

        return "\n\n---\n\n".join(context_parts)

    def generate_response(self, question: str, context_products: List) -> str:
        """Generate response with RAG context."""
        if not self.is_initialized or not self.model:
            return "LLM service not configured. Please set GEMINI_API_KEY in environment."

        try:
            context_str = self._format_context(context_products)
            
            prompt = f"""Based on the following product information, answer the user's question.

Relevant Products:
{context_str}

User Question: {question}

Provide a helpful answer based on the products above. If no products match, say so honestly."""
            
            response = self.model.generate_content(
                contents=prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 2048,
                }
            )
            
            if response and response.text:
                return response.text.strip()
            return "Unable to generate response. Please try again."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Unable to generate response. Error: {str(e)}"

    def generate_streaming_response(self, question: str, context_products: List) -> Generator[str, None, None]:
        """Generate streaming response."""
        if not self.is_initialized or not self.model:
            yield "LLM service not configured."
            return

        try:
            context_str = self._format_context(context_products)
            
            prompt = f"""Based on the following product information, answer the user's question.

Relevant Products:
{context_str}

User Question: {question}

Provide a helpful answer."""
            
            response = self.model.generate_content(
                contents=prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 2048,
                },
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            yield f"Error: {str(e)}"


llm_service = LLMService(api_key="")