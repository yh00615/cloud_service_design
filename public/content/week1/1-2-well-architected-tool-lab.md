---
title: 'AWS Well-Architected Tool 워크로드 평가'
week: 1
session: 2
awsServices:
  - AWS Well-Architected Tool
learningObjectives:
  - AWS Well-Architected Framework의 6가지 핵심 원칙(운영 우수성, 보안, 안정성, 성능 효율성, 비용 최적화, 지속 가능성)을 이해할 수 있습니다.
  - AWS Well-Architected Tool로 워크로드를 생성하고 평가할 수 있습니다.
  - 운영 우수성, 보안, 안정성 원칙을 평가하고 개선 계획을 수립할 수 있습니다.
  - 평가 결과 보고서를 생성하고 공유할 수 있습니다.
prerequisites:
  - AWS 기본 서비스 이해
  - 클라우드 아키텍처 기본 개념
---

이 실습에서는 AWS Well-Architected Tool을 사용하여 **QuickTable 레스토랑 예약 시스템**의 워크로드를 평가하고 아키텍처 개선 영역을 식별하는 방법을 학습합니다.

먼저 Well-Architected Tool에 접속하여 **QuickTable 3-Tier 아키텍처**를 워크로드로 생성한 후 **AWS Well-Architected Framework의 6가지 핵심 원칙**별로 질문에 답변합니다.:

1\. **운영 우수성 (Operational Excellence)**: 시스템 운영 및 모니터링  
2\. **보안 (Security)**: 데이터 및 시스템 보호  
3\. **안정성 (Reliability)**: 장애 복구 및 수요 대응  
4\. **성능 효율성 (Performance Efficiency)**: 리소스 효율적 사용  
5\. **비용 최적화 (Cost Optimization)**: 불필요한 비용 제거  
6\. **지속 가능성 (Sustainability)**: 환경 영향 최소화

각 원칙에 대한 모범 사례를 검토한 후 위험 수준을 확인하며, 개선 계획을 수립하는 전체 프로세스를 실습합니다.

이를 통해 AWS 모범 사례를 기반으로 아키텍처를 체계적으로 평가한 후 비즈니스 요구사항에 맞는 최적의 아키텍처를 설계하는 방법을 이해하게 됩니다.  
Week 1-3에서 작성할 QuickTable 아키텍처 다이어그램의 설계 원칙을 미리 학습하는 기회가 됩니다.

> [!DOWNLOAD]
> [week1-2-well-architected-guide.zip](/files/week1/week1-2-well-architected-guide.zip)
>
> - `quicktable-architecture-overview.md` - QuickTable 3-Tier 아키텍처 개요 및 구성 요소 설명 (VPC, 서브넷, ALB, EC2, RDS 구성)
> - `well-architected-checklist.md` - AWS Well-Architected Framework 6가지 원칙별 체크리스트 (QuickTable 시스템 현황 기반 평가 가이드)
>
> **관련 태스크:**
>
> - 태스크 1: AWS Well-Architected Tool 시작하기 (`quicktable-architecture-overview.md` 참고하여 워크로드 생성)
> - 태스크 2-7: 6가지 원칙 평가 (`well-architected-checklist.md` 참고하여 질문 답변)

> [!NOTE]
> 이 실습은 AWS 리소스를 생성하지 않으므로 비용이 발생하지 않습니다.

## 태스크 1: AWS Well-Architected Tool 시작하기

이 태스크에서는 AWS Well-Architected Tool에 접속한 후 새로운 워크로드를 생성합니다.

> [!NOTE]
> 워크로드는 비즈니스 가치를 제공하는 리소스와 코드의 집합입니다. 웹 애플리케이션, 모바일 앱 백엔드, 데이터 분석 파이프라인 등이 워크로드의 예입니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Well-Architected Tool`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Workloads**를 선택합니다.
3. 우측 상단의 [[Define workload]] 버튼을 클릭합니다.
   <img src="/images/week1/1-2-task1-step3-define-workload.png" alt="Well-Architected Tool의 Define workload 버튼" class="guide-img-md" />

> [!NOTE]
> [[Define workload]] 버튼은 드롭다운 형태로 표시될 수 있습니다. 이 경우 버튼을 클릭한 후 나타나는 메뉴에서 **Define workload**를 다시 선택합니다.
>
> 처음 Well-Architected Tool을 사용하는 경우 시작 화면이 표시될 수 있습니다. [[Get started]] 버튼을 클릭한 후 [[Define workload]]를 선택합니다.

4. **Name**에 `quicktable-web-application`을 입력합니다.
5. **Description**에 `QuickTable 레스토랑 예약 시스템 3-Tier 아키텍처 평가`를 입력합니다.
6. **Review owner**에 본인의 이름을 입력합니다.
7. **Environment**에서 `Production`을 선택합니다.
8. 아래로 스크롤하여 **Regions** 섹션으로 이동합니다.
9. **AWS Regions** 드롭다운을 클릭한 후 `Asia Pacific (Seoul) ap-northeast-2`를 선택합니다.
   <img src="/images/week1/1-2-task1-step9-region-selection.png" alt="Regions 섹션에서 AWS Region 선택" class="guide-img-md" />

> [!NOTE]
> **Regions** 섹션은 AWS Regions와 Non-AWS regions 두 부분으로 구성됩니다. 이 실습에서는 AWS 리전만 선택합니다.

10. **Account IDs**, **Application**, **Architectural design**, **Industry type**, **Industry** 필드는 선택사항이므로 비워둡니다.
11. 아래로 스크롤하여 **AWS Trusted Advisor** 섹션으로 이동합니다.
12. **AWS Trusted Advisor** 섹션은 선택사항이므로 활성화하지 않습니다.
13. **Jira** 섹션은 선택사항이므로 설정하지 않습니다.
    <img src="/images/week1/1-2-task1-step13-jira-section.png" alt="Jira 섹션 설정 화면" class="guide-img-md" />

14. 아래로 스크롤하여 **Tags** 섹션으로 이동합니다.
15. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `1-2`     |
| `CreatedBy` | `Student` |

   <img src="/images/week1/1-2-task1-step15-tags-section.png" alt="Tags 섹션에서 태그 추가" class="guide-img-md" />

16. [[Next]] 버튼을 클릭합니다.
17. **Apply profile** 단계에서 프로파일을 적용하지 않습니다.

> [!NOTE]
> **프로파일(Profile)**: 조직의 내부 표준이나 규정을 반영한 커스텀 질문 세트입니다. 이 실습에서는 프로파일을 적용하지 않고 기본 Well-Architected Framework 질문만 사용합니다.

18. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week1/1-2-task1-step18-apply-profile.png" alt="Apply profile 단계 화면" class="guide-img-md" />

19. **Apply lenses** 단계에서 **AWS Well-Architected Framework** 렌즈가 자동으로 선택되어 있는지 확인합니다.

> [!NOTE]
> **렌즈(Lens)**: 특정 산업이나 기술 영역에 맞춘 질문 세트입니다. AWS Well-Architected Framework 렌즈는 워크로드 생성 시 자동으로 적용됩니다. 한 워크로드에 최대 20개의 렌즈를 동시에 적용할 수 있습니다.

20. [[Define workload]] 버튼을 클릭하여 워크로드를 저장합니다.
    <img src="/images/week1/1-2-task1-step20-apply-lenses.png" alt="Apply lenses 단계에서 AWS Well-Architected Framework 렌즈 확인" class="guide-img-md" />

21. 워크로드가 생성되면 워크로드 상세 페이지로 이동합니다.

✅ **태스크 완료**: 워크로드가 생성되었습니다.

## 태스크 2: 운영 우수성 원칙 평가

이 태스크에서는 운영 우수성(Operational Excellence) 원칙을 평가합니다. 운영 우수성은 시스템을 효과적으로 운영하고 모니터링하며, 지속적으로 개선하는 능력을 의미합니다.

22. 워크로드 상세 페이지에서 [[Start reviewing]] 버튼을 클릭합니다.
   <img src="/images/week1/1-2-task2-step1-start-reviewing.png" alt="워크로드 상세 페이지의 Start reviewing 버튼" class="guide-img-md" />

> [!NOTE]
> 처음 평가를 시작하는 경우 [[Start reviewing]] 버튼이 표시됩니다. 이미 일부 평가가 진행된 경우에는 [[Continue reviewing]] 버튼으로 표시됩니다.

23. 왼쪽 네비게이션에서 **Operational Excellence**를 선택합니다.

> [!CONCEPT] 운영 우수성 원칙 (Operational Excellence Pillar)
> 운영 우수성은 비즈니스 가치를 제공하고 지속적으로 프로세스와 절차를 개선하는 능력입니다. 코드형 인프라(IaC), 자동화된 배포, 포괄적인 모니터링, 인시던트 대응 절차 등이 핵심 요소입니다.

> [!NOTE]
> **QuickTable 시스템 현황**: 단일 리전(ap-northeast-2) 배포, 3-Tier 아키텍처, ALB + EC2 2대 + RDS Multi-AZ, 수동 배포, 기본 모니터링, 소규모 팀 운영. 정답은 없으며, 시스템 상태에 대한 본인의 판단을 반영합니다.

24. 첫 번째 질문 **OPS 1. How do you determine what your priorities are?**를 확인합니다.
25. 다운로드한 `well-architected-checklist.md` 파일을 엽니다.
26. 파일에서 **1. 운영 우수성 (Operational Excellence)** 섹션을 찾습니다.
27. **QuickTable 적용 사항**의 **현재 구성**과 **개선 영역**을 확인합니다.

> [!NOTE]
> **예시: OPS 1 질문 답변 방법**
>
> 질문: "How do you determine what your priorities are?"
>
> QuickTable은 초기 단계 스타트업으로 다음과 같은 상황입니다:
>
> - 고객 예약 기능이 핵심 비즈니스 목표
> - 소규모 팀으로 운영 중
> - 명확한 우선순위 문서화는 아직 미흡
>
> **선택 예시:**
>
> - ✅ **Evaluate external customer needs**: 고객의 예약 요구사항을 평가하고 있음
> - ✅ **Evaluate compliance requirements**: 개인정보 보호 등 기본 규정 준수
> - ❌ **Evaluate governance requirements**: 아직 공식적인 거버넌스 프로세스 미수립
> - ❌ **Evaluate threat landscape**: 체계적인 위협 평가 프로세스 없음
>
> 이처럼 QuickTable의 현재 상태를 고려하여 실제로 구현된 항목만 선택합니다.
>
>    <img src="/images/week1/1-2-task2-ops1-example.png" alt="OPS 1 질문 답변 예시 화면" class="guide-img-sm" />

28. Well-Architected Tool 화면으로 돌아와 위 예시를 참고하여 해당하는 모범 사례를 선택합니다.
29. 필요한 경우 **Notes** 필드에 추가 설명을 입력합니다.

> [!TIP]
> 체크리스트 파일의 "현재 구성"에 나열된 항목은 선택하고, "개선 영역"에 나열된 항목은 선택하지 않습니다. 예를 들어, "CloudWatch 메트릭 수집"은 이미 구현되어 있으므로 관련 모범 사례를 선택하지만, "Infrastructure as Code 도입"은 아직 미구현이므로 선택하지 않습니다.

> [!TIP]
> 각 질문에는 "Info" 링크가 있어 모범 사례에 대한 자세한 설명을 확인할 수 있습니다. 체크리스트 파일과 Info 링크를 함께 참고하면 더 정확한 답변을 할 수 있습니다.

30. [[Next]] 버튼을 클릭하여 다음 질문으로 이동합니다.

> [!NOTE]
> **예시: OPS 7 질문 답변 방법**
>
> 질문: "How do you know that you are ready to support a workload?"
>
> QuickTable의 운영 준비 상태:
>
> - CloudWatch로 기본 메트릭 수집 중
> - ALB 헬스 체크 설정됨
> - 하지만 공식적인 운영 Runbook은 없음
> - 장애 대응 절차가 문서화되지 않음
>
> **선택 예시:**
>
> - ✅ **Ensure personnel capability**: 팀원들이 시스템 운영 방법을 알고 있음
> - ✅ **Ensure consistent review of operational readiness**: 배포 전 기본 체크리스트 확인
> - ❌ **Use runbooks to perform procedures**: 공식 Runbook 미작성
> - ❌ **Use playbooks to investigate issues**: 장애 대응 Playbook 미작성
>
> 이처럼 각 질문마다 QuickTable의 실제 상황을 반영하여 답변합니다.
>
>    <img src="/images/week1/1-2-task2-ops7-example.png" alt="OPS 7 질문 답변 예시 화면" class="guide-img-sm" />

31. 나머지 질문들도 동일한 방법으로 체크리스트 파일을 참고하여 답변합니다.
32. 모든 질문에 답변한 후 [[Save and exit]] 버튼을 클릭하거나, [[Next]] 버튼을 클릭하여 다음 원칙(보안)으로 이동합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

✅ **태스크 완료**: 운영 우수성 원칙 평가가 완료되었습니다.

## 태스크 3: 보안 원칙 평가

이 태스크에서는 보안(Security) 원칙을 평가합니다. 보안은 데이터와 시스템을 보호하고, 위협을 탐지하며, 보안 이벤트에 대응하는 능력을 의미합니다.

> [!CONCEPT] 보안 원칙 (Security Pillar)
> 보안 원칙은 데이터 기밀성과 무결성을 유지하고, 권한을 관리하며, 보안 이벤트를 탐지하는 능력을 다룹니다. 최소 권한 원칙, 다층 방어, 자동화된 보안 모범 사례 적용이 핵심입니다.

33. 왼쪽 네비게이션에서 **Security**를 선택합니다.
34. `well-architected-checklist.md` 파일에서 **2. 보안 (Security)** 섹션을 참고합니다.
35. QuickTable의 현재 구성(계층화된 보안 그룹, HTTPS, RDS 암호화 등)을 확인합니다.

> [!NOTE]
> **예시: SEC 5 질문 답변 방법**
>
> 질문: "How do you protect your network resources?"
>
> QuickTable의 네트워크 보안:
>
> - 계층화된 보안 그룹 (ALB-SG, Web-SG, DB-SG)
> - 프라이빗 서브넷에 애플리케이션과 데이터베이스 배치
> - ALB에서 HTTPS 종료
> - 하지만 AWS WAF는 미적용
>
> **선택 예시:**
>
> - ✅ **Create network layers**: 퍼블릭/프라이빗 서브넷 분리
> - ✅ **Control traffic at all layers**: 보안 그룹으로 계층별 트래픽 제어
> - ✅ **Implement inspection and protection**: ALB에서 HTTPS 종료
> - ❌ **Automate network protection**: AWS WAF 미적용
> - ❌ **Use AWS services for protection**: GuardDuty, Shield 미사용
>
>    <img src="/images/week1/1-2-task3-sec5-example.png" alt="SEC 5 질문 답변 예시 화면" class="guide-img-sm" />

> [!NOTE]
> **예시: SEC 8 질문 답변 방법**
>
> 질문: "How do you protect your data at rest?"
>
> QuickTable의 데이터 보호:
>
> - RDS 암호화 활성화 (저장 데이터 암호화)
> - 자동 백업 설정 (7일 보관)
> - 하지만 S3 버킷 암호화는 미설정
> - 암호화 키 관리는 AWS 관리형 키 사용
>
> **선택 예시:**
>
> - ✅ **Implement secure key management**: AWS 관리형 키 사용
> - ✅ **Enforce encryption at rest**: RDS 암호화 활성화
> - ✅ **Automate data at rest protection**: RDS 자동 암호화
> - ❌ **Enforce access control**: S3 버킷 정책 미설정
> - ❌ **Use mechanisms to keep people away from data**: Secrets Manager 미사용
>
>    <img src="/images/week1/1-2-task3-sec8-example.png" alt="SEC 8 질문 답변 예시 화면" class="guide-img-sm" />

36. 위 예시들을 참고하여 해당하는 모범 사례를 선택합니다.
37. 나머지 질문들도 동일한 방법으로 체크리스트 파일을 참고하여 답변합니다.
38. 모든 질문에 답변한 후 [[Save and exit]] 버튼을 클릭하거나, [[Next]] 버튼을 클릭하여 다음 원칙(안정성)으로 이동합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

✅ **태스크 완료**: 보안 원칙 평가가 완료되었습니다.

## 태스크 4: 안정성 원칙 평가

이 태스크에서는 안정성(Reliability) 원칙을 평가합니다. 안정성은 시스템이 장애를 복구하고, 수요 변화에 동적으로 대응하며, 구성 오류를 완화하는 능력을 의미합니다.

> [!CONCEPT] 안정성 원칙 (Reliability Pillar)
> 안정성 원칙은 워크로드가 의도한 기능을 올바르고 일관되게 수행하는 능력을 다룹니다. 장애 복구, 수요 변화 대응, 구성 오류 완화가 핵심입니다.

39. 왼쪽 네비게이션에서 **Reliability**를 선택합니다.
40. `well-architected-checklist.md` 파일에서 **3. 안정성 (Reliability)** 섹션을 참고합니다.
41. QuickTable의 현재 구성(Multi-AZ, RDS Multi-AZ, Auto Scaling 등)을 확인합니다.

> [!NOTE]
> **예시: REL 2 질문 답변 방법**
>
> 질문: "How do you plan your network topology?"
>
> QuickTable의 네트워크 구성:
>
> - VPC를 퍼블릭/프라이빗 서브넷으로 분리
> - 2개 가용 영역(ap-northeast-2a, 2c)에 리소스 분산
> - NAT Gateway를 통한 아웃바운드 트래픽 처리
> - 하지만 단일 리전만 사용 중
>
> **선택 예시:**
>
> - ✅ **Use highly available network connectivity for workload public endpoints**: ALB를 통한 고가용성 엔드포인트
> - ✅ **Provision redundant connectivity between private networks**: Multi-AZ 구성으로 중복 연결
> - ❌ **Ensure IP subnet allocation accounts for expansion**: 서브넷 확장 계획 미수립
> - ❌ **Prefer hub-and-spoke topologies over many-to-many mesh**: 단순 구조로 해당 없음
>
>    <img src="/images/week1/1-2-task4-rel2-example.png" alt="REL 2 질문 답변 예시 화면" class="guide-img-sm" />

> [!NOTE]
> **예시: REL 11 질문 답변 방법**
>
> 질문: "How do you design your workload to withstand component failures?"
>
> QuickTable의 장애 대응 설계:
>
> - RDS Multi-AZ로 데이터베이스 장애 자동 복구
> - ALB 헬스 체크로 비정상 인스턴스 제외
> - Auto Scaling으로 인스턴스 자동 교체
> - 하지만 애플리케이션 레벨 재시도 로직은 없음
>
> **선택 예시:**
>
> - ✅ **Monitor all components of the workload to detect failures**: CloudWatch로 모니터링
> - ✅ **Fail over to healthy resources**: ALB와 Auto Scaling으로 자동 장애 조치
> - ✅ **Automate healing on all layers**: RDS Multi-AZ 자동 복구
> - ❌ **Use bulkhead architectures**: 장애 격리 패턴 미적용
> - ❌ **Test reliability**: 정기적인 장애 복구 테스트 미실시
>
>    <img src="/images/week1/1-2-task4-rel11-example.png" alt="REL 11 질문 답변 예시 화면" class="guide-img-sm" />

42. 위 예시들을 참고하여 해당하는 모범 사례를 선택합니다.
43. 나머지 질문들도 동일한 방법으로 체크리스트 파일을 참고하여 답변합니다.
44. 모든 질문에 답변한 후 [[Save and exit]] 버튼을 클릭하거나, [[Next]] 버튼을 클릭하여 다음 원칙(보안)으로 이동합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

✅ **태스크 완료**: 안정성 원칙 평가가 완료되었습니다.

## 태스크 5: 나머지 원칙 자율 실습

이 태스크에서는 나머지 3가지 원칙(성능 효율성, 비용 최적화, 지속 가능성)을 자율적으로 평가합니다.

> [!NOTE]
> 이 실습에서는 운영 우수성, 보안, 안정성 3개 원칙을 중점적으로 평가했습니다. 나머지 3개 원칙도 동일한 방법으로 평가할 수 있습니다.

**자율 실습 가이드:**

### 성능 효율성 (Performance Efficiency)

> [!CONCEPT] 성능 효율성 원칙
> 성능 효율성은 컴퓨팅 리소스를 효율적으로 사용하여 시스템 요구사항을 충족하고, 수요 변화와 기술 발전에 따라 효율성을 유지하는 능력입니다.

45. 왼쪽 네비게이션에서 **Performance Efficiency**를 선택합니다.
46. `well-architected-checklist.md` 파일에서 **4. 성능 효율성 (Performance Efficiency)** 섹션을 참고합니다.
47. QuickTable의 현재 구성(ALB, Auto Scaling 등)과 개선 영역(ElastiCache, CloudFront 등)을 확인한 후 답변합니다.
48. 모든 질문에 답변한 후 [[Save and exit]] 버튼을 클릭하거나, [[Next]] 버튼을 클릭하여 다음 원칙(보안)으로 이동합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

### 비용 최적화 (Cost Optimization)

> [!CONCEPT] 비용 최적화 원칙
> 비용 최적화는 불필요한 비용을 제거하고, 가장 비용 효율적인 리소스를 선택하며, 시간 경과에 따라 지출을 최적화하는 능력입니다.

49. 왼쪽 네비게이션에서 **Cost Optimization**을 선택합니다.
50. `well-architected-checklist.md` 파일에서 **5. 비용 최적화 (Cost Optimization)** 섹션을 참고합니다.
51. QuickTable의 현재 구성(Auto Scaling, 리소스 태그)과 개선 영역(Reserved Instances, Savings Plans 등)을 확인한 후 답변합니다.
52. 모든 질문에 답변한 후 [[Save and exit]] 버튼을 클릭하거나, [[Next]] 버튼을 클릭하여 다음 원칙(보안)으로 이동합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

### 지속 가능성 (Sustainability)

> [!CONCEPT] 지속 가능성 원칙
> 지속 가능성은 클라우드 워크로드 실행의 환경 영향을 최소화하는 능력입니다. 에너지 효율, 리소스 활용 최적화, 탄소 배출 감소가 핵심입니다.

53. 왼쪽 네비게이션에서 **Sustainability**를 선택합니다.
54. `well-architected-checklist.md` 파일에서 **6. 지속 가능성 (Sustainability)** 섹션을 참고합니다.
55. QuickTable의 현재 구성(서울 리전, Auto Scaling)과 개선 영역(Graviton 인스턴스, Lambda 등)을 확인한 후 답변합니다.
56. [[Save and exit]] 버튼을 클릭합니다.

> [!NOTE]
> 버튼명은 콘솔 버전에 따라 "Save and exit", "Save", "Save and close"로 표시될 수 있습니다.

> [!TIP]
> 6가지 원칙을 모두 평가하면 Well-Architected Framework의 전체 관점에서 아키텍처를 검토할 수 있습니다.  
> 각 원칙 간의 트레이드오프 관계를 이해하는 것이 중요합니다.

✅ **태스크 완료**: 6가지 원칙 평가가 모두 완료되었습니다.

## 태스크 6: 평가 결과 확인 및 개선 계획

이 태스크에서는 평가 결과를 확인한 후 개선이 필요한 영역을 식별합니다. Well-Architected Tool은 각 원칙별로 위험 수준(높음, 중간, 없음)을 표시한 후 개선을 위한 권장 사항을 제공합니다. 대시보드에서 전체 워크로드의 상태를 한눈에 파악한 후 우선순위가 높은 개선 항목을 식별하여 체계적으로 아키텍처를 개선할 수 있습니다.

57. 워크로드 상세 페이지의 **Overview** 탭을 확인합니다.
58. **Workload overview** 섹션에서 **Overall questions answered**와 **Overall risks**를 확인합니다.

> [!NOTE]
> **Overall risks**: 전체 워크로드의 위험 수준을 요약하여 표시합니다.
>
> - ❌ **High risk**: 즉시 개선 필요
> - ⚠️ **Medium risk**: 개선 고려 필요

59. 아래로 스크롤하여 **Lenses** 섹션을 확인합니다.
60. **Lenses** 테이블에서 **AWS Well-Architected Framework** 렌즈를 클릭합니다.
   <img src="/images/week1/1-2-task6-step6-lens-overview.png" alt="Lenses 테이블에서 AWS Well-Architected Framework 렌즈 선택" class="guide-img-md" />

> [!NOTE]
> **마일스톤(Milestone)**: 워크로드 상세 페이지의 **Milestones** 탭에서 특정 시점의 평가 상태를 스냅샷으로 저장할 수 있습니다.

61. **Overview** 탭에서 전체 평가 결과를 확인합니다.
62. **Lens overview** 섹션에서 각 원칙별 답변 개수와 위험 수준을 확인합니다.
   <img src="/images/week1/1-2-task6-step6-pillars.png" alt="Lens overview 섹션의 각 원칙별 평가 결과" class="guide-img-md" />

> [!OUTPUT]
> **예상 출력** (답변에 따라 결과가 다르게 표시됩니다):
>
> **Lens overview** 섹션에 각 원칙이 다음과 같이 표시됩니다:
>
> ```
> Operational Excellence
> Questions answered: 2/11
> High risks: 5
> Medium risks: 3
>
> Security
> Questions answered: 0/11
> High risks: 4
> Medium risks: 2
>
> Reliability
> Questions answered: 0/13
> High risks: 3
> Medium risks: 4
>
> Performance Efficiency
> Questions answered: 0/5
> High risks: 2
> Medium risks: 1
>
> Cost Optimization
> Questions answered: 0/11
> High risks: 3
> Medium risks: 2
>
> Sustainability
> Questions answered: 0/6
> High risks: 2
> Medium risks: 1
> ```
>
> 💡 초기 단계 스타트업 시스템 특성상 High risk 항목이 다수 식별되는 것이 정상입니다. Infrastructure as Code 미도입, 공식 Runbook 부재, AWS WAF 미적용 등 개선 영역이 많습니다.

63. **Next risk to address** 섹션에서 다음으로 해결해야 할 위험 항목을 확인합니다.
   <img src="/images/week1/1-2-task6-step7-next-risk.png" alt="Next risk to address 섹션에서 다음 위험 항목 확인" class="guide-img-md" />

64. 위험 항목을 클릭하여 상세 내용과 권장 개선 사항을 확인합니다.
   <img src="/images/week1/1-2-task6-step8-risk-detail.png" alt="위험 항목의 상세 내용과 개선 권장 사항" class="guide-img-md" />

65. **Improvement plan** 탭을 선택합니다.
66. 개선이 필요한 위험 항목 목록을 확인합니다.

> [!NOTE]
> **Improvement plan** 탭에는 평가 중 식별된 위험 항목(High/Medium)이 자동으로 표시됩니다. 각 항목은 질문 제목, 위험 수준, 원칙, 개선 권장 사항을 포함합니다.

67. 각 항목의 위험 수준(High/Medium)과 개선 권장 사항을 검토합니다.
68. 우선순위가 높은 항목부터 개선 계획을 수립합니다.
    <img src="/images/week1/1-2-task6-step12-improvement-plan.png" alt="Improvement plan 탭의 위험 항목 목록" class="guide-img-md" />

> [!TIP]
> **개선 우선순위**: High risk 항목 우선, 빠른 효과(Quick Wins), 비용 대비 효과, 규제 요구사항 순으로 결정합니다.

> [!TIP]
> 개선 계획은 팀과 공유하여 체계적으로 아키텍처를 개선할 수 있습니다. 각 항목에 담당자와 우선순위를 지정하면 진행 상황을 추적하기 쉽습니다.

✅ **태스크 완료**: 평가 결과를 확인하고 개선 계획을 수립했습니다.

## 태스크 7: 보고서 생성 및 공유

이 태스크에서는 평가 결과를 보고서로 생성한 후 팀과 공유합니다. Well-Architected Tool은 전체 평가 결과, 위험 항목, 개선 권장 사항을 포함한 상세 보고서를 자동으로 생성합니다. 이 보고서를 경영진이나 이해관계자에게 공유하여 아키텍처 개선의 필요성을 설명한 후 예산과 리소스를 확보하는 데 활용할 수 있습니다.

69. 왼쪽 메뉴에서 **Workloads**를 선택합니다.
70. 워크로드 목록에서 `quicktable-web-application`을 선택합니다.
71. 상단의 [[Generate report]] 버튼을 클릭합니다.
   <img src="/images/week1/1-2-task7-step3-generate-report.png" alt="워크로드 목록에서 Generate report 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> **보고서 생성 위치**:
>
> - 워크로드 목록에서 워크로드를 선택한 후 [[Generate report]] 버튼 클릭
> - 또는 워크로드 상세 페이지에서 렌즈를 선택한 후 우측 상단의 **Properties** 섹션에서 [[Generate report]] 클릭
>
> 보고서는 렌즈별로 생성됩니다. 여러 렌즈를 적용한 경우 각 렌즈에 대해 별도의 보고서를 생성할 수 있습니다.

72. 보고서 생성이 시작됩니다.

> [!NOTE]
> 보고서 생성에 10-20초가 소요됩니다. 보고서는 PDF 형식으로 생성됩니다.
>
> **보고서 열람 방식**:
>
> - 브라우저 설정에 따라 새 탭에서 자동으로 열리거나 파일로 다운로드됩니다
> - 파일로 다운로드된 경우 PDF 뷰어에서 열어 확인합니다

73. 생성된 보고서를 확인합니다.

> [!NOTE]
> **보고서 내용**: 워크로드 개요, 각 원칙별 평가 결과, 위험 항목 상세 내용, 개선 권장 사항을 포함합니다.  
> 경영진 보고, 팀 공유, 규제 감사 자료로 활용할 수 있습니다.

74. 보고서를 팀원들과 공유합니다.

> [!TIP]
> 보고서는 AWS Well-Architected Tool에 접근 권한이 없는 이해관계자와 평가 결과를 공유할 때 유용합니다. 정기적으로 보고서를 생성하여 아키텍처 개선 진행 상황을 추적할 수 있습니다.

✅ **태스크 완료**: Well-Architected Tool을 사용하여 워크로드를 평가하고 보고서를 생성했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Well-Architected Tool에서 워크로드를 생성했습니다.
- 운영 우수성, 보안, 안정성 원칙을 평가했습니다.
- 성능 효율성, 비용 최적화, 지속 가능성 원칙을 자율적으로 평가했습니다.
- 위험 수준을 확인하고 개선 영역을 식별했습니다.
- 개선 계획을 수립했습니다.
- 평가 결과를 보고서(PDF 형식)로 생성하고 공유했습니다.

---

# 🗑️ 리소스 정리

> [!NOTE]
> Well-Architected Tool은 AWS 리소스를 생성하지 않으므로 비용이 발생하지 않습니다.
> 워크로드 데이터만 삭제하면 됩니다.

## 1단계: 생성된 워크로드 확인

실습에서 생성한 워크로드를 확인합니다.

75. AWS Management Console에 로그인한 후 상단 검색창에 `Well-Architected Tool`을 입력하고 선택합니다.
76. 왼쪽 메뉴에서 **Workloads**를 선택합니다.
77. 이 실습에서 생성한 `quicktable-web-application` 워크로드를 확인합니다.

> [!NOTE]
> 워크로드 목록에서 이름, 설명, 생성 날짜, 마지막 수정 날짜를 확인할 수 있습니다.

## 2단계: 워크로드 삭제

생성한 워크로드를 삭제합니다.

78. 워크로드 목록에서 `quicktable-web-application`을 선택합니다.
   <img src="/images/week1/1-2-cleanup-step2-delete-workload.png" alt="워크로드 목록에서 quicktable-web-application 선택 후 Delete workload 버튼" class="guide-img-md" />

79. [[Delete workload]] 버튼을 클릭합니다.
80. 확인 창에서 삭제할 내용을 확인합니다.

> [!NOTE]
> 확인 창에는 다음 내용이 표시됩니다:
>
> - Deletes the workload
> - Deletes all milestones associated with the workload
>
> 워크로드를 삭제하면 평가 결과, 개선 계획, 마일스톤 등 모든 데이터가 영구적으로 삭제됩니다. 필요한 경우 삭제 전에 보고서를 다운로드하여 보관합니다.

81. [[Delete]] 버튼을 클릭하여 삭제를 확정합니다.

<img src="/images/week1/1-2-cleanup-step2-confirm-delete.png" alt="워크로드 삭제 확인 창" class="guide-img-sm" />

## 3단계: 삭제 확인

워크로드가 삭제되었는지 확인합니다.

82. 워크로드 목록을 새로고침합니다.
83. `quicktable-web-application` 워크로드가 목록에서 사라졌는지 확인합니다.

> [!SUCCESS]
> 워크로드가 목록에 없으면 정상적으로 삭제되었습니다.

✅ **실습 종료**: 모든 워크로드 데이터가 정리되었습니다.

## 추가 학습 리소스

- [AWS Well-Architected Framework 백서](https://docs.aws.amazon.com/ko_kr/wellarchitected/latest/framework/welcome.html)
- [Well-Architected Tool 사용자 가이드](https://docs.aws.amazon.com/ko_kr/wellarchitected/latest/userguide/intro.html)
- [Well-Architected Labs](https://wellarchitectedlabs.com/)
- [AWS Architecture Center](https://aws.amazon.com/ko/architecture/)

## 📚 참고: AWS Well-Architected Framework 6가지 원칙

### 1. 운영 우수성 (Operational Excellence)

**핵심 개념:**

- 시스템을 효과적으로 운영하고 모니터링
- 지속적인 개선과 자동화
- 운영 절차 문서화 및 표준화

**주요 영역:**

- 조직 문화: DevOps, 실험 문화, 실패로부터 학습
- 운영 준비: 코드형 인프라(IaC), 자동화된 배포
- 운영 및 진화: 모니터링, 로깅, 지속적 개선

### 2. 보안 (Security)

**핵심 개념:**

- 데이터와 시스템 보호
- 자격 증명 및 액세스 관리
- 위협 탐지 및 인시던트 대응

**주요 영역:**

- 자격 증명 관리: AWS IAM, MFA, 임시 자격 증명
- 탐지 제어: AWS CloudTrail, Amazon GuardDuty, AWS Security Hub
- 인프라 보호: Amazon VPC, Amazon EC2 보안 그룹, AWS WAF
- 데이터 보호: 암호화, 백업, 데이터 분류

### 3. 안정성 (Reliability)

**핵심 개념:**

- 장애 복구 및 자동 복구
- 수요 변화에 동적 대응
- Multi-AZ 및 백업 전략

**주요 영역:**

- 기초: 서비스 한도, 네트워크 토폴로지
- 워크로드 아키텍처: 분산 시스템, 느슨한 결합
- 변경 관리: 자동화된 배포, 롤백 전략
- 장애 관리: 모니터링, 자동 복구, 재해 복구

### 4. 성능 효율성 (Performance Efficiency)

**핵심 개념:**

- 적절한 리소스 유형 및 크기 선택
- 성능 모니터링 및 최적화
- 새로운 기술 및 서비스 활용

**주요 영역:**

- 선택: 컴퓨팅, 스토리지, 데이터베이스, 네트워크
- 검토: 성능 테스트, 벤치마킹
- 모니터링: Amazon CloudWatch, AWS X-Ray
- 트레이드오프: 일관성 vs 지연 시간, 비용 vs 성능

### 5. 비용 최적화 (Cost Optimization)

**핵심 개념:**

- 불필요한 비용 제거
- 예약 인스턴스 및 Savings Plans 활용
- 비용 모니터링 및 분석

**주요 영역:**

- 비용 인식: 태깅, AWS Cost Explorer, 예산
- 비용 효율적인 리소스: 적절한 크기 조정, Spot 인스턴스
- 수요 및 공급 관리: Amazon EC2 Auto Scaling, 서버리스
- 시간 경과에 따른 최적화: 정기적인 검토, 새로운 서비스 활용

### 6. 지속 가능성 (Sustainability)

**핵심 개념:**

- 에너지 효율적인 리소스 사용
- 탄소 배출 최소화
- 환경 영향 측정 및 개선

**주요 영역:**

- 리전 선택: 재생 에너지 비율이 높은 리전
- 사용자 행동 패턴: 효율적인 데이터 전송, 캐싱
- 소프트웨어 및 아키텍처: 효율적인 코드, 서버리스
- 데이터 패턴: 데이터 수명 주기 관리, 중복 제거

### 마일스톤 (Milestone)

**마일스톤**은 특정 시점의 워크로드 평가 상태를 저장하는 스냅샷 기능입니다. 시간이 지남에 따라 아키텍처가 어떻게 개선되었는지 추적할 수 있습니다.

**마일스톤 생성 방법:**

- 워크로드 상세 페이지의 **Milestones** 탭에서 [[Create milestone]] 버튼 클릭
- 마일스톤 이름 입력 (예: `Initial Assessment`, `Q1 Review`, `Post-Migration`)
- 저장 후 해당 시점의 평가 결과가 스냅샷으로 보관됨

**활용 사례:**

- 초기 평가 기준선 설정
- 분기별 아키텍처 개선 진행 상황 추적
- 마이그레이션 전후 비교
- 규제 감사를 위한 이력 관리
- 팀 간 개선 성과 공유
