# 세계관 AI 캐릭터 엔진
### World Character Engine

**State Management, Action Validation, and Result-driven Dialogue**

<p>
  <img src="https://img.shields.io/badge/Status-Partial%20Implementation-EAA12B?style=flat-square" alt="Partial Implementation">
  <img src="https://img.shields.io/badge/Python-Standard%20Library-3561D8?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Core-State%20%26%20Action-151F32?style=flat-square" alt="State and Action">
</p>

> 캐릭터의 현재 상태와 행동 조건을 코드로 관리하고,
> 제안된 행동을 검증한 뒤 **성공한 실행만 세계 상태에 반영하는**
> 세계관 AI 캐릭터용 상태·행동 엔진 프로젝트입니다.
>
> **Status: Partial Implementation — State / Action Core**  
> LLM과 장기 기억은 아직 연결하지 않았습니다.

---

## Why This Project

AI 캐릭터가 자연스럽게 대화하는 것만으로는
일관된 세계 상태를 유지하기 어렵습니다.

예를 들어 캐릭터가 실제로는 서류를 정리하지 못했는데
대사에서 이미 완료했다고 말하거나,
현재 위치와 맞지 않는 행동을 실행하면
대화와 세계 상태가 서로 어긋날 수 있습니다.

이 프로젝트에서는 다음 원칙을 먼저 코드로 구현했습니다.

```text
행동을 제안하는 것
≠
실제로 행동이 실행되는 것
≠
세계 상태가 변경되는 것
```

모델이 향후 행동을 제안하더라도,
실제 실행 가능 여부와 상태 변경은 Python 코드가 검증하도록 만드는 것이 목표입니다.

---

## Project Overview

| 항목 | 내용 |
|---|---|
| **기간** | 2026.09–현재 |
| **형태** | 개인 학습·구현 프로젝트 |
| **목표** | AI 캐릭터의 상태와 행동 실행을 코드로 검증할 수 있는 Core Engine 구현 |
| **현재 범위** | 상태 생성, 행동 허용 목록, 선행 조건 검사, 실행, 상태 변경, 결과 기반 대사 |
| **현재 기술** | Python Standard Library |
| **현재 상태** | State / Action Core 구현 |
| **테스트** | 회귀 테스트 13개 포함 |
| **미구현** | LLM, 장기 기억 검색, 사용자별 기억, DB, Web API |

---

## Problem → Implementation → Result

| Problem | Implementation | Current Result |
|---|---|---|
| 제안된 행동을 그대로 실행하면 지원하지 않는 행동까지 실행될 수 있음 | 허용 행동 목록과 `validate_action_proposal()` 분리 | 미지원·누락 행동 차단 |
| 행동 실패 후에도 상태가 변경될 수 있음 | 성공 여부 확인 후에만 상태 변경 | Tool 실패 시 기존 상태 유지 |
| 현재 상태와 맞지 않는 행동이 실행될 수 있음 | 행동별 선행 조건 검사 | 잘못된 장소·작업 중 상태에서 실행 거절 |
| 같은 행동이 중복 실행될 수 있음 | 현재 상태를 이용해 완료·이동 여부 확인 | 서류 정리 및 이동 중복 차단 |
| 실행 결과와 캐릭터 대사가 다를 수 있음 | 검증된 실행 결과를 대사 생성 입력으로 사용 | 성공·실패 결과에 맞는 대사 반환 |
| 테스트 간 상태가 섞일 수 있음 | 테스트마다 새로운 초기 상태 생성 | 독립적인 테스트 상태 유지 |

---

## System Overview

현재 구현 흐름은 다음과 같습니다.

```text
Structured Action Proposal
↓
Action Allowlist Validation
↓
State Preconditions
↓
Action Execution
↓
Success Check
↓
State Update
↓
Result-driven Dialogue
```

핵심 원칙:

```text
Proposal
→ Validation
→ Execution
→ Verified Result
→ State Change
→ Response
```

상태 변경은 실행이 성공한 뒤에만 수행합니다.

---

## Technical Details

<details open>
<summary><b>01 | Character State</b></summary>

<br>

새로운 세션이나 테스트마다 독립적인 초기 상태를 생성합니다.

현재 상태 예시는 다음과 같습니다.

```python
{
    "location": "집무실",
    "activity": "대기",
    "report_reviewed": True,
    "outfit_arranged": True,
    "documents_organized": False,
}
```

현재 상태는 문자열과 Boolean 값으로 구성된 작은 MVP입니다.

</details>

<details>
<summary><b>02 | Action Validation</b></summary>

<br>

현재 허용 행동은 다음 두 가지입니다.

```text
organize_documents
move_to_audience_room
```

`validate_action_proposal()`은
제안된 행동이 지원되는 행동인지 먼저 확인합니다.

```text
Action Missing
→ Reject

Unknown Action
→ Reject

No Action
→ Accept without execution

Allowed Action
→ Dispatch
```

검증 단계에서는 상태를 변경하지 않습니다.

</details>

<details>
<summary><b>03 | Preconditions and State Change</b></summary>

<br>

각 행동은 현재 상태에 따라 실행 가능 여부를 확인합니다.

예를 들어 접견실 이동은 다음 조건이 필요합니다.

```text
현재 위치 = 집무실
현재 활동 = 대기
보고서 검토 완료
의복 정리 완료
서류 정리 완료
```

서류 정리는 다음 경우 실행하지 않습니다.

```text
이미 완료됨
잘못된 장소
다른 작업 중
Tool 실행 실패
```

실행이 실패하면 상태를 변경하지 않습니다.

</details>

<details>
<summary><b>04 | Result-driven Dialogue</b></summary>

<br>

행동 함수의 실행 결과를 먼저 확정한 뒤
그 결과를 캐릭터 대사로 변환합니다.

```text
Action Result
↓
success / reason
↓
Dialogue
```

예:

```text
completed
→ "서류 정리를 마쳤어요."

tool_failed
→ "서류를 정리하지 못했어요."

move_not_allowed
→ "아직 접견실로 이동할 수 없어요."
```

향후 LLM을 연결하더라도
실제로 검증되지 않은 행동을 완료했다고 표현하지 않도록
이 경계를 유지하는 것이 목표입니다.

</details>

---

## Run and Verify

별도 패키지 설치 없이 Python으로 실행할 수 있습니다.

```bash
python test_character_engine.py
```

현재 테스트 파일에는 **13개의 회귀 테스트**가 포함되어 있습니다.

검증 항목:

- 서류 정리 성공 및 상태 변경
- Tool 실패 시 상태 유지
- 완료 행동 중복 실행 차단
- 잘못된 장소에서 실행 차단
- 작업 중 행동 실행 차단
- 미지원 행동 거부
- `action` 필드 누락 처리
- 행동 없는 입력 처리
- 이동 선행 조건 확인
- 중복 이동 차단
- 실행 결과에 따른 대사 확인
- 거절·실패 시 상태 불변
- 두 Turn의 상태 연결

---

## Project Structure

```text
world-character-engine/
├── character_engine.py
├── test_character_engine.py
├── PROGRESS.md
├── docs/
│   ├── MISSION-01.md
│   └── ROUND-01-LEARNING-GUIDE.md
├── .gitignore
└── README.md
```

---

## Current Scope and Limitations

### Current Scope

- 독립적인 초기 Character State 생성
- 행동 Allowlist
- 행동 제안 검증
- 행동별 선행 조건 검사
- 성공 여부 기반 상태 변경
- 실패·중복 행동 차단
- 실행 결과 기반 캐릭터 대사
- 두 Turn 간 상태 연결
- 13개 회귀 테스트

### Limitations

- 현재 행동은 2종만 구현되어 있습니다.
- 현재 상태는 메모리 내 Python Dictionary입니다.
- LLM을 호출하지 않습니다.
- 사용자 자연어를 구조화 행동으로 변환하지 않습니다.
- 최근 대화 Context 관리가 없습니다.
- 장기 기억 저장·검색이 없습니다.
- 사용자별 기억 격리가 없습니다.
- Database가 연결되어 있지 않습니다.
- Web API가 없습니다.
- 현재 테스트는 결정론적 State / Action Core만 검증합니다.
- LLM 응답 품질이나 기억 검색 성능을 검증한 결과가 아닙니다.

### Next Steps

```text
사용자 입력
→ 구조화된 행동 제안
→ 기존 Action Validator 연결
→ OpenAI API Structured Output
→ 최근 대화 상태
→ 장기 기억 저장·검색
→ 사용자별 기억 분리
→ API / Service Interface
```

각 단계는 기존 검증기와 실행기를 우회하지 않는 방향으로 확장할 예정입니다.

---

## What This Project Demonstrates

- 캐릭터 상태와 행동 실행 책임을 분리한 경험
- 행동 제안과 실제 실행을 구분한 설계 경험
- Allowlist 기반 행동 검증 구현 경험
- 현재 상태에 따른 행동 선행 조건 구현 경험
- 실행 실패 시 상태를 보존하는 처리 경험
- 중복 행동을 상태를 이용해 차단한 경험
- 실행 결과와 사용자에게 보여주는 응답을 연결한 경험
- 상태 변경을 포함한 작은 엔진을 회귀 테스트로 검증한 경험
- 향후 LLM을 연결하더라도 코드 검증 계층을 유지하도록 경계를 설계한 경험

---

## Contact

- Developer: 김수진
- GitHub: https://github.com/lightleaping
- Email: workingskyroad@gmail.com
