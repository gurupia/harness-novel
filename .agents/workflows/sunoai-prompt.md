---
description: Suno AI 노래 생성을 위한 보컬 및 편곡 프롬프트 작성 가이드
---

# Suno AI 보컬 및 편곡 프롬프트 작성 워크플로우

이 워크플로우는 뛰어난 퀄리티의 Suno AI 곡(발라드, 락, 동요 등)을 생성하기 위한 프롬프트 작성 지침입니다.  
**대상 버전:** Suno v5 (권장) / Studio 1.2+

> [!IMPORTANT]
> 스타일 프롬프트 설계의 상세 레퍼런스(GMIV 공식, 장르별 레시피, 메타태그 체계 등)는 `/sunoai-global-prompt` 워크플로우를 참조한다.

---

## 1. 보컬 스타일 (Vocal Style) 지정

명확한 보컬 캐릭터를 부여하여 곡의 감성을 결정합니다. AI가 이해하기 쉽도록 **영문으로 묘사**하는 것이 가장 좋습니다.

| 장르 | 보컬 프롬프트 예시 |
|------|-------------------|
| **발라드/감성** | `A soft female voice with angelic tones and gentle vibrato` |
| **락/고음** | `Powerful rock vocal with controlled rasp, strong chest voice projection, soaring high registers` |
| **재즈/R&B** | `A deep male voice like a jazz singer, soulful delivery with emotional depth` |
| **동요/몽환** | `A gentle and clear female vocal (like a lullaby singer) or a cheerful child's voice` |
| **힙합/트랩** | `Confident rap delivery with rhythmic flow, ad-libs, and autotuned hooks` |
| **일렉트로닉/팝** | `Bright, autotuned pop vocal with layered harmonies and crisp diction` |

### v5 Persona 활용

v5에서는 **Persona** 기능으로 마음에 드는 보컬 캐릭터를 저장·재사용할 수 있다:

1. 첫 곡 생성 시 3~5회 반복하여 최적의 보컬 톤을 확보
2. 해당 트랙의 보컬을 Persona로 저장 (이름·태그 지정)
3. 이후 곡 생성 시 동일 Persona를 선택 → 앨범 전체 보컬 일관성 유지
4. v5에서는 이전 버전의 보컬 드리프트(변조) 문제가 크게 개선됨

---

## 2. 악기 배치 및 편곡 (Instrumentation) 파악

곡의 진행(기승전결)에 따라 사용될 주요 악기를 구체적으로 나열합니다.

- **락발라드 예시:**  
  `Instrumentation: emotional piano, clean electric guitar arpeggios, warm strings, melodic lead guitar lines, and heavy distorted guitars during the chorus.`
- **동요 예시:**
  `Instrumentation includes warm piano chords, sparkling glockenspiel, soft string pads, and light, airy percussion.`
- **메탈/하드락 예시:**
  `Heavy distorted guitars, deep bass, wide strings, and explosive drums in the chorus.`

---

## 3. 구조와 메타태그 (Structure & Metatags) 활용

가사에 곡 구성(Song Structure) 태그를 명확히 구분하여 AI가 파트별 전개를 이해하도록 합니다.

- `[Verse 1]`, `[Verse 2]`: 곡의 도입부이자 스토리가 시작되는 파트 (잔잔함)
- `[Pre-Chorus]`: 클라이맥스로 상승하는 긴장감 조성 파트
- `[Chorus]`: 하이라이트 구간. 가장 감정이 폭발하는 멜로디 라인
- `[Bridge]`: 곡의 분위기 환기 및 기악 솔로 (예: `[Guitar Solo]`)
- `[Outro]`: 여운을 남기며 부드럽게 또는 강렬하게 맺음

> [!TIP]
> **v5 개선:** 콜백 프레이징과 가사 마커(`[Verse]`, `[Chorus]`)의 인식 정확도가 크게 향상되었으며, 메타태그 스태킹(`|`)도 더 안정적으로 처리합니다.

### `//` 인라인 지시문

가사 중간에 `//`로 시작하는 줄을 삽입하면, AI가 가사로 부르지 않고 **악기·에너지 변화 지시**로 처리합니다:

```
[Verse 1]
// Soft acoustic guitar only, intimate and quiet
달빛 아래 걸어가는 이 밤
차가운 바람이 볼을 스쳐도
```

---

## 4. 추천 Suno 세팅값 (v5 기준)

의도한 분위기를 극대화하기 위해 아래를 참고하여 패러미터를 조정합니다.

### 기본 파라미터

| 파라미터 | 정통 스타일 (발라드/락/팝) | 실험적 스타일 (앰비언트/아방가르드) |
|---------|--------------------------|--------------------------------------|
| **Weirdness** | `0.2 ~ 0.3` (안정적·예측 가능) | `15 ~ 35` (독특한 멜로디·창의적 해석) |
| **Style Influence** | `0.88 ~ 0.95` (프롬프트에 충실) | `0.75 ~ 0.95` |

### v5 Remaster 모드

| 모드 | 권장 장르 | 효과 |
|------|----------|------|
| **Subtle** | 발라드, 재즈, 어쿠스틱 | 원곡 뉘앙스 보존 + 미세 음질 개선 |
| **Normal** | 팝, 록, R&B, K-pop | 선명도·밸런스 향상, 보컬/악기 분리감 강화 |
| **High** | EDM, 메탈, 트랩, 신스웨이브 | 사운드 대폭 리터칭, 저음·고음 강화 |

### Stems Export

- **Pro 티어:** 2 Stems (Vocal + Instrumental) 
- **Premier 티어:** 최대 12 Stems (Vocal, Drums, Bass, Melody 등 개별 분리)
- DAW(Logic Pro, Ableton, FL Studio)로 내보내 정밀 믹싱·마스터링 가능

---

## 5. v5 Studio 연동 워크플로우

v5 Studio Timeline을 활용하면 **섹션 단위로 독립 생성·교체·재배치**가 가능하다.

### 권장 워크플로우

```
1. 전체 곡의 프롬프트(스타일 + 가사)를 먼저 설계
2. v5로 전체 곡을 3~5회 생성하여 최적 베이스 트랙 선별
3. Studio Timeline에서 불만족 섹션 식별
4. 해당 섹션만 Alternates로 대체 버전 생성 (5~10개)
5. 최적 테이크 선택 → 크로스페이드로 자연스럽게 연결
6. Add Vocals / Add Instrumental로 레이어 추가
7. Remaster (Subtle → Normal 단계적) 적용
8. Stems Export → DAW로 최종 마스터링
```

### Studio 1.2 고급 기능

| 기능 | 활용 |
|------|------|
| **Warp Markers** | 보컬 타이밍 미세 조정 |
| **Remove FX** | 드라이 시그널 추출 후 DAW에서 이펙트 재적용 |
| **Time Signature** | 3/4, 6/8, 5/4 등 변박자 곡 제작 |

---

## 6. 앨범 커버 이미지 프롬프트 (Album Cover Prompt)

곡의 전반적인 분위기와 가사 내용에 맞춰 앨범 커버 이미지를 생성할 수 있는 프롬프트를 함께 제안합니다. 이미지 생성 AI가 이해하기 쉽도록 시각적 요소를 구체적인 영문 키워드로 묘사합니다.

- **작성 항목:** 중심 피사체(Subject), 배경(Background), 색감(Color Palette), 분위기/조명(Mood/Lighting), 예술적 스타일(Art Style)
- **발라드/감성 예시:** `A lonely coffee cup on a wooden table by the window, rainy day, soft natural lighting, melancholic and cozy mood, muted cinematic colors, lo-fi aesthetic anime style`
- **락/EDM 예시:** `Abstract bursting neon lights over a dark cinematic sky, dynamic angles, energetic and powerful vibe, high contrast, vibrant colors, surreal digital art`

---

## 7. 산출물 관리 (Repository)

새로 만든 가사 및 프롬프트 문서는 다음 폴더 규칙에 맞게 저장합니다:
- 작성된 프롬프트나 가사 생성 전략은 `sunoai\sunoai-prompt` 폴더에 저장
- 순수 가사나 곡 결과물 기록은 `sunoai\sunoai-lyrics` 폴더에 저장
