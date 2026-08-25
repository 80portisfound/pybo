from sqlalchemy.orm import Session
from crud.document import get_all_documents
from crud.chunk import get_chunks
from services.embedding import embed_chunks
from services.vector_store import add_chunks_to_vector_store, delete_document_vectors

def sync_document_vectors(db : Session, document_id: int):
    chunks = get_chunks(db, document_id)  # 주어진 document_id에 해당하는 청크들을 데이터베이스에서 가져옴
    if not chunks:
        return 0

    embedded_chunks = embed_chunks(chunks)  # 가져온 청크들을 임베딩 벡터로 변환
    add_chunks_to_vector_store(chunks, embedded_chunks)  # 임베딩된 청크들을 벡터 스토어에 추가

    return len(chunks)  # 처리된 청크의 수를 반환

def sync_all_document_vectors(db : Session):
    documents = get_all_documents(db)  # 데이터베이스에서 모든 문서를 가져옴

    total_chunks = 0 # 총 처리된 청크 수를 저장할 변수 초기화

    for document in documents:  # 각 문서에 대해 반복
        count  = sync_document_vectors(db, document.id)  # 각 문서의 청크들을 벡터 스토어에 동기화
        total_chunks += count  # 처리된 청크 수를 누적

    return total_chunks  # 총 처리된 청크 수를 반환
