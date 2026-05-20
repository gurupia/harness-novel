import os
import sys

# 기본 퓨샷 데이터베이스
RAW_FEW_SHOT_DATA = [
    {
        "id": "ex1",
        "draft": "시우는 갑자기 지하수로의 문을 열었다. 그리고 안으로 들어갔다. 그곳에는 괴물이 서 있었고 시우는 그것을 보고 매우 놀랐다.",
        "corrected": "끼이익, 철문이 비명을 지르며 젖혀졌다. 시우는 한 걸음 내딛었다. 훅 끼치는 퀴퀴한 구리 냄새 속에, 지하수로 깊은 어둠 속 복안의 붉은 안광이 그를 쏘아보고 있었다. 등 뒤로 서늘한 소름이 돋아올랐다.",
        "points": "1. '갑자기', '그리고' 등 불필요한 접속사/부사 제거.\n2. 설명식 서술('놀랐다')을 감각적 묘사('구리 냄새', '붉은 안광', '서늘한 소름')로 치환."
    },
    {
        "id": "ex2",
        "draft": "그는 위상 코어 합선을 시도했다. 기계는 윙윙 소리를 내며 과열되기 시작했다. 이윽고 폭발하여 파편이 사방으로 튀었다.",
        "corrected": "지이익! 특수 인하기 끝에서 불꽃이 거칠게 튀었다. 위상 코어가 비명을 지르듯 터져 나가는 고주파 음이 고막을 짓눌렀다. 콰아아앙! 뜨거운 오존 연기와 함께 흩어진 금속 파편들이 사막의 황야 위로 쏟아져 내렸다.",
        "points": "1. 3중 감각 묘사(지이익 소리, 고주파 이명, 오존 탄 냄새) 결합.\n2. 기술 장치 작동 시 긴박감 있는 단문 구성."
    }
]

# Fallback용 단순 텍스트 유사도 매칭 엔진 (ChromaDB 로딩 실패 시 사용)
class FallbackVectorDB:
    def __init__(self):
        self.data = RAW_FEW_SHOT_DATA

    def get_common_words_count(self, str1, str2):
        # 단어 기준 단순 교집합 개수를 통한 유사도 산출
        words1 = set(str1.split())
        words2 = set(str2.split())
        return len(words1.intersection(words2))

    def query(self, query_text, n_results=1):
        # 공통 단어 수가 많은 순으로 정렬
        sorted_data = sorted(
            self.data,
            key=lambda x: self.get_common_words_count(query_text, x["draft"]),
            reverse=True
        )
        return sorted_data[:n_results]

# ChromaDB 및 Sentence-Transformers 초기화 시도
# ChromaDB 및 Sentence-Transformers 초기화 상태 변수
CHROMA_AVAILABLE = False
db_client = None
collection = None
_initialized = False

def _init_db():
    global CHROMA_AVAILABLE, db_client, collection, _initialized
    if _initialized:
        return
    _initialized = True

    # 환경변수 'USE_CHROMA'가 활성화되어 있지 않으면 로딩 없이 즉시 Fallback 사용
    # 이를 통해 PyTorch / SentenceTransformer 로드 및 다운로드 대기 병목(수초~수분)을 완벽히 방지합니다.
    if os.environ.get("USE_CHROMA", "False").lower() not in ("true", "1", "yes"):
        collection = FallbackVectorDB()
        CHROMA_AVAILABLE = False
        return

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        from chromadb.api.types import EmbeddingFunction
        
        # ChromaDB 커스텀 임베딩 함수 프로토콜 준수
        class TransformerEmbeddingFunction(EmbeddingFunction):
            def __init__(self):
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                
            def __call__(self, input_texts):
                embeddings = self.model.encode(input_texts)
                return [e.tolist() for e in embeddings]

        # ChromaDB 메모리 DB 초기화
        db_client = chromadb.Client()
        emb_fn = TransformerEmbeddingFunction()
        
        # 기존 컬렉션이 있다면 가져오고, 없으면 생성
        collection = db_client.get_or_create_collection(
            name="humanizer_few_shot",
            embedding_function=emb_fn
        )
        
        # 퓨샷 데이터 적재
        ids = [item["id"] for item in RAW_FEW_SHOT_DATA]
        documents = [item["draft"] for item in RAW_FEW_SHOT_DATA]
        metadatas = [{"corrected": item["corrected"], "points": item["points"]} for item in RAW_FEW_SHOT_DATA]
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        CHROMA_AVAILABLE = True
        print("[Info] ChromaDB & SentenceTransformer loaded successfully.")

    except Exception as e:
        # 라이브러리가 없거나, 네트워크 에러, C++ 컴파일 에러 발생 시 Fallback 작동
        print(f"[Warning] Failed to initialize ChromaDB ({e}). Switching to Fallback Vector Engine.", file=sys.stderr)
        collection = FallbackVectorDB()
        CHROMA_AVAILABLE = False

def get_few_shot_examples(target_draft, n_results=1):
    """
    타겟 초고와 가장 유사한 인간의 교정 사례를 검색하여 문자열 형식으로 반환합니다.
    """
    _init_db()  # 지연 초기화 수행
    examples_str = ""
    
    if CHROMA_AVAILABLE:
        try:
            results = collection.query(
                query_texts=[target_draft],
                n_results=n_results
            )
            # 결과 파싱
            for idx in range(len(results["ids"][0])):
                doc = results["documents"][0][idx]
                meta = results["metadatas"][0][idx]
                
                examples_str += f"### 사례 {idx + 1}\n"
                examples_str += f"* **초고 (기계어)**: {doc}\n"
                examples_str += f"* **정답 (인간 윤문)**: {meta['corrected']}\n"
                examples_str += f"* **교정 포인트**:\n{meta['points']}\n\n"
        except Exception as query_err:
            print(f"[Error] Chroma query failed ({query_err}), falling back.", file=sys.stderr)
            # 쿼리 실패 시 즉석 fallback 처리
            fallback_db = FallbackVectorDB()
            results = fallback_db.query(target_draft, n_results=n_results)
            for idx, item in enumerate(results):
                examples_str += f"### 사례 {idx + 1}\n"
                examples_str += f"* **초고 (기계어)**: {item['draft']}\n"
                examples_str += f"* **정답 (인간 윤문)**: {item['corrected']}\n"
                examples_str += f"* **교정 포인트**:\n{item['points']}\n\n"
    else:
        # Fallback 엔진 쿼리
        results = collection.query(target_draft, n_results=n_results)
        for idx, item in enumerate(results):
            examples_str += f"### 사례 {idx + 1}\n"
            examples_str += f"* **초고 (기계어)**: {item['draft']}\n"
            examples_str += f"* **정답 (인간 윤문)**: {item['corrected']}\n"
            examples_str += f"* **교정 포인트**:\n{item['points']}\n\n"
            
    return examples_str.strip()

if __name__ == "__main__":
    test_query = "시우는 갑자기 지하수로의 문을 열었다. 쇠냄새가 심하게 났다."
    print("--- Search Result for test query ---")
    print(get_few_shot_examples(test_query, n_results=1))
