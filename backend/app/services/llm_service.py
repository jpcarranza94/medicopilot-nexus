"""
LLM Service for making calls to Saptiva API
"""
import httpx
import json
from typing import Dict, Any, Optional
from app.config.settings import settings


class SaptivaLLMService:
    """Service for interacting with Saptiva LLM API"""

    def __init__(self):
        self.api_key = settings.SAPTIVA_API_KEY
        self.base_url = settings.SAPTIVA_BASE_URL
        self.timeout = settings.LLM_TIMEOUT

    async def call_llm(
        self,
        prompt: str,
        system_prompt: str,
        model: str = "SAPTIVA_OPS",
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Make a call to Saptiva LLM API

        Args:
            prompt: User prompt
            system_prompt: System instructions
            model: Model to use (SAPTIVA_LEGACY or SAPTIVA_OPS)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            response_format: Optional JSON schema for structured output

        Returns:
            LLM response as string

        Raises:
            httpx.HTTPError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add response format if provided (for structured JSON output)
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions/",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data["choices"][0]["message"]

            # Some models return content in "reasoning_content" field
            content = message.get("content") or message.get("reasoning_content", "")
            return content

    async def call_with_json_response(
        self,
        prompt: str,
        system_prompt: str,
        model: str = "SAPTIVA_OPS",
        temperature: float = 0.3,
        max_tokens: int = 3000,
    ) -> Dict[str, Any]:
        """
        Make LLM call expecting JSON response

        Returns:
            Parsed JSON response as dictionary
        """
        response_format = {"type": "json_object"}

        response_text = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

        # Parse JSON response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from markdown code blocks or clean the response
            import re

            # Try to extract from ```json code blocks (non-greedy match for complete object)
            json_match = re.search(r'```json\s*(\{.*\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to extract from ``` code blocks (non-greedy match for complete object)
            json_match = re.search(r'```\s*(\{.*\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object anywhere in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            raise ValueError(f"Failed to parse JSON response. Raw response: {response_text[:500]}")


# Singleton instance
llm_service = SaptivaLLMService()
