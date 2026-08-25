
def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]: # 텍스트를 일정한 크기로 분할하는 함수
    chunks = [] # 분할된 텍스트를 저장할 리스트 초기화
    step = chunk_size - overlap # 분할 시 겹치는 부분을 고려하여 step 계산
    for i in range(0, len(text), step): # 텍스트 길이만큼 반복, step 단위로 증가
        chunks.append(text[i:i + chunk_size]) # 텍스트를 chunk_size 단위로 분할하여 리스트에 추가
    return chunks # 분할된 텍스트 리스트 반환