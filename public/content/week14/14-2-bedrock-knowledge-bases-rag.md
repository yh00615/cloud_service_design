---
title: 'Amazon Bedrock Knowledge Bases 기반 RAG 구현'
week: 14
session: 2
awsServices:
  - Amazon Bedrock
  - Amazon S3
  - Amazon OpenSearch Serverless
learningObjectives:
  - RAG(Retrieval-Augmented Generation)의 개념과 벡터 임베딩 원리를 이해할 수 있습니다.
  - Amazon S3에 문서를 업로드하고 Amazon Bedrock Knowledge Base를 생성할 수 있습니다.
  - 벡터 임베딩을 생성하고 Amazon OpenSearch Serverless에 저장할 수 있습니다.
  - Amazon Bedrock Knowledge Base를 쿼리하고 RAG 기반 응답을 확인할 수 있습니다.

prerequisites:
  - Amazon S3 기본 사용 경험.
  - 생성형 AI 기본 개념 이해.
---

> [!IMPORTANT]
> **리전 설정 필수**: 이 실습은 **Asia Pacific (Seoul) ap-northeast-2** 리전에서 진행합니다.
>
> **권장 이유**:
>
> - 모든 Amazon Bedrock 모델(Claude Sonnet 4.6, Titan Text Embeddings V2 등)이 지원됩니다
> - Amazon OpenSearch Serverless가 서울 리전에서 지원됩니다
> - Knowledge Base와 Agent 통합 시 같은 리전을 사용해야 합니다
> - Week 14-3 Agent와 같은 리전에서 통합해야 합니다

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

이 데모에서는 Amazon Bedrock Knowledge Bases를 사용하여 RAG (Retrieval-Augmented Generation) 시스템을 구현합니다.
QuickTable 레스토랑의 메뉴, 영업 정보, FAQ 문서를 벡터 데이터베이스에 저장하고, 고객 질문에 대해 관련 문서를 검색한 후 생성형 AI로 정확한 답변을 생성하는 과정을 학습합니다.

다음 세션인 Week 14-3에서는 이 Knowledge Base를 Amazon Bedrock Agent와 통합하여 대화형 AI 챗봇을 완성합니다.

> [!CONCEPT] RAG (Retrieval-Augmented Generation)
> RAG는 생성형 AI의 한계를 극복하기 위한 아키텍처입니다.
>
> **LLM의 한계:**
>
> - 학습 데이터에 없는 최신 정보에 대해 답변하기 어렵습니다
> - 기업 내부 문서나 특정 도메인 지식에 접근할 수 없습니다
> - 잘못된 정보를 생성할 수 있습니다 (Hallucination)
>
> **RAG 동작 원리:**
>
> - **Retrieval (검색)**: 사용자 질문과 관련된 문서를 벡터 데이터베이스에서 검색합니다
> - **Augmentation (증강)**: 검색된 문서를 컨텍스트로 LLM에 제공합니다
> - **Generation (생성)**: LLM이 컨텍스트를 기반으로 정확한 답변을 생성합니다

> [!DOWNLOAD]
> [week14-2-knowledge-base-lab.zip](/files/week14/week14-2-knowledge-base-lab.zip)
>
> - `quicktable-menu.txt` - QuickTable 레스토랑 메뉴 정보
> - `quicktable-info.txt` - 영업 시간, 예약 정책, 위치 정보
> - `quicktable-faq.txt` - 자주 묻는 질문 (FAQ)
>
> **관련 태스크:**
>
> - 태스크 1: Amazon S3 버킷 생성 및 문서 업로드

## 태스크 1: Amazon S3 버킷 생성 및 레스토랑 문서 업로드

이 태스크에서는 Knowledge Base의 데이터 소스로 사용할 Amazon S3 버킷을 생성하고 QuickTable 레스토랑의 메뉴, 영업 정보, FAQ 문서를 업로드합니다.
Knowledge Base는 Amazon S3 버킷의 문서를 자동으로 읽어 벡터 임베딩으로 변환하여 OpenSearch Serverless에 저장합니다.

1. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
2. 상단 검색창에 `S3`을 입력하고 선택합니다.
3. [[Create bucket]] 버튼을 클릭합니다.
4. **Bucket name**에 `quicktable-kb-documents-{StudentId}`를 입력합니다. (예: `quicktable-kb-documents-20240001`)

> [!TIP]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.  
> 버킷 이름은 전 세계적으로 고유해야 합니다.

> [!NOTE]
> **Bucket namespace** 옵션이 표시될 수 있습니다.
>
> - **Global namespace (기본값)**: 버킷 이름이 전 세계 모든 AWS 계정에서 고유해야 합니다. 기존 S3 방식과 동일합니다.
> - **Account Regional namespace (권장)**: 버킷 이름이 내 계정 + 리전 내에서만 고유하면 됩니다. 다른 계정에서 같은 이름을 사용해도 충돌하지 않습니다.
>
> 이 실습에서는 기본값인 Global namespace를 사용합니다.

5. **AWS Region**이 `Asia Pacific (Seoul) ap-northeast-2`로 설정되어 있는지 확인합니다.
6. 아래로 스크롤하여 **Tags - optional** 섹션을 확인합니다.
7. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-2`    |
| `CreatedBy` | `Student` |

> [!NOTE]
> 나머지 설정은 기본값을 유지합니다.

8. [[Create bucket]] 버튼을 클릭합니다.
9. 생성한 버킷을 선택합니다.
10. [[Create folder]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task1-step10-create-folder.png" alt="Create folder 버튼 클릭" class="guide-img-md" />

11. **Folder name**에 `documents`를 입력합니다.
12. [[Create folder]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task1-step12-folder-created.png" alt="documents 폴더 생성" class="guide-img-md" />

> [!CONCEPT] 벡터 임베딩 (Vector Embedding)
> 벡터 임베딩은 텍스트를 숫자 배열로 변환하는 과정입니다.
> 의미가 유사한 텍스트는 벡터 공간에서 가까운 위치에 배치됩니다.
> 예: "강아지"와 "개"는 벡터 공간에서 가까운 위치에, "강아지"와 "자동차"는 먼 위치에 배치됩니다.
> Knowledge Base는 문서를 벡터로 변환하여 의미 기반 검색을 가능하게 합니다.

13. `documents` 폴더를 선택합니다.

    <img src="/images/week14/14-2-task1-step13-documents.png" alt="documents 폴더 선택" class="guide-img-md" />

14. 다운로드한 `week14-2-knowledge-base-lab.zip` 파일의 압축을 해제합니다.
15. [[Upload]] 버튼을 클릭합니다.
16. [[Add files]]를 클릭합니다.
17. 압축 해제한 폴더에서 3개 파일을 모두 선택합니다:
    - `quicktable-menu.txt`
    - `quicktable-info.txt`
    - `quicktable-faq.txt`
18. [[Upload]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task1-step18-upload.png" alt="Upload 버튼 클릭" class="guide-img-md" />

    <img src="/images/week14/14-2-task1-step18-uploaded.png" alt="파일 업로드 완료" class="guide-img-md" />

> [!OUTPUT]
> 3개의 문서 파일이 업로드됩니다.
> 여러 문서로 분리하면 RAG 시스템의 다중 문서 검색 효과를 더 잘 확인할 수 있습니다.
> 업로드된 파일: `quicktable-menu.txt`, `quicktable-info.txt`, `quicktable-faq.txt`

✅ **태스크 완료**: Amazon S3 버킷이 생성되고 QuickTable 레스토랑 문서가 업로드되었습니다.

> [!TIP] CLI로 확인
> CloudShell 또는 터미널에서 다음 명령어로 생성된 S3 버킷과 업로드된 파일을 확인할 수 있습니다:
>
> ```bash
> # 버킷 확인
> aws s3 ls | grep quicktable-kb
>
> # 업로드된 파일 확인
> aws s3 ls s3://quicktable-kb-documents-{StudentId}/documents/
> ```

## 태스크 2: Amazon Bedrock Knowledge Base 생성

이 태스크에서는 Amazon Bedrock Knowledge Base를 생성하고 Amazon S3 버킷을 데이터 소스로 연결합니다.
Knowledge Base는 문서를 자동으로 처리하여 벡터 데이터베이스에 저장하고, 사용자 질문에 대해 관련 문서를 검색할 수 있도록 합니다.

> [!NOTE]
> Amazon Bedrock에서는 모든 서버리스 Foundation Model에 대한 액세스가 자동으로 활성화되어 있습니다.
> Anthropic Claude 모델은 처음 사용 시 일회성 **Use case details** 양식 제출이 필요하지만, 14-1 실습에서 이미 완료한 경우 추가 제출 없이 바로 사용할 수 있습니다.

19. Amazon Bedrock 콘솔로 이동합니다.
20. 왼쪽 메뉴에서 **Build** > **Knowledge bases**를 선택합니다.
21. [[Create]] 드롭다운을 클릭합니다.
22. **Unstructured data** 섹션에서 `Knowledge Base with vector store`를 선택합니다.

    <img src="/images/week14/14-2-task2-step22-create-kb.png" alt="Knowledge Base with vector store 선택" class="guide-img-md" />

> [!NOTE]
> Create 드롭다운에는 다음 옵션이 표시됩니다:
>
> - **Unstructured data** > `Knowledge Base with vector store`: 문서 기반 RAG (이 실습에서 사용).
> - **Structured data** > `Structured data store`: 구조화된 데이터 쿼리.
>
> 이 실습에서는 TXT 문서를 벡터화하여 검색하므로 `Knowledge Base with vector store`를 선택합니다.

23. **Knowledge Base name**에 `quicktable-restaurant-kb`를 입력합니다.
24. **Knowledge Base description**에 `QuickTable restaurant menu and information knowledge base`를 입력합니다.
25. **IAM permissions**에서 `Create and use a new service role`을 선택합니다.
26. **Choose data source type**에서 `Amazon S3`가 선택되어 있는지 확인합니다.
27. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-2`    |
| `CreatedBy` | `Student` |

28. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task2-step28-next.png" alt="Knowledge Base 설정 후 Next" class="guide-img-md" />

> [!CONCEPT] Knowledge Base 아키텍처
> Knowledge Base는 다음 구성 요소로 이루어집니다:
>
> 1. **Data source**: 문서가 저장된 Amazon S3 버킷
> 2. **Embedding model**: 문서를 벡터로 변환하는 AI 모델
> 3. **Vector database**: 벡터를 저장하고 검색하는 데이터베이스 (OpenSearch Serverless)
> 4. **Foundation model**: 검색된 문서를 기반으로 답변을 생성하는 LLM

29. **Data source name**에 `s3-documents`를 입력합니다.
30. **S3 URI**에서 [[Browse S3]]를 클릭합니다.
31. `quicktable-kb-documents-{StudentId}` 버킷을 선택합니다. (예: `quicktable-kb-documents-20240001`)

    <img src="/images/week14/14-2-task2-step31-select-bucket.png" alt="S3 버킷 선택" class="guide-img-md" />

32. `documents` 폴더를 선택합니다.
33. [[Choose]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task2-step33-choose.png" alt="Choose 버튼 클릭" class="guide-img-md" />

> [!TIP]
> Amazon S3 URI를 직접 입력할 수도 있습니다: `s3://quicktable-kb-documents-{StudentId}/documents/`  
> (예: `s3://quicktable-kb-documents-20240001/documents/`)

34. **Parsing strategy**에서 `Amazon Bedrock default parser`가 선택되어 있는지 확인합니다.
35. **Chunking strategy**에서 `Default chunking`이 선택되어 있는지 확인합니다.
36. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task2-step36-next.png" alt="Data source 설정 후 Next" class="guide-img-md" />

> [!NOTE]
> Knowledge Base는 Amazon S3 버킷의 모든 파일을 자동으로 읽어 처리합니다.
> 지원 형식: TXT, PDF, MD, HTML, DOC, DOCX, CSV 등
> Chunking strategy는 Default 외에 Fixed size, Hierarchical, Semantic, No chunking을 선택할 수 있습니다.
> 이 실습에서는 Default chunking을 사용합니다.

37. **Embeddings model**에서 `Titan Text Embeddings V2`를 선택합니다.

    <img src="/images/week14/14-2-task2-step37-embeddings.png" alt="Titan Text Embeddings V2 선택" class="guide-img-md" />

    <img src="/images/week14/14-2-task2-step37-vector-store.png" alt="Vector store 설정" class="guide-img-sm" />

> [!CONCEPT] 임베딩 모델 선택
> Amazon Bedrock은 여러 임베딩 모델을 제공합니다:
>
> - **Titan Text Embeddings V2** (권장): Amazon 자체 모델, 다국어 지원 개선, 벡터 차원 설정 가능 (256/512/1024), OpenSearch Serverless와 호환성 우수
> - **Cohere Embed Multilingual v3**: 다국어 지원 우수, 한국어 임베딩 품질 높음
> - **Titan Embeddings G1 - Text**: 이전 세대, 영어 중심
>
> 이 실습에서는 OpenSearch Serverless 벡터 스토어와의 차원 호환성을 위해 Titan Text Embeddings V2를 사용합니다.

38. **Vector store** 섹션에서 다음을 설정합니다:
    - **Vector store creation method**: `Quick create a new vector store - Recommended` 선택 (기본값)
    - **Vector store type**: 드롭다운에서 `Amazon OpenSearch Serverless`를 선택합니다.

> [!NOTE]
> Quick create는 Amazon OpenSearch Serverless 컬렉션을 자동으로 생성합니다.  
> Vector store type으로 Amazon OpenSearch Serverless 외에도 Aurora PostgreSQL Serverless, Neptune Analytics, S3 Vectors 등을 선택할 수 있습니다.  
> 이 실습에서는 Amazon OpenSearch Serverless를 사용합니다.

> [!WARNING]
> Amazon OpenSearch Serverless는 비용이 발생하므로 실습 종료 후 반드시 삭제해야 합니다.

39. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task2-step39-next.png" alt="Embeddings 설정 후 Next" class="guide-img-md" />

40. 설정을 검토합니다.

    <img src="/images/week14/14-2-task2-step40-review.png" alt="Knowledge Base 설정 검토" class="guide-img-md" />

41. [[Create knowledge base]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task2-step41-create.png" alt="Create knowledge base 버튼 클릭" class="guide-img-sm" />

> [!NOTE]
> Knowledge Base 생성에 5~10분이 소요될 수 있습니다.  
> Amazon OpenSearch Serverless 컬렉션이 자동으로 생성되고 AWS IAM 역할이 구성됩니다.  
> 상태가 "Creating"에서 "Available"로 변경될 때까지 기다립니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

> [!TROUBLESHOOTING]
> **문제**: Knowledge Base 생성이 실패합니다.
>
> **원인**: Amazon OpenSearch Serverless 컬렉션은 생성되었지만 Knowledge Base 연결에 실패한 경우입니다.
>
> **해결**:
>
> 1. 실패한 Knowledge Base를 삭제합니다.
> 2. Amazon OpenSearch Service 콘솔 > **Serverless** > **Collections**에서 `bedrock-knowledge-base-`로 시작하는 컬렉션이 남아있으면 삭제합니다.
> 3. 처음부터 다시 Knowledge Base를 생성합니다.

✅ **태스크 완료**: Knowledge Base가 생성되었습니다.

> [!TIP] CLI로 확인
> CloudShell 또는 터미널에서 다음 명령어로 생성된 Knowledge Base를 확인할 수 있습니다:
>
> ```bash
> # Knowledge Base 목록 확인
> aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb']" --output table
>
> # Knowledge Base 상세 정보 확인
> KB_ID=$(aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb'].knowledgeBaseId" --output text)
> aws bedrock-agent get-knowledge-base --knowledge-base-id ${KB_ID}
>
> # OpenSearch Serverless 컬렉션 확인
> aws opensearchserverless list-collections --query "collectionSummaries[?starts_with(name,'bedrock-knowledge-base-')]" --output table
> ```

## 태스크 3: 데이터 소스 동기화

이 태스크에서는 Amazon S3 버킷의 문서를 Knowledge Base로 동기화합니다.
동기화 과정에서 문서가 청크(chunk)로 분할되고, 각 청크가 벡터로 변환되어 OpenSearch Serverless에 저장됩니다.

42. Knowledge Base 상세 페이지에서 **Data source** 섹션을 확인합니다.
43. `s3-documents` 데이터 소스를 선택합니다.

    <img src="/images/week14/14-2-task3-step43-datasource.png" alt="s3-documents 데이터 소스 선택" class="guide-img-md" />

44. [[Sync]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task3-step44-sync.png" alt="Sync 버튼 클릭" class="guide-img-md" />

> [!CONCEPT] 문서 청킹 (Chunking)
> 긴 문서를 작은 조각(chunk)으로 나누는 과정입니다.
> 각 청크는 독립적으로 벡터로 변환되어 저장됩니다.  
> 사용자 질문과 가장 관련성 높은 청크만 검색하여 LLM에 제공합니다.
> 기본 청크 크기: 300 토큰 (약 200-250 단어)

> [!NOTE]
> 동기화에 1-2분이 소요됩니다. 상태가 "Completed"로 변경될 때까지 기다립니다.  
> 동기화가 완료되면 **Sync history**에서 처리된 문서 수와 청크 수를 확인할 수 있습니다.  
> Status가 "Completed"이면 동기화가 성공한 것입니다.  
> Documents processed 수가 3으로 표시되면 3개 파일이 모두 처리된 것입니다.  
> Chunks created 항목은 콘솔 버전에 따라 표시되지 않을 수 있습니다.

45. **Sync history** 섹션에서 최근 동기화 결과를 확인합니다:
    - **Status**: `Complete`
    - **Source files**: 업로드한 문서 수 (예: 3)
    - **Added**: 추가된 문서 수
    - **Failed files**: `0` (실패 없음)

    <img src="/images/week14/14-2-task3-step45-sync-history.png" alt="Sync history 확인" class="guide-img-md" />

> [!NOTE]
> 동기화가 완료되면 Status가 "Complete"로 표시됩니다. Source files 수가 업로드한 문서 수와 일치하는지 확인합니다.

✅ **태스크 완료**: 데이터 소스가 동기화되었습니다.

> [!TIP] CLI로 확인
> CloudShell 또는 터미널에서 다음 명령어로 데이터 소스 동기화 상태를 확인할 수 있습니다:
>
> ```bash
> # Knowledge Base ID 확인
> KB_ID=$(aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb'].knowledgeBaseId" --output text)
>
> # 데이터 소스 목록 확인
> DS_ID=$(aws bedrock-agent list-data-sources --knowledge-base-id ${KB_ID} --query "dataSourceSummaries[0].dataSourceId" --output text)
> echo "Data Source ID: ${DS_ID}"
>
> # 동기화 작업 상태 확인
> aws bedrock-agent list-ingestion-jobs --knowledge-base-id ${KB_ID} --data-source-id ${DS_ID} --query "ingestionJobSummaries[0].{Status:status,StartedAt:startedAt,Statistics:statistics}" --output table
> ```

## 태스크 4: Knowledge Base 테스트

이 태스크에서는 Knowledge Base를 테스트하여 문서 검색과 답변 생성이 올바르게 작동하는지 확인합니다.
사용자 질문에 대해 관련 문서를 검색하고, 검색된 문서를 기반으로 정확한 답변을 생성하는 전체 RAG 프로세스를 경험합니다.

### 태스크 4.1: 기본 질문 테스트

46. Knowledge Base 상세 페이지에서 **Test knowledge base** 섹션으로 스크롤합니다.

    <img src="/images/week14/14-2-task4-step46-test-kb.png" alt="Test knowledge base 섹션" class="guide-img-md" />

47. **Select model**에서 추론 프로파일(inference profile)을 선택합니다 (예: `Anthropic Claude Sonnet 4.6` 또는 `Anthropic Claude Opus 4.6`).

    <img src="/images/week14/14-2-task4-step47-select-model.png" alt="모델 선택" class="guide-img-md" />

> [!CONCEPT] Foundation Model 선택과 추론 프로파일
> Claude 4.5 이상 모델은 추론 프로파일(inference profile)을 통해서만 호출할 수 있습니다.
> Knowledge Base 테스트 시 모델 선택 드롭다운에서 추론 프로파일이 표시됩니다.
>
> - **Claude Opus 4.6**: 최고 성능, 복잡한 질문에 최적 (2026년 2월 출시)
> - **Claude Sonnet 4.6**: 성능과 비용의 균형, 한국어 지원 우수 (권장, 2026년 2월 출시)
> - **Claude Haiku 4.5**: 빠른 응답 속도, 저렴한 비용
>
> 한국어 질문의 경우 Claude Sonnet 4.6 또는 Claude Opus 4.6이 권장됩니다.
> 추론 프로파일은 크로스 리전 라우팅을 지원하여 가용성과 처리량을 높여줍니다.

48. 질문 입력창에 다음을 입력합니다: `안심 스테이크 가격이 얼마인가요?`.
49. [[Run]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-task4-step49-run.png" alt="Run 버튼 클릭 및 응답 확인" class="guide-img-md" />

50. **Generated response** 섹션에서 답변을 확인합니다.

> [!OUTPUT]
>
> ```
> 안심 스테이크(200g)는 38,000원입니다.
> 미디엄 레어로 추천되며, 감자 퓨레와 구운 야채가 포함되어 있습니다.
> ```

51. 답변 아래의 **Details** 링크를 클릭하면 오른쪽에 해당 답변의 **Source chunks**가 표시됩니다.
52. 답변의 근거가 된 문서 청크 내용을 확인합니다.

> [!NOTE]
> Source chunks는 답변의 신뢰성을 보장합니다.
> 각 답변이 어떤 문서에서 나왔는지 추적할 수 있어 환각(hallucination)을 방지합니다.

✅ **하위 태스크 완료**: 기본 질문 테스트가 완료되었습니다.

### 태스크 4.2: 복잡한 질문 테스트

53. 질문 입력창에 다음을 입력합니다: `주말에 4명이 방문하려고 하는데, 주차가 가능하고 영업 시간은 언제까지인가요?`.
54. [[Run]] 버튼을 클릭합니다.
55. 답변을 확인합니다.

> [!OUTPUT]
>
> ```
> 주말 영업 시간은 11:00부터 23:00까지이며, 라스트 오더는 22:00입니다.
> 주차는 건물 지하 주차장을 이용하실 수 있으며, 2시간 무료 주차가 제공됩니다.
> 예약 가능 시간은 2시간이며, 최소 예약 인원은 2명입니다.
> ```

> [!NOTE]
> 예상 출력은 참고용이며, 실제 응답은 모델에 따라 다를 수 있습니다.
> 답변은 업로드한 문서의 내용만을 기반으로 생성됩니다.

56. **Details** 패널의 **Source chunks**에서 여러 문서 청크가 사용되었는지 확인합니다.

    <img src="/images/week14/14-2-task4-step56-source-chunks.png" alt="Source chunks 확인" class="guide-img-md" />

> [!CONCEPT] 다중 문서 검색
> RAG는 여러 문서 청크를 동시에 검색하여 복잡한 질문에 답변할 수 있습니다.
> 이 예시에서는 "영업 시간" 섹션과 "주차" 섹션, "예약 정책" 섹션을 모두 검색하여 종합적인 답변을 생성했습니다.

✅ **하위 태스크 완료**: 복잡한 질문 테스트가 완료되었습니다.

### 태스크 4.3: FAQ 기반 질문 테스트

57. 질문 입력창에 다음을 입력합니다: `배달 서비스가 가능한가요?`.
58. [[Run]] 버튼을 클릭합니다.
59. 답변을 확인합니다.

    <img src="/images/week14/14-2-task4-step59-faq-test.png" alt="FAQ 기반 질문 테스트 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> 현재 배달 서비스는 제공하지 않습니다.
> 매장 방문 또는 테이크아웃만 가능합니다.
> ```

> [!NOTE]
> 이 질문에 대한 답변은 `quicktable-faq.txt` 파일에 포함되어 있습니다.
> 실제 응답은 모델에 따라 다를 수 있습니다.

> [!CONCEPT] 환각 방지 (Hallucination Prevention)
> RAG의 핵심 장점은 환각을 방지하는 것입니다.
> 문서에 없는 정보에 대해서는 "모른다"고 답변하거나 추가 정보를 요청합니다.
> 일반 LLM은 학습 데이터를 기반으로 그럴듯한 거짓 정보를 생성할 수 있지만, RAG는 검색된 문서만을 기반으로 답변합니다.

✅ **태스크 완료**: Knowledge Base 테스트가 완료되었습니다.

> [!TIP] CLI로 확인
> CloudShell 또는 터미널에서 다음 명령어로 Knowledge Base에 직접 쿼리할 수 있습니다:
>
> ```bash
> # Knowledge Base ID 확인
> KB_ID=$(aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb'].knowledgeBaseId" --output text)
>
> # Knowledge Base 검색 (Retrieve - 문서 청크만 반환)
> aws bedrock-agent-runtime retrieve \
>   --knowledge-base-id ${KB_ID} \
>   --retrieval-query '{"text": "안심 스테이크 가격"}' \
>   --query "retrievalResults[].{Content:content.text,Score:score}" --output table
>
> # Knowledge Base 검색 + 답변 생성 (RetrieveAndGenerate)
> aws bedrock-agent-runtime retrieve-and-generate \
>   --input '{"text": "안심 스테이크 가격이 얼마인가요?"}' \
>   --retrieve-and-generate-configuration '{
>     "type": "KNOWLEDGE_BASE",
>     "knowledgeBaseConfiguration": {
>       "knowledgeBaseId": "'${KB_ID}'",
>       "modelArn": "arn:aws:bedrock:ap-northeast-2::foundation-model/anthropic.claude-sonnet-4-6-20250514-v1:0"
>     }
>   }'
> ```
>
> `retrieve` 명령은 관련 문서 청크만 반환하고, `retrieve-and-generate` 명령은 검색된 문서를 기반으로 LLM이 답변을 생성합니다.

## 마무리

다음을 성공적으로 수행했습니다:

- RAG (Retrieval-Augmented Generation) 아키텍처를 이해했습니다.
- Amazon Bedrock Knowledge Base를 생성하고 구성했습니다.
- QuickTable 레스토랑의 메뉴, 영업 정보, FAQ를 3개 문서로 분리하여 데이터 소스로 연결하고 동기화했습니다.
- 벡터 임베딩과 의미 기반 검색 원리를 학습했습니다.
- 생성형 AI와 지식 베이스를 통합하여 정확한 답변을 생성했습니다.
- 환각 방지와 Source attribution의 중요성을 이해했습니다.

이 Knowledge Base는 다음 세션인 Week 14-3에서 Amazon Bedrock Agent와 통합하여 QuickTable AI 챗봇의 핵심 구성 요소로 사용됩니다.

> [!IMPORTANT]
> Week 14-3에서 이 Knowledge Base를 사용하므로, 14-3 실습을 진행할 예정이라면 리소스를 유지하는 것을 권장합니다.
> 단, OpenSearch Serverless는 OCU당 시간당 약 $0.24 비용이 계속 발생하므로 주의합니다.
> 14-3 실습을 진행하지 않는다면 아래 리소스 정리 단계를 수행합니다.

<a id="cleanup"></a>

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!WARNING]
> 리소스 삭제 순서를 반드시 지켜야 합니다: **Knowledge Base → OpenSearch Serverless → S3** 순서로 삭제합니다.
> OpenSearch Serverless 컬렉션을 먼저 삭제하면 Knowledge Base가 벡터 데이터를 정리하지 못해 삭제 실패(DELETE_UNSUCCESSFUL) 상태에 빠질 수 있으며, 이 경우 복구가 매우 어렵습니다.

### 단계 1: 생성된 리소스 확인 (Tag Editor)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `14-2`
6. [[Search resources]] 버튼을 클릭합니다.

<img src="/images/week14/14-2-cleanup-step6-tag-search.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!OUTPUT]
> 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 단계 2: 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
8. Knowledge Base를 삭제합니다:

<img src="/images/week14/14-2-cleanup-step8-delete-kb.png" alt="Knowledge Base 삭제 CLI" class="guide-img-md" />

```bash
# Knowledge Base ID 확인
KB_ID=$(aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb'].knowledgeBaseId" --output text)
echo "Knowledge Base ID: ${KB_ID}"

# Knowledge Base 삭제
aws bedrock-agent delete-knowledge-base --knowledge-base-id ${KB_ID}
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='quicktable-restaurant-kb']" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

9. Amazon OpenSearch Serverless 컬렉션을 삭제합니다:

<img src="/images/week14/14-2-cleanup-step9-delete-oss.png" alt="OpenSearch Serverless 컬렉션 삭제 CLI" class="guide-img-md" />

```bash
# 컬렉션 ID 확인
COLLECTION_ID=$(aws opensearchserverless list-collections --query "collectionSummaries[?starts_with(name,'bedrock-knowledge-base-')].id" --output text)
echo "Collection ID: ${COLLECTION_ID}"

# 컬렉션 삭제
aws opensearchserverless delete-collection --id ${COLLECTION_ID}
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws opensearchserverless list-collections --query "collectionSummaries[?starts_with(name,'bedrock-knowledge-base-')]" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

10. Amazon OpenSearch Serverless 보안 정책을 삭제합니다:

    <img src="/images/week14/14-2-cleanup-step10-delete-policies.png" alt="OpenSearch Serverless 보안 정책 삭제 CLI" class="guide-img-md" />

```bash
# Data access policy 삭제
for POLICY_NAME in $(aws opensearchserverless list-access-policies --type data --query "accessPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text); do
  aws opensearchserverless delete-access-policy --name ${POLICY_NAME} --type data
  echo "Deleted data access policy: ${POLICY_NAME}"
done

# Encryption policy 삭제
for ENC_POLICY in $(aws opensearchserverless list-security-policies --type encryption --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text); do
  aws opensearchserverless delete-security-policy --name ${ENC_POLICY} --type encryption
  echo "Deleted encryption policy: ${ENC_POLICY}"
done

# Network policy 삭제
for NET_POLICY in $(aws opensearchserverless list-security-policies --type network --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text); do
  aws opensearchserverless delete-security-policy --name ${NET_POLICY} --type network
  echo "Deleted network policy: ${NET_POLICY}"
done
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws opensearchserverless list-access-policies --type data --query "accessPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')]" --output text
> aws opensearchserverless list-security-policies --type encryption --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')]" --output text
> aws opensearchserverless list-security-policies --type network --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')]" --output text
> ```
>
> 모두 출력이 없으면 삭제 완료입니다.

11. Amazon S3 버킷을 비우고 삭제합니다:

    <img src="/images/week14/14-2-cleanup-step11-delete-s3.png" alt="S3 버킷 삭제 CLI" class="guide-img-md" />

```bash
STUDENT_ID="20240001"
aws s3 rm s3://quicktable-kb-documents-${STUDENT_ID} --recursive
aws s3 rb s3://quicktable-kb-documents-${STUDENT_ID}
```

> [!NOTE]
> `STUDENT_ID`를 본인 학번으로 변경합니다.  
> 삭제를 확인하려면 `aws s3 ls | grep quicktable-kb`를 실행합니다. 출력이 없으면 삭제 완료입니다.

12. AWS IAM 역할을 삭제합니다:

```bash
# Knowledge Base 서비스 역할 삭제
KB_ROLE=$(aws iam list-roles --query "Roles[?starts_with(RoleName,'AmazonBedrockExecutionRoleForKnowledgeBase_')].RoleName" --output text)
if [ -n "${KB_ROLE}" ]; then
  POLICIES=$(aws iam list-attached-role-policies --role-name ${KB_ROLE} --query "AttachedPolicies[*].PolicyArn" --output text)
  for POLICY in ${POLICIES}; do
    aws iam detach-role-policy --role-name ${KB_ROLE} --policy-arn ${POLICY}
  done
  INLINE=$(aws iam list-role-policies --role-name ${KB_ROLE} --query "PolicyNames" --output text)
  for P in ${INLINE}; do
    aws iam delete-role-policy --role-name ${KB_ROLE} --policy-name ${P}
  done
  aws iam delete-role --role-name ${KB_ROLE}
  echo "Deleted: ${KB_ROLE}"
fi
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws iam list-roles --query "Roles[?starts_with(RoleName,'AmazonBedrockExecutionRoleForKnowledgeBase_')].RoleName" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

13. 옵션 1 완료 후 아래 **단계 3: 삭제 확인**으로 이동합니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

**Amazon Bedrock Knowledge Base 삭제**

13. Amazon Bedrock 콘솔로 이동합니다.
14. 왼쪽 메뉴에서 **Build** > **Knowledge bases**를 선택합니다.
15. `quicktable-restaurant-kb`를 선택합니다.
16. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step16-delete-kb.png" alt="Knowledge Base Delete 버튼 클릭" class="guide-img-md" />

17. `delete`를 입력하여 삭제를 확인합니다.
18. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step18-confirm-delete.png" alt="삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 삭제가 완료될 때까지 기다립니다.

> [!WARNING]
> Knowledge Base를 삭제해도 OpenSearch Serverless 컬렉션은 자동으로 삭제되지 않습니다.
> 반드시 아래 단계에서 컬렉션을 직접 삭제해야 합니다.

**Amazon OpenSearch Serverless 컬렉션 삭제**

19. 상단 검색창에 `OpenSearch`을 입력하고 선택합니다.
20. 왼쪽 메뉴에서 **Serverless** > **Collections**를 선택합니다.
21. Knowledge Base와 연결된 컬렉션이 남아있다면 선택 후 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step21-delete-collection.png" alt="OpenSearch Serverless 컬렉션 삭제" class="guide-img-md" />

22. 확인 창에서 `confirm`을 입력합니다.
23. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step23-confirm-collection.png" alt="컬렉션 삭제 확인" class="guide-img-sm" />

> [!WARNING]
> OpenSearch Serverless 컬렉션이 삭제되지 않으면 사용하지 않아도 지속적으로 비용이 부과됩니다.  
> 컬렉션이 존재하는 동안 매월 상당한 비용이 발생하므로 반드시 삭제 여부를 확인합니다.

**Amazon OpenSearch Serverless 보안 정책 삭제**

> [!WARNING]
> Knowledge Base 생성 시 OpenSearch Serverless에 보안 정책이 자동으로 생성됩니다.
> Knowledge Base를 삭제하거나 생성에 실패해도 이 정책들은 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

24. 왼쪽 메뉴에서 **Serverless** > **Security** > **Data access policies**를 선택합니다.
25. `bedrock-knowledge-base-` 로 시작하는 정책을 선택합니다.
26. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step26-delete-data-policy.png" alt="Data access policy 삭제" class="guide-img-md" />

27. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step27-confirm-data-policy.png" alt="Data access policy 삭제 확인" class="guide-img-sm" />

28. 왼쪽 메뉴에서 **Encryption policies**를 선택합니다.
29. `bedrock-knowledge-base-` 로 시작하는 정책을 선택합니다.
30. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step30-delete-encryption.png" alt="Encryption policy 삭제" class="guide-img-md" />

31. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.
32. 왼쪽 메뉴에서 **Network policies**를 선택합니다.
33. `bedrock-knowledge-base-` 로 시작하는 정책을 선택합니다.
34. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step34-delete-network.png" alt="Network policy 삭제" class="guide-img-md" />

35. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!TIP]
> CLI로 보안 정책이 남아있는지 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws opensearchserverless list-access-policies --type data --query "accessPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text
> aws opensearchserverless list-security-policies --type encryption --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text
> aws opensearchserverless list-security-policies --type network --query "securityPolicySummaries[?starts_with(name,'bedrock-knowledge-base-')].name" --output text
> ```
>
> 모두 출력이 없으면 삭제 완료입니다.

**Amazon S3 버킷 삭제**

36. Amazon S3 콘솔로 이동합니다.
37. `quicktable-kb-documents-{StudentId}` 버킷을 선택합니다. (예: `quicktable-kb-documents-20240001`)
38. [[Empty]] 버튼을 클릭합니다.
39. `permanently delete`를 입력합니다.
40. [[Empty]] 버튼을 클릭합니다.
41. 버킷을 선택합니다.
42. [[Delete]] 버튼을 클릭합니다.
43. 버킷 이름을 입력합니다.
44. [[Delete bucket]] 버튼을 클릭합니다.

**AWS IAM 역할 삭제**

45. 상단 검색창에 `IAM`을 입력하고 선택합니다.
46. 왼쪽 메뉴에서 **Roles**를 선택합니다.
47. 검색창에 `KnowledgeBase`를 입력합니다.
48. `AmazonBedrockExecutionRoleForKnowledgeBase_` 로 시작하는 역할을 선택합니다.
49. [[Delete]] 버튼을 클릭합니다.
50. 확인 창에서 역할 이름을 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Knowledge Base 생성 시 자동으로 생성된 IAM 역할입니다. Knowledge Base를 삭제해도 이 역할은 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

### 단계 3: 삭제 확인

51. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
52. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
53. **Regions**에서 `ap-northeast-2`를 선택합니다.
54. **Resource types**에서 `All supported resource types`를 선택합니다.
55. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `14-2`
56. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week14/14-2-cleanup-step56-verify.png" alt="삭제 확인 검색 결과" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.  
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon Bedrock Knowledge Bases 개발자 가이드](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [RAG 아키텍처 모범 사례](https://aws.amazon.com/ko/what-is/retrieval-augmented-generation/)
- [벡터 데이터베이스 개요](https://aws.amazon.com/ko/what-is/vector-databases/)

## 📚 참고: RAG 아키텍처 심화

### RAG vs 일반 LLM

**일반 LLM의 한계:**

- 학습 데이터 이후의 정보를 알 수 없음
- 기업 내부 문서나 개인 데이터에 접근 불가
- 환각(hallucination) 발생 가능 - 그럴듯한 거짓 정보 생성

**RAG의 장점:**

- 최신 정보 및 기업 문서 활용 가능
- 답변의 근거(source) 제공으로 신뢰성 향상
- 환각 방지 - 문서에 없는 정보는 "모른다"고 답변
- 문서 업데이트 시 재학습 불필요

### 벡터 검색 원리

**1단계: 임베딩 생성**

- 문서를 작은 청크로 분할
- 각 청크를 벡터(숫자 배열)로 변환
- 의미가 유사한 텍스트는 벡터 공간에서 가까운 위치에 배치

**2단계: 사용자 질문 임베딩**

- 사용자 질문도 동일한 방식으로 벡터로 변환
- 질문 벡터와 문서 벡터 간의 유사도 계산

**3단계: 관련 문서 검색**

- 코사인 유사도(cosine similarity)로 가장 관련성 높은 청크 검색
- 상위 K개 청크를 LLM에 컨텍스트로 제공 (기본 K=5)

**4단계: 답변 생성**

- LLM이 검색된 문서를 기반으로 답변 생성
- 문서에 없는 정보는 답변하지 않음

### Knowledge Base 구성 요소

**Data Source (데이터 소스):**

- Amazon S3 버킷, Confluence, SharePoint, Salesforce 등 지원
- 지원 형식: TXT, PDF, MD, HTML, DOC, DOCX, CSV, XLS, XLSX
- **동기화 방식**:
  - 수동: Sync 버튼 클릭
  - 자동(스케줄): 콘솔에서 Sync schedule 설정 (시간별/일별/주별)
  - 자동(이벤트): Amazon EventBridge + AWS Lambda로 Amazon S3 업로드 시 즉시 동기화

**Embedding Model (임베딩 모델):**

- Titan Text Embeddings V2: Amazon 자체 모델, 다국어 지원 개선, 벡터 차원 설정 가능 (256/512/1024), OpenSearch Serverless와 호환성 우수 (권장)
- Cohere Embed Multilingual v3: 다국어 지원 우수, 한국어 임베딩 품질 높음
- Titan Embeddings G1: 이전 세대, 영어 중심
- 벡터 차원: 1024 (Titan V2 기본값), 1024 (Cohere Multilingual v3)

**Vector Database (벡터 데이터베이스):**

- OpenSearch Serverless: 완전 관리형, 자동 스케일링, 서울 리전 지원
- 벡터 인덱스: HNSW (Hierarchical Navigable Small World)
- 검색 속도: 밀리초 단위

**Foundation Model (기반 모델):**

- Claude 4.5 이상 모델은 추론 프로파일(inference profile)을 통해서만 호출 가능
- Claude Sonnet 4.6: 최신 모델, 한국어 지원 우수 (권장, 2026년 2월 출시)
- Claude Opus 4.6: 최고 성능, 복잡한 작업에 최적 (2026년 2월 출시)
- Claude Haiku 4.5: 빠른 응답 속도, 저렴한 비용
- Amazon Nova Pro: AWS 자체 모델, 다국어 지원
- 추론 프로파일은 크로스 리전 라우팅을 지원하여 가용성과 처리량을 높여줌

### 청킹 전략

**고정 크기 청킹 (Fixed-size Chunking):**

- 기본 방식: 300 토큰 단위로 분할 (약 200-250 단어, 영어 기준)
- 한국어: 토큰당 단어 수가 영어와 다르므로 실제 단어 수는 다를 수 있음
- 장점: 간단하고 빠름
- 단점: 문맥이 끊길 수 있음

**의미 기반 청킹 (Semantic Chunking):**

- 문단, 섹션 단위로 분할
- 장점: 문맥 유지
- 단점: 청크 크기가 불균일

**계층적 청킹 (Hierarchical Chunking):**

- 문서 → 섹션 → 문단 계층 구조 유지
- 장점: 문서 구조 보존
- 단점: 복잡한 구현

### 검색 최적화

**하이브리드 검색:**

- 벡터 검색 + 키워드 검색 결합
- 의미 유사도와 정확한 키워드 매칭 모두 활용

**재순위화 (Reranking):**

- 검색된 청크를 다시 정렬
- 더 정확한 답변을 위해 상위 청크 선택

**메타데이터 필터링:**

- 문서 유형, 날짜, 작성자 등으로 필터링
- 검색 범위 축소로 정확도 향상

### 실무 활용 사례

**레스토랑 고객 지원 챗봇:**

- 메뉴, 영업 시간, 예약 정책을 Knowledge Base에 저장
- 고객 질문에 즉시 정확한 답변 제공
- 24/7 자동 응답으로 고객 만족도 향상
- QuickTable 예시: "비건 메뉴가 있나요?", "주차 가능한가요?", "단체 예약이 가능한가요?"

**기업 내부 검색:**

- 사내 문서, 정책, 프로세스를 Knowledge Base에 저장
- 직원이 필요한 정보를 빠르게 검색
- 온보딩 시간 단축

**법률/의료 문서 분석:**

- 방대한 법률 판례, 의료 논문을 Knowledge Base에 저장
- 전문가가 관련 사례를 빠르게 검색
- 의사결정 지원

### 비용 최적화

**임베딩 비용:**

- Titan Text Embeddings V2: 1,000 토큰당 $0.00002
- Cohere Embed Multilingual v3: 1,000 토큰당 $0.0001
- 100만 토큰 처리 시 Titan V2는 약 $0.02, Cohere는 약 $0.10

**벡터 데이터베이스 비용:**

- OpenSearch Serverless: OCU당 시간당 $0.24
- 프로덕션 환경: 최소 2 OCU (시간당 $0.48, 월 약 $346)
- 개발/테스트 환경: 0.5 OCU 단위 사용 가능 (시간당 $0.24부터)
- ⚠️ 실습 후 미삭제 시 지속적으로 비용 발생

**Foundation Model 비용:**

- Claude Sonnet 4.6: 1,000 입력 토큰당 $0.003, 1,000 출력 토큰당 $0.015
- 1,000 질문 처리 시 약 $5-10 (질문 길이에 따라)

**최적화 전략:**

- 청크 크기 조정으로 벡터 수 감소
- 캐싱으로 중복 질문 처리
- 배치 처리로 임베딩 비용 절감
