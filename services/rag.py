from ollama import chat
from sqlalchemy.orm import Session
from services.hybrid_search import hybrid_search
from crud.document import get_document

def build_context(results: list ) -> str: # LLM에게 전달할 context를 생성하는 함수

    contexts = [] 

    for index, result in enumerate(results, start=1):
        context = (
            f"[자료 {index}]\n"
            f"{result['content']}\n"
        ) # llm에게 전달할 context를 생성하는 부분, 각 검색 결과의 content를 포함
        contexts.append(context)
        
    return "\n\n".join(contexts) 

def build_prompt(query: str, context: str) -> str: # LLM에게 전달할 prompt를 생성하는 함수
    prompt = (
        "다음 자료만을 근거로 질문에 답하세요.\n"
        "자료에 없는 내용은 추측하거나 만들어내지 마세요.\n"
        "자료만으로 답할 수 없다면 '제공된 자료에서 답을 찾을 수 없습니다.'라고 답하세요.\n\n"

        f"[자료]: {context}\n\n"
        f"[질문]: {query}\n\n"
        "[답변]\n"
    ) # llm에게 전달할 prompt를 생성하는 부분, 검색 결과와 사용자의 질문을 포함

    return prompt

def generate_answer(query: str, results: list) -> str: # LLM을 사용하여 답변을 생성하는 함수
    context = build_context(results) # 검색 결과를 기반으로 context를 생성
    prompt = build_prompt(query, context) # context와 사용자의 질문을 기반으로 prompt를 생성

    response = chat(
        model="qwen3:8b", 
        messages=[{"role": "user", "content": prompt,}]
    ) # LLM 모델 초기화

    return response.message.content

def answer_question(db: Session, query: str, top_k: int = 5, min_rerank_score: float = 0.1) -> dict: # 검색 결과를 기반으로 LLM을 사용하여 답변을 생성하는 함수
    results = hybrid_search(db, query, top_k) # 검색 결과를 가져옴

    relevant_results = [
        result 
        for result in results # 검색 결과를 rerank_score 기준으로 필터링
        if result["rerank_score"] >= min_rerank_score  # rerank_score가 최소값 이상인 경우만 필터링
    ]
    
    
    if not relevant_results: # 검색 결과가 없는 경우
        return {
            "answer": "제공된 자료에서 답을 찾을 수 없습니다.",
            "sources": [],
        } # 검색 결과가 없는 경우, LLM에게 전달할 답변과 source를 반환
    

    answer = generate_answer(query, relevant_results) # 검색 결과를 기반으로 답변을 생성

    sources = []

    seen_page_ids = set()  # 중복된 page_id를 추적하기 위한 집합
    
    for result in relevant_results:
        page_id = result["page_id"]
        document_id = result["document_id"]

        if page_id in seen_page_ids:
            continue  # 이미 처리한 page_id이면 건너뜀

        document = get_document(db, document_id) # 검색 결과의 document 정보를 가져옴
        
        if document:
            sources.append({
                "document_id": document.id,
                "title": document.title,
                "content": result["content"],
                "source": document.source,
                "page_id": page_id,
                "page_title": result["page_title"],
                "page_path": result["page_path"],
                "page_url": f"https://www.notion.so/{page_id.replace('-', '')}",  # Notion 페이지 URL 생성
            }) # 검색 결과의 document 정보를 source에 추가

            seen_page_ids.add(page_id) # 이미 처리한 page_id를 집합에 추가

    return {
        "answer": answer,
        "sources": sources,
    }
