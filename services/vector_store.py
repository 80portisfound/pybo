from services.embedding import embed_chunks,embed_query
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")  # ChromaDB 클라이언트 초기화, 데이터는 ./chroma_db에 저장

def get_collection(): # Chroma collection을 생성/가져오는 함수
        knowledge_collection = client.get_or_create_collection("knowledge_chunks")  # "knowledge_chunks"라는 이름의 컬렉션을 생성 후 반환
        return knowledge_collection  # 생성된 컬렉션 반환

def add_chunks_to_vector_store(chunks, embedded_chunks: list[dict]): # Chunk + Embedding을 ChromaDB에 저장
    collection = get_collection()  # 컬렉션 가져오기
    ids = []  # 청크 ID를 저장할 리스트 초기화
    documents = []  # 청크 내용을 저장할 리스트 초기화
    embeddings = []  # 임베딩 벡터를 저장할 리스트 초기화
    metadatas = []  # 메타데이터를 저장할 리스트 초기화

    for chunk, embedded_chunk in zip(chunks, embedded_chunks):  # 청크와 임베딩된 청크를 순회하며 추가
        ids.append(f"chunk_{chunk.id}") # 청크 ID를 리스트에 추가
        documents.append(chunk.content)  # 청크 내용을 리스트에 추가
        embeddings.append(embedded_chunk['embedding'])  # 임베딩 벡터를 리스트에 추가
        metadatas.append({
            "chunk_id": chunk.id,  # 청크 ID를 메타데이터에 추가
            "document_id": chunk.document_id,  # 청크가 속한 문서 ID를 메타데이터에 추가
            "chunk_index": chunk.chunk_index,  # 청크 인덱스를 메타데이터에 추가
            "page_id" : chunk.page_id,  # 청크가 속한 페이지 ID를 메타데이터에 추가
            "page_title" : chunk.page_title,  # 청크가 속한 페이지 제목을 메타데이터에 추가
            "page_path" : chunk.page_path,  # 청크가 속한 페이지 경로를 메타데이터에 추가
        })

    collection.upsert(
        ids=ids,  # 청크 ID 리스트
        documents=documents,  # 청크 내용 리스트
        embeddings=embeddings,  # 임베딩 벡터 리스트
        metadatas=metadatas  # 메타데이터 리스트
    ) # ChromaDB 컬렉션에 청크와 임베딩된 데이터를 추가

    return collection  # 업데이트된 컬렉션 반환

def delete_document_vectors(document_id: int): # ChromaDB에서 청크 삭제
    collection = get_collection()  # 컬렉션 가져오기
    collection.delete(where={"document_id": document_id})  # 주어진 문서 ID 해당하는 청크 삭제

def get_vector_count() -> int: # ChromaDB에 저장된 벡터 수 조회
    collection = get_collection()  # 컬렉션 가져오기
    return collection.count()  # 컬렉션에 저장된 벡터 수 반환   


def search_vectors(query_embedding: list[float], top_k: int = 5, document_id: int | None = None) -> list[dict]: # 쿼리 임베딩 벡터를 기반으로 유사한 벡터 검색
    collection = get_collection()  # 컬렉션 가져오기

    if document_id is not None:  # 문서 ID가 주어진 경우
        results = collection.query(
            query_embeddings=[query_embedding],  # 쿼리 임베딩 벡터
            n_results=top_k,  # 반환할 상위 K개의 결과 수
            where={"document_id": document_id}  # 주어진 문서 ID에 해당하는 청크만 검색
        )  # ChromaDB에서 유사한 벡터 검색

    else:  # 문서 ID가 주어지지 않은 경우
        results = collection.query(
            query_embeddings=[query_embedding],  # 쿼리 임베딩 벡터
            n_results=top_k  # 반환할 상위 K개의 결과 수
        )  # ChromaDB에서 유사한 벡터 검색
    
    search_results = []
    for chunk_id, document, metadata, distance in zip(
        results['ids'][0], 
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    ): # 검색 결과를 순회하며 dict 생성(거리 내용 포함시킴)
        search_results.append({
            "id": metadata["chunk_id"],
            "document_id": metadata["document_id"],
            "chunk_index": metadata.get("chunk_index"),
            "content": document,
            "distance": distance,
            "page_id": metadata.get("page_id"),
            "page_title": metadata.get("page_title"),
            "page_path": metadata.get("page_path"),
        }) # 검색 결과를 리스트에 추가

    return search_results  # 검색 결과를 리스트로 반환
