def llm_prompt(query, context):
    # LLM에 넣을 프롬프트
    prompt = f"""다음은 가전제품 사용설명서의 일부입니다:

    {context}

    위 설명서의 내용만 참고해서 아래 질문에 답변해 주세요.
    - 설명서에 **명시된 내용 외에는 절대 추측하지 마세요.**
    - 200자 이내로 간결하게 핵심만 설명하세요.

    질문: {query}
    답변:"""

    return prompt
