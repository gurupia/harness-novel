---
description: 디버깅, 메모리 누수 탐지 및 보안 강화를 위한 글로벌 통합 워크플로우
---

# 🛡️ 글로벌 디버깅, 메모리 누수 및 보안 워크플로우

본 워크플로우는 전사적 혹은 모든 언어/플랫폼(C/C++, C#, Rust, TypeScript, Python 등)에 공통으로 적용되는 디버깅, 메모리 관리, 보안 취약점 점검을 위한 표준 절차 및 가이드라인입니다. 새로운 기능을 개발하거나 시스템을 리팩토링할 때 이 지침을 단계별로 점검하여 무결성과 일관성을 확보하십시오.

---

## 1. 🐛 디버깅 로드맵 (Debugging Strategy)

### 1.1 현상 파악 및 재현 (Reproduction)
- **로깅 및 컨텍스트 확보:** 에러 로그, 덤프(Dump) 파일, 스택 트레이스를 최우선으로 확보합니다. 현상이 발생한 브랜치, 빌드 버전, OS 환경을 기록합니다.
- **재현 환경 특정:** 이슈가 발생하는 정확한 조건(입력 데이터, 특정 UI 조작 순서, 타이밍 등)을 좁혀서 명세화합니다.
- **최소 재현 코드 (Minimal Reproducible Example):** 문제가 일어나는 최소 단위의 코드로 분리해 냅니다. 이 과정 중 50% 이상의 버그 원인이 밝혀집니다.

### 1.2 원인 분석 (Root Cause Analysis)
- **경계선 및 엣지 케이스 검토:**
  - Null 참조, 오프-바이-원(Off-by-one), 인덱스 범위 초과 확인.
  - 리소스 초기화 순서 문제 파악.
- **동시성 및 타이밍 문제 조사:**
  - 비동기 로직 내 교착 상태(Deadlock) 및 경쟁 상태(Race Condition) 여부를 조사합니다.
  - UI 스레드 모델 위반(예: 백그라운드 스레드에서 UI 업데이트)을 점검합니다.
- **진단 도구 투입:**
  - IDE 디버거를 통한 스텝 진입, 변수 조사.
  - 타겟 종속 도구 활용 (`dotnet-dump`, `WinDbg`, `gdb`, Chrome DevTools, Wireshark).

### 1.3 수정 및 검증 (Fix & Validate)
- **테스트 코드로 방어막 구축:** 버그 재발 방지를 위해 문제 상황을 재현하는 단위 테스트(Unit/Integration Test)를 우선 작성하여 실패를 확인합니다(TDD 접근).
- **안전한 로직 교체:** Side-effect를 검토한 후 구조적결함수정을 최우선시하여 로직을 픽스합니다.
- **전체 무결성 교차 검증:** 변경사항이 영향을 줄 수 있는 통합 테스트 스위트를 구동하여 회귀 버그(Regression)가 없음을 입증합니다.

---

## 2. 💧 메모리 누수 탐지 및 방어 (Memory Management)

### 2.1 예방 원칙 (Proactive Measures)
- **언어별 라이프사이클 준수:**
  - `C/C++`: 스마트 포인터(`std::unique_ptr`, `std::shared_ptr`) 및 RAII 패턴 강제.
  - `C# / .NET`: Unmanaged 리소스의 경우 `IDisposable` 패턴의 완벽한 연쇄 구현. `struct`, `Span<T>`를 활용한 힙 할당 최소화(Zero Allocation).
  - `Rust`: 소유권, 차용 규칙 엄수. 검증된 경계를 제외한 `unsafe` 사용 및 Raw Pointer 전달 금지.
- **이벤트 훅 오펀(Orphan) 방지:**
  - 객체가 파괴될 때 `+=` 또는 `addEventListener`로 할당된 이벤트 구독을 명시적으로 해제합니다. (C#: `-=` 또는 `WeakEventManager` 사용)

### 2.2 런타임 누수 모니터링 (Detection Tools)
- **스냅샷 & 델타분석:** 장기 구동 이후 베이스라인 메모리 프로파일보다 객체 수가 우상향하는지 관찰합니다. 
- **도구 활용:**
  - .NET: `dotMemory`, `dotnet-gcdump`, Visual Studio Diagnostic Tools.
  - C/C++/Rust: Valgrind, AddressSanitizer(ASan), LeakSanitizer.
  - 웹 클라이언트: Chrome DevTools Memory 패널 (Heap Allocation Timeline 기록).

### 2.3 조치 단계 (Mitigation)
1. 누수 발생 전-후의 Heap Snapshot을 취득하여 비교합니다.
2. 장기간 해제되지 않은 객체들의 **GC Root (참조 최상위 경로)**를 쫓아가 강결합을 확인합니다.
3. Static Cache, 전역 상태, 캡처된 클로저 등에 의한 불필요한 생명주기 연장을 끊어냅니다.
4. 필요시, 메모리 압박 시 수거되도록 유연한 캐시는 **약한 참조(Weak Reference)** 구조로 변경합니다.

---

## 3. 🔒 보안 취약점 점검 및 하드닝 (Security Hardening)

### 3.1 1단계: 철저한 입력 검증 (Zero Trust Input)
- **Guard Clauses 방어벽:** 클라이언트, 브라우저, 외부 파일, 네트워크에서 인입되는 모든 데이터의 타입, 범위, 길이를 즉각 검증하여 예외 처리합니다.
- **인젝션 방지:** SQL Query는 100% Parameterized 방식 전용(ORM 우선). 명령어 파라미터를 쉘에 전달할 때 철저히 이스케이프.
- **역직렬화 및 페이로드 검열:** 신뢰할 수 없는 데이터의 무조건적인 역직렬화를 피하고, 허용 가능 타입(Allow-list)을 명시적으로 제한합니다.

### 3.2 2단계: 접근 권한 통제 (Authorization & Authentication)
- **최소 권한의 원칙 (PoLP):** 
  - 앱/서비스 데몬 구동 시 Root/Admin 권한을 박탈하고 필요한 최소 권한만을 부여합니다.
  - 파일시스템 쓰기, 카메라 사용 등 자원에 접근할 때마다 검사합니다.
- **시크릿(Secret) 하드코딩 금지:** 코드 내 인증 토큰, 비밀번호, API 키를 절대 삽입하지 말고 안전한 비밀 보관소나 환경 변수(Vault, .env + `.gitignore`)를 사용합니다.

### 3.3 3단계: 인터페이스 및 통신 보안 (Transport Security)
- **암호화 통신 강제:** 모든 외부 네트워크 통신은 TLS 1.2/1.3 이상의 규격으로 암호화(`https://` 및 `wss://`)합니다.
- **데이터 인코딩 패치:** XSS (Cross Site Scripting)를 방어하기 위해 화면에 출력을 반영하기 전 철저한 Output Encoding을 진행합니다.

### 3.4 4단계: 컴파일 & 시스템 안전 (Binary & Dependency Security)
- **메모리 보호 기법 체득:** C/C++ 시스템 레벨 빌드 시 ASLR, DEP(NX), Stack Canaries(오버플로우 감지) 플래그를 활성화하여 릴리즈합니다.
- **공급망 보안 검사 (Supply Chain Audit):** 사용 중인 오픈소스(npm, NuGet, Cargo) 패키지에서 알려진 보안 결함이 없는지 CI 파이프라인에서 정기적으로 점검(`audit` 커맨드 등)하여 조치합니다.

---

**[사용 시 주의사항]**
이 글로벌 가이드라인은 특정 기술 부채나 취약점이 쌓이기 전, **코드 리뷰나 주요 설계 승인 단계에서 필수 확인 체크리스트**로 활용합니다. 이상 징후가 감지될 시 반드시 해당 단계로 역추적하여 근본 원인을 해제하십시오.
