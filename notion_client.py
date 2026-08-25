import os
import time
from dotenv import load_dotenv
import httpx


load_dotenv()  # .env 파일에서 환경 변수를 로드

NOTION_TOKEN = os.getenv("NOTION_TOKEN") # Notion API 토큰, 실제 서비스에서는 안전하게 관리되어야 함
NOTION_DATA_SOURCE_ID = os.getenv("NOTION_DATA_SOURCE_ID") # Notion 데이터 소스 ID, 실제 서비스에서는 안전하게 관리되어야 함

if NOTION_TOKEN is None:
    raise RuntimeError("NOTION_TOKEN is not set")

if NOTION_DATA_SOURCE_ID is None:
    raise RuntimeError("NOTION_DATA_SOURCE_ID is not set")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2026-03-11",
}
NOTION_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
NOTION_MAX_RETRIES = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def request_notion(method: str, url: str) -> httpx.Response:
    for attempt in range(NOTION_MAX_RETRIES):
        try:
            response = httpx.request(
                method,
                url,
                headers=NOTION_HEADERS,
                timeout=NOTION_TIMEOUT,
            )
        except httpx.TransportError:
            if attempt == NOTION_MAX_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
            continue

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt == NOTION_MAX_RETRIES - 1:
                response.raise_for_status()
            time.sleep(2 ** attempt)
            continue

        response.raise_for_status()
        return response

    raise RuntimeError("Notion request failed")

def get_data_source(): # Notion 데이터 소스를 조회하는 함수 정의
    url = f"https://api.notion.com/v1/data_sources/{NOTION_DATA_SOURCE_ID}" # Notion API의 데이터 소스 조회 엔드포인트 URL 생성
    response = request_notion("GET", url)

    return response.json() # 요청 성공 시 응답 반환

def get_pages(): # Notion 데이터 소스의 페이지를 조회하는 함수 정의
    url = (f"https://api.notion.com/v1/data_sources/"
        f"{NOTION_DATA_SOURCE_ID}/query") # Notion API의 페이지 조회 엔드포인트 URL 생성
    response = request_notion("POST", url)

    data = response.json() # 요청 성공 시 응답을 JSON 형식으로 변환
    return data["results"] # 조회된 페이지 리스트 반환

def extract_page_metadata(page : dict):  # Notion 페이지에서 텍스트를 추출하는 함수 정의
    title = "" # Notion 페이지의 텍스트를 저장할 변수 초기화
    for prop in page["properties"].values(): # Notion 페이지의 속성(properties) 반복
        if prop["type"] == "title": # 속성 타입이 title인
            title = "".join( # title 속성의 plain_text를 추출하여 title 변수에 저장
                item["plain_text"]
                for item in prop["title"] 
            )
            break
    return {
        "notion_page_id" : page["id"],
        "title" : title,
        "source" : page["url"],
        "last_edited_time" : page["last_edited_time"],
    }

def get_block_children(block_id: str) -> list[dict]: # Notion 블록의 자식 블록을 조회하는 함수 정의
    url = f"https://api.notion.com/v1/blocks/{block_id}/children" # Notion API의 블록 조회 엔드포인트 URL 생성
    response = request_notion("GET", url)

    return response.json()["results"] # 요청 성공 시 응답에서 블록 리스트 반환

def get_page_blocks(page_id: str) : # Notion 페이지의 블록을 조회하는 함수 정의
    return get_block_children(page_id) # Notion 페이지의 블록 조회


def get_all_blocks(page_id: str) -> list[dict]: # Notion 페이지의 모든 블록을 조회하는 함수 정의
    blocks = get_block_children(page_id) # Notion 페이지의 블록 조회

    all_blocks = [] # 모든 블록을 저장할 리스트 초기화

    for block in blocks: # 블록 반복
        all_blocks.append(block) # 블록을 all_blocks 리스트에 추가

        if block.get("has_children"): # 블록에 자식 블록이 있는 경우
            child_blocks = get_all_blocks(block["id"]) # 재귀적으로 자식 블록 조회
            all_blocks.extend(child_blocks) # 자식 블록을 all_blocks 리스트에 추가
        
    return all_blocks # 모든 블록 리스트 반환


def extract_block_text(block: dict) -> str: # Notion 블록에서 텍스트를 추출하는 함수 정의
    block_type = block["type"] # 블록 타입 추출
    
    if block_type == "child_page": # 블록 타입이 child_page인 경우
        return block["child_page"]["title"] # child_page 블록의 title 반환
    
    block_data = block.get(block_type, {}) # 블록 데이터 추출

    rich_text = block_data.get("rich_text", []) # 블록 데이터에서 rich_text 추출
    
    return "".join(item["plain_text"] for item in rich_text) # rich_text에서 plain_text를 추출하여 문자열로 반환

def extract_page_text(blocks : list[dict]) -> str: # Notion 페이지에서 텍스트를 추출하는 함수 정의
    text_content = [] # 텍스트를 저장할 리스트 초기화
    for block in blocks: # 블록 반복
        text = extract_block_text(block) # 블록에서 텍스트 추출
        if text: # 텍스트가 존재할 경우
            text_content.append(text) # 텍스트를 리스트에 추가
    return "\n".join(text_content) # 텍스트 리스트를 줄바꿈으로 연결하여 반환

def get_page_sections(page_id: str, page_title: str, parent_path: list[str] | None = None) -> list[dict]: # Notion 페이지의 섹션을 조회하는 함수 정의
    if parent_path is None : 
        parent_path = []

    current_path = parent_path + [page_title] # 현재 경로를 parent_path와 page_title을 합쳐서 생성
        
    blocks = get_block_children(page_id) # 자식 Notion 페이지의 모든 블록 조회
    texts = [] # 텍스트를 저장할 리스트 초기화
    sections = [] # 섹션을 저장할 리스트 초기화
    
    for block in blocks: # 블록 반복
        if block["type"] == "child_page": # 블록 타입이 child_page인 경우
            child_page_id = block["id"] # child_page 블록의 id 추출
            child_page_title = block["child_page"]["title"] # child_page 블록의 title
            child_sections = get_page_sections(child_page_id, child_page_title, current_path) # 재귀적으로 child_page 블록의 섹션 조회
                
            sections.extend(child_sections) # child_page 블록의 섹션을 sections 리스트에 추가
            continue # 다음 블록으로 이동

        text = extract_block_text(block) # 블록에서 텍스트 추출
        if text: # 텍스트가 존재할 경우
            texts.append(text) # 텍스트를 리스트에 추가

    sections.insert(0, { # 섹션 리스트의 첫 번째 요소에 현재 페이지의 섹션 정보를 추가
        "page_id": page_id,
        "page_title": page_title,
        "page_path": ">".join(current_path),
        "content": "\n".join(texts),
        "page_url": f"https://www.notion.so/{page_id.replace('-', '')}",  # Notion 페이지 URL 생성
    })


    return sections # 섹션 리스트 반환