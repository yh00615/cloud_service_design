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
> **리전 설정 필수**: 이 실습은 **US East (N. Virginia)** 또는 **US West (Oregon)** 리전에서 진행합니다.
>
> **권장 이유**:
>
> - 모든 Amazon Bedrock 모델(Claude 3.5 Sonnet, Titan Embeddings 등)이 지원됩니다
> - Knowledge Base와 Agent 통합 시 안정적입니다
> - Week 14-3 Agent와 같은 리전에서 통합해야 합니다

> [!WARNING]
> 이 데모는 AWS 리소스를 생성하며 다음 비용이 발생합니다.
>
> **예상 비용** (ap-northeast-2 리전 기준):
>
> | 리소스                | 타입       | 시간당 비용    | 월 비용 (24/7 운영 시) |
> | --------------------- | ---------- | -------------- | ---------------------- |
> | OpenSearch Serverless | 최소 2 OCU | 약 $0.48       | 약 $346                |
> | Knowledge Base 쿼리   | -          | 무료 티어 범위 | -                      |
>
> **⚠️ 중요**:
>
> - OpenSearch Serverless는 최소 2 OCU(인덱싱 1 + 검색 1)를 사용합니다
> - 실습 후 미삭제 시 월 약 $346의 비용이 지속적으로 발생합니다
> - 실습 종료 후 반드시 리소스를 삭제해야 합니다

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

1. AWS Management Console 우측 상단에서 리전을 **US East (N. Virginia) us-east-1** 또는 **US West (Oregon) us-west-2**로 설정합니다.

> [!IMPORTANT]
> **리전 선택 주의사항:**
>
> - 이 실습은 Amazon Bedrock이 지원되는 리전에서 진행해야 합니다
> - **권장 리전**: US East (N. Virginia) 또는 US West (Oregon) - 모든 모델 지원
> - **서울 리전(ap-northeast-2)**: 일부 모델(Claude 3.5 Sonnet 등)이 지원되지 않을 수 있습니다
> - Week 14-3 Agent와 통합하려면 같은 리전을 사용해야 합니다
>
> **모델 가용성 확인 방법:**
>
> 1. Amazon Bedrock 콘솔 → 왼쪽 메뉴 **Foundation models** → **Model catalog**
> 2. 사용하려는 모델(Claude 3.5 Sonnet, Titan Embeddings 등)이 현재 리전에서 사용 가능한지 확인
> 3. **Anthropic 모델(Claude)**: 첫 사용 시 Use case 양식 제출 필요 (즉시 승인)

2. 상단 검색창에 `S3`을 입력하고 선택합니다.
3. [[Create bucket]] 버튼을 클릭합니다.
4. **Bucket name**에 `quicktable-kb-documents-YOUR-INITIALS`을 입력합니다.

> [!TIP]
> `YOUR-INITIALS`를 본인의 이니셜로 변경합니다 (예: `quicktable-kb-documents-jdoe`).
> 버킷 이름은 전 세계적으로 고유해야 합니다.

5. **AWS Region**에서 `Asia Pacific (Seoul) ap-northeast-2`를 선택합니다.
6. 아래로 스크롤하여 **Tags - optional** 섹션을 확인합니다.
7. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-2`    |
| `CreatedBy` | `Student` |

8. 나머지 설정은 기본값을 유지합니다.
9. [[Create bucket]] 버튼을 클릭합니다.
10. 생성한 버킷을 선택합니다.
11. [[Create folder]] 버튼을 클릭합니다.
12. **Folder name**에 `documents`를 입력합니다.
13. [[Create folder]] 버튼을 클릭합니다.

> [!CONCEPT] 벡터 임베딩 (Vector Embedding)
> 벡터 임베딩은 텍스트를 숫자 배열로 변환하는 과정입니다.
> 의미가 유사한 텍스트는 벡터 공간에서 가까운 위치에 배치됩니다.
> 예: "강아지"와 "개"는 벡터 공간에서 가까운 위치에, "강아지"와 "자동차"는 먼 위치에 배치됩니다.
> Knowledge Base는 문서를 벡터로 변환하여 의미 기반 검색을 가능하게 합니다.

14. `documents` 폴더를 선택합니다.
15. 다운로드한 `week14-2-knowledge-base-lab.zip` 파일의 압축을 해제합니다.
16. [[Upload]] 버튼을 클릭합니다.
17. [[Add files]]를 클릭합니다.
18. 압축 해제한 폴더에서 3개 파일을 모두 선택합니다:
	- `quicktable-menu.txt`
	- `quicktable-info.txt`
	- `quicktable-faq.txt`
19. [[Upload]] 버튼을 클릭합니다.
20. 업로드가 완료될 때까지 기다립니다.

> [!NOTE]
> 3개의 문서 파일을 업로드했습니다.
> 여러 문서로 분리하면 RAG 시스템의 다중 문서 검색 효과를 더 잘 확인할 수 있습니다.

21. 업로드된 파일을 확인합니다:
	- `quicktable-menu.txt`
	- `quicktable-info.txt`
	- `quicktable-faq.txt`

✅ **태스크 완료**: Amazon S3 버킷이 생성되고 QuickTable 레스토랑 문서가 업로드되었습니다.

## 태스크 2: Amazon Bedrock Knowledge Base 생성

이 태스크에서는 Amazon Bedrock Knowledge Base를 생성하고 Amazon S3 버킷을 데이터 소스로 연결합니다.
Knowledge Base는 문서를 자동으로 처리하여 벡터 데이터베이스에 저장하고, 사용자 질문에 대해 관련 문서를 검색할 수 있도록 합니다.

> [!NOTE]
> Amazon Bedrock에서는 모든 Foundation Model에 대한 액세스가 기본적으로 활성화되어 있습니다.
> AWS Marketplace 권한만 있으면 바로 모델을 사용할 수 있으며, Cohere 및 Anthropic 모델의 경우 첫 사용 시 사용 사례 양식만 제출하면 됩니다.

22. Amazon Bedrock 콘솔로 이동합니다.
23. 왼쪽 메뉴에서 **Build** > **Knowledge bases**를 선택합니다.
24. [[Create knowledge base]] 버튼을 클릭합니다.
25. **Knowledge base name**에 `quicktable-restaurant-kb`를 입력합니다.
26. **Description**에 `QuickTable restaurant menu and information knowledge base`를 입력합니다.
27. **AWS IAM permissions**에서 `Create and use a new service role`을 선택합니다.
28. [[Next]] 버튼을 클릭합니다.

> [!CONCEPT] Knowledge Base 아키텍처
> Knowledge Base는 다음 구성 요소로 이루어집니다:
>
> 1. **Data source**: 문서가 저장된 Amazon S3 버킷
> 2. **Embedding model**: 문서를 벡터로 변환하는 AI 모델
> 3. **Vector database**: 벡터를 저장하고 검색하는 데이터베이스 (OpenSearch Serverless)
> 4. **Foundation model**: 검색된 문서를 기반으로 답변을 생성하는 LLM

29. **Data source name**에 `s3-documents`를 입력합니다.
30. **Amazon S3 URI**에서 [[Browse Amazon S3]]를 클릭합니다.
31. `quicktable-kb-documents-YOUR-INITIALS` 버킷을 선택합니다.
32. `documents` 폴더를 선택합니다.
33. [[Choose]] 버튼을 클릭합니다.

> [!TIP]
> Amazon S3 URI를 직접 입력할 수도 있습니다: `s3://quicktable-kb-documents-YOUR-INITIALS/documents/`

34. [[Next]] 버튼을 클릭합니다.

> [!NOTE]
> Knowledge Base는 Amazon S3 버킷의 모든 파일을 자동으로 읽어 처리합니다.
> 지원 형식: TXT, PDF, MD, HTML, DOC, DOCX, CSV 등

35. **Embeddings model**에서 `Cohere Embed Multilingual v3`를 선택합니다.

임베딩 모델을 선택합니다.

> [!CONCEPT] 임베딩 모델 선택
> Amazon Bedrock은 여러 임베딩 모델을 제공합니다:
>
> - **Cohere Embed Multilingual v3**: 다국어 지원 우수, 한국어 임베딩 품질 높음 (권장)
> - **Titan Embeddings G1 - Text**: 영어 중심, 한국어 지원 제한적
> - **Titan Embeddings V2**: 개선된 다국어 지원
>
> 한국어 문서의 경우 Cohere Embed Multilingual v3가 가장 적합합니다.

36. **Vector database**에서 `Quick create a new vector store`를 선택합니다.

> [!NOTE]
> Quick create는 OpenSearch Serverless 컬렉션을 자동으로 생성합니다.
> 최소 2 OCU(OpenSearch Compute Unit)를 사용하며 시간당 약 $0.48 비용이 발생합니다.
> 수동으로 생성하려면 "Use an existing vector store"를 선택할 수 있습니다.

37. [[Next]] 버튼을 클릭합니다.
38. 설정을 검토합니다.
39. [[Create knowledge base]] 버튼을 클릭합니다.

> [!NOTE]
> Knowledge Base 생성에 2-3분이 소요됩니다.
> OpenSearch Serverless 컬렉션이 자동으로 생성되고 AWS IAM 역할이 구성됩니다.

40. 상태가 "Creating"에서 "Active"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: Knowledge Base가 생성되었습니다.

## 태스크 3: 데이터 소스 동기화

이 태스크에서는 Amazon S3 버킷의 문서를 Knowledge Base로 동기화합니다.
동기화 과정에서 문서가 청크(chunk)로 분할되고, 각 청크가 벡터로 변환되어 OpenSearch Serverless에 저장됩니다.

41. Knowledge Base 상세 페이지에서 **Data source** 섹션을 확인합니다.
42. `s3-documents` 데이터 소스를 선택합니다.
43. [[Sync]] 버튼을 클릭합니다.

> [!CONCEPT] 문서 청킹 (Chunking)
> 긴 문서를 작은 조각(chunk)으로 나누는 과정입니다.
> 각 청크는 독립적으로 벡터로 변환되어 저장됩니다.
> 사용자 질문과 가장 관련성 높은 청크만 검색하여 LLM에 제공합니다.
> 기본 청크 크기: 300 토큰 (약 200-250 단어)

44. 동기화 상태가 "In progress"로 표시됩니다.
45. 상태가 "Completed"로 변경될 때까지 기다립니다 (1-2분 소요).

> [!NOTE]
> 동기화가 완료되면 **Sync history**에서 처리된 문서 수와 청크 수를 확인할 수 있습니다.
> Status가 "Completed"이면 동기화가 성공한 것입니다.
> Documents processed 수가 3으로 표시되면 3개 파일이 모두 처리된 것입니다.
> Chunks created 항목은 콘솔 버전에 따라 표시되지 않을 수 있습니다.

46. **Sync history** 섹션에서 최근 동기화 결과를 확인합니다.
47. **Documents processed**와 **Chunks created** 수를 확인합니다.

✅ **태스크 완료**: 데이터 소스가 동기화되었습니다.

## 태스크 4: Knowledge Base 테스트

이 태스크에서는 Knowledge Base를 테스트하여 문서 검색과 답변 생성이 올바르게 작동하는지 확인합니다.
사용자 질문에 대해 관련 문서를 검색하고, 검색된 문서를 기반으로 정확한 답변을 생성하는 전체 RAG 프로세스를 경험합니다.

### 태스크 4.1: 기본 질문 테스트

48. Knowledge Base 상세 페이지에서 **Test knowledge base** 섹션으로 스크롤합니다.
49. **Select model**에서 최신 Claude 모델을 선택합니다 (예: `Anthropic Claude Sonnet 4.6` 또는 `Anthropic Claude Opus 4.6`).

> [!CONCEPT] Foundation Model 선택
> Knowledge Base는 다양한 Foundation Model과 통합할 수 있습니다:
>
> - **Claude Opus 4.6**: 최고 성능, 복잡한 질문에 최적 (2026년 2월 출시)
> - **Claude Sonnet 4.6**: 성능과 비용의 균형, 한국어 지원 우수 (권장, 2026년 2월 출시)
> - **Claude Haiku 4.5**: 빠른 응답 속도, 저렴한 비용
>
> 한국어 질문의 경우 Claude Sonnet 4.6 또는 Claude Opus 4.6이 권장됩니다.

50. 질문 입력창에 다음을 입력합니다: `안심 스테이크 가격이 얼마인가요?`.
51. [[Run]] 버튼을 클릭합니다.
52. **Generated response** 섹션에서 답변을 확인합니다.

> [!OUTPUT]
>
> ```
> 안심 스테이크(200g)는 38,000원입니다.
> 미디엄 레어로 추천되며, 감자 퓨레와 구운 야채가 포함되어 있습니다.
> ```

53. **Source attribution** 섹션에서 답변의 근거가 된 문서를 확인합니다.
54. 문서 청크와 유사도 점수를 확인합니다.

> [!NOTE]
> Source attribution은 답변의 신뢰성을 보장합니다.
> 각 답변이 어떤 문서에서 나왔는지 추적할 수 있어 환각(hallucination)을 방지합니다.

✅ **하위 태스크 완료**: 기본 질문 테스트가 완료되었습니다.

### 태스크 4.2: 복잡한 질문 테스트

55. 질문 입력창에 다음을 입력합니다: `주말에 4명이 방문하려고 하는데, 주차가 가능하고 영업 시간은 언제까지인가요?`.
56. [[Run]] 버튼을 클릭합니다.
57. 답변을 확인합니다.

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

58. **Source attribution**에서 여러 문서 청크가 사용되었는지 확인합니다.

> [!CONCEPT] 다중 문서 검색
> RAG는 여러 문서 청크를 동시에 검색하여 복잡한 질문에 답변할 수 있습니다.
> 이 예시에서는 "영업 시간" 섹션과 "주차" 섹션, "예약 정책" 섹션을 모두 검색하여 종합적인 답변을 생성했습니다.

✅ **하위 태스크 완료**: 복잡한 질문 테스트가 완료되었습니다.

### 태스크 4.3: FAQ 기반 질문 테스트

59. 질문 입력창에 다음을 입력합니다: `배달 서비스가 가능한가요?`.
60. [[Run]] 버튼을 클릭합니다.
61. 답변을 확인합니다.

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

## 마무리

다음을 성공적으로 수행했습니다:

- RAG (Retrieval-Augmented Generation) 아키텍처를 이해했습니다
- Amazon Bedrock Knowledge Base를 생성하고 구성했습니다
- QuickTable 레스토랑의 메뉴, 영업 정보, FAQ를 3개 문서로 분리하여 데이터 소스로 연결하고 동기화했습니다
- 벡터 임베딩과 의미 기반 검색 원리를 학습했습니다
- 생성형 AI와 지식 베이스를 통합하여 정확한 답변을 생성했습니다
- 환각 방지와 Source attribution의 중요성을 이해했습니다

이 Knowledge Base는 다음 세션인 Week 14-3에서 Amazon Bedrock Agent와 통합하여 QuickTable AI 챗봇의 핵심 구성 요소로 사용됩니다.

> [!IMPORTANT]
> Week 14-3에서 이 Knowledge Base를 사용하므로, 14-3 실습을 진행할 예정이라면 리소스를 유지하는 것을 권장합니다.
> 단, OpenSearch Serverless는 시간당 약 $0.48 비용이 계속 발생하므로 주의합니다.
> 14-3 실습을 진행하지 않는다면 아래 리소스 정리 단계를 수행합니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `14-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### Amazon Bedrock Knowledge Base 삭제

8. Amazon Bedrock 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Orchestration** > **Knowledge bases**를 선택합니다.
10. `quicktable-restaurant-kb`를 선택합니다.
11. [[Delete]] 버튼을 클릭합니다.
12. `delete`를 입력하여 삭제를 확인합니다.
13. [[Delete]] 버튼을 클릭합니다.
14. 삭제가 완료될 때까지 기다립니다.

> [!WARNING]
> Knowledge Base를 삭제해도 OpenSearch Serverless 컬렉션은 자동으로 삭제되지 않습니다.
> 반드시 아래 단계에서 컬렉션을 직접 삭제해야 합니다.

#### OpenSearch Serverless 컬렉션 삭제 확인

15. 상단 검색창에 `OpenSearch`을 입력하고 선택합니다.
16. 왼쪽 메뉴에서 **Serverless** > **Collections**를 선택합니다.
17. Knowledge Base와 연결된 컬렉션이 삭제되었는지 확인합니다.
18. 컬렉션이 남아있다면 선택 후 [[Delete]] 버튼을 클릭합니다.
19. 확인 창에서 `confirm`을 입력합니다.
20. [[Delete]] 버튼을 클릭합니다.

> [!WARNING]
> OpenSearch Serverless 컬렉션이 삭제되지 않으면 시간당 $0.24 비용이 계속 발생합니다.
> 반드시 삭제 여부를 확인합니다.

#### Amazon S3 버킷 삭제

21. Amazon S3 콘솔로 이동합니다.
22. `quicktable-kb-documents-YOUR-INITIALS` 버킷을 선택합니다.
23. [[Empty]] 버튼을 클릭합니다.
24. `permanently delete`를 입력합니다.
25. [[Empty]] 버튼을 클릭합니다.
26. 버킷을 선택합니다.
27. [[Delete]] 버튼을 클릭합니다.
28. 버킷 이름을 입력합니다.
29. [[Delete bucket]] 버튼을 클릭합니다.

#### Amazon CloudWatch Log Group 삭제

30. 상단 검색창에 `CloudWatch`을 입력하고 선택합니다.
31. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
32. 검색창에 `bedrock`을 입력합니다.

> [!NOTE]
> Knowledge Base 사용량에 따라 Amazon CloudWatch Log Group이 생성되지 않을 수 있습니다.
> 검색 결과가 없으면 이 단계를 건너뜁니다.

33. Knowledge Base 관련 로그 그룹을 선택합니다.
34. **Actions** > `Delete log group(s)`를 선택합니다.
35. [[Delete]] 버튼을 클릭합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon Bedrock Knowledge Bases 개발자 가이드](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/knowledge-base.html)
- [RAG 아키텍처 모범 사례](https://aws.amazon.com/blogs/machine-learning/retrieval-augmented-generation/)
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

- Cohere Embed Multilingual v3: 다국어 지원 우수, 한국어 임베딩 품질 높음 (권장)
- Titan Embeddings G1: 영어 중심, 한국어 지원 제한적
- Titan Embeddings V2: 개선된 다국어 지원
- 벡터 차원: 1024 (Titan G1), 1024 (Cohere Multilingual v3)

**Vector Database (벡터 데이터베이스):**

- OpenSearch Serverless: 완전 관리형, 자동 스케일링
- 벡터 인덱스: HNSW (Hierarchical Navigable Small World)
- 검색 속도: 밀리초 단위

**Foundation Model (기반 모델):**

- Claude 3.5 Sonnet: 최신 모델, 한국어 지원 우수 (권장)
- Claude 3 Sonnet/Opus: 이전 세대, 안정적인 성능
- Titan Text: AWS 자체 모델, 영어 중심, 한국어 성능 제한적
- Llama 2: 오픈소스 모델

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

- Titan Embeddings G1: 1,000 토큰당 $0.0001
- Cohere Embed Multilingual v3: 1,000 토큰당 $0.0001
- 100만 토큰 처리 시 약 $0.10

**벡터 데이터베이스 비용:**

- OpenSearch Serverless: 시간당 $0.48 (최소 2 OCU 기준, ap-northeast-2 리전)
- 월 약 $346 (24/7 운영 시)
- ⚠️ 실습 후 미삭제 시 지속적으로 비용 발생

**Foundation Model 비용:**

- Claude 3 Sonnet: 1,000 입력 토큰당 $0.003, 1,000 출력 토큰당 $0.015
- 1,000 질문 처리 시 약 $5-10 (질문 길이에 따라)

**최적화 전략:**

- 청크 크기 조정으로 벡터 수 감소
- 캐싱으로 중복 질문 처리
- 배치 처리로 임베딩 비용 절감
