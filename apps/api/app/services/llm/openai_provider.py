import json

from openai import AsyncOpenAI, OpenAIError

from app.domain import QAResultKind
from app.services.llm.base import LLMProviderError, LLMRequest, LLMResult


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str, timeout_seconds: float):
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds)

    async def answer(self, request: LLMRequest) -> LLMResult:
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Reviews:\n{request.review_context}\n\n"
                            f"Question: {request.question}"
                        ),
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "reviewlens_answer",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "answer": {"type": "string"},
                                "result_kind": {
                                    "type": "string",
                                    "enum": [kind.value for kind in QAResultKind],
                                },
                                "evidence_review_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "answer",
                                "result_kind",
                                "evidence_review_ids",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
            )
            content = response.choices[0].message.content
            if not content:
                raise LLMProviderError()
            payload = json.loads(content)
            return LLMResult(
                answer=str(payload["answer"]).strip(),
                result_kind=QAResultKind(payload["result_kind"]),
                evidence_review_ids=tuple(payload["evidence_review_ids"]),
            )
        except (
            OpenAIError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise LLMProviderError() from exc
