# 알고리즘 문제 풀이 시스템

이 시스템은 대기업 코딩테스트 수준의 알고리즘 문제를 체계적으로 학습하고 관리할 수 있는 종합적인 플랫폼입니다.

## 🚀 주요 기능

### 1. 문제 관리 시스템
- **표준화된 문제 데이터 구조**: 모든 플랫폼의 문제를 통일된 형식으로 관리
- **다중 플랫폼 지원**: LeetCode, CodeForces, 백준 등 다양한 플랫폼 통합
- **문제 메타데이터 관리**: 난이도, 태그, 성공률 등 상세 정보 추적

### 2. 고급 알고리즘 챌린지 시스템 ⭐ NEW!
- **난이도별 문제 선별**: 사용자 수준에 맞는 최적의 문제 추천
- **개인화된 학습 경로**: AI 기반 맞춤형 학습 계획 생성
- **점진적 난이도 상승**: 사용자 성과에 따른 동적 난이도 조정
- **실시간 코드 검증**: 다중 언어 지원 코드 실행 및 테스트
- **성능 분석**: 실행 시간, 메모리 사용량, 복잡도 분석
- **챌린지 시스템**: 일일/주간/커스텀 챌린지로 동기부여

### 3. 사용자 진도 추적
- **상세한 성취도 분석**: 문제별, 태그별, 난이도별 통계
- **연속 해결 스트릭**: 학습 동기부여를 위한 스트릭 시스템
- **개인화된 통계**: 사용자별 맞춤 통계 및 분석 리포트

### 4. 원격 문제 제공자
- **실시간 문제 동기화**: 외부 플랫폼과의 실시간 연동
- **캐싱 시스템**: 효율적인 데이터 관리 및 빠른 응답
- **에러 처리**: 안정적인 네트워크 오류 대응

## 📁 프로젝트 구조

```
algorithm_system/
├── __init__.py
├── problem_data_structures.py      # 핵심 데이터 구조
├── remote_problem_provider.py      # 원격 문제 제공자
├── user_progress_tracker.py        # 사용자 진도 추적
├── advanced_challenge_system.py    # 고급 챌린지 시스템 ⭐
├── advanced_challenge_example.py   # 사용 예제
├── example_problems.py             # 예제 문제들
├── remote_provider_example.py      # 원격 제공자 예제
├── cache/                          # 캐시 데이터
│   ├── leetcode/
│   ├── codeforces/
│   └── kaggle/
└── README.md                       # 이 파일
```

## 🛠️ 설치 및 사용법

### 1. 기본 사용법

```python
from algorithm_system.advanced_challenge_system import AdvancedChallengeSystem
from algorithm_system.remote_problem_provider import RemoteProblemProvider

# 시스템 초기화
problem_provider = RemoteProblemProvider()
challenge_system = AdvancedChallengeSystem("user123", problem_provider)

# 개인화된 문제 추천
recommendations = challenge_system.get_personalized_recommendations(5)

# 일일 챌린지 생성
daily_challenge = challenge_system.create_daily_challenge()

# 코드 제출 및 검증
is_correct, test_results, performance = challenge_system.submit_solution(
    problem_id, code, language, test_cases
)
```

### 2. 고급 기능 사용법

```python
# 학습 경로 생성
learning_path = challenge_system.generate_learning_path("동적 프로그래밍 마스터", 30)

# 커스텀 챌린지 생성
custom_challenge = challenge_system.create_custom_challenge(
    name="문자열 알고리즘 집중 학습",
    description="문자열 관련 문제들을 집중적으로 풀어보세요!",
    target_difficulty=ProblemDifficulty.MEDIUM,
    target_problems=10,
    time_limit_days=14
)

# 사용자 통계 확인
stats = challenge_system.get_user_statistics()
print(f"사용자 레벨: {stats['user_level']}")
print(f"성공률: {stats['success_rate']:.2%}")

# 약점/강점 분석
weak_areas = challenge_system.get_weak_areas(5)
strong_areas = challenge_system.get_strong_areas(5)
```

## 🎯 고급 챌린지 시스템 상세 기능

### 1. 난이도별 문제 선별 로직
- **품질 점수 계산**: 문제의 교육적 가치와 품질을 수치화
- **랜덤 선택**: 상위 문제들 중에서 랜덤 선택으로 다양성 확보
- **사용자 맞춤**: 해결한 문제 제외 및 난이도 적합성 고려

### 2. 개인화된 문제 추천
- **약한 태그 기반 추천 (40%)**: 부족한 영역 집중 학습
- **현재 레벨 문제 (30%)**: 안정적인 실력 향상
- **다음 레벨 준비 (20%)**: 도전적인 문제로 성장
- **강한 태그 심화 (10%)**: 전문성 강화

### 3. 점진적 난이도 상승 알고리즘
- **성과 분석**: 최근 7일간의 성공률 및 난이도 트렌드 분석
- **동적 조정**: 성과에 따른 자동 난이도 조정
- **안전장치**: 급격한 난이도 변화 방지

### 4. 코드 검증 시스템
- **다중 언어 지원**: Python, Java, C++, JavaScript 등
- **실시간 실행**: 안전한 샌드박스 환경에서 코드 실행
- **상세한 피드백**: 오류 메시지, 실행 시간, 메모리 사용량

### 5. 성능 분석
- **복잡도 추정**: 코드 패턴 분석을 통한 시간/공간 복잡도 추정
- **코드 품질 점수**: 가독성, 효율성, 성공률 종합 평가
- **성능 지표**: 실행 시간, 메모리 사용량, 테스트 통과율

### 6. 학습 경로 생성
- **목표 기반**: 사용자 목표에 따른 맞춤형 경로
- **진도 기반**: 현재 실력과 목표 간의 최적 경로 설계
- **다양한 경로**: 기초/중급/고급/커스텀 경로 제공

## 📊 사용자 통계 및 분석

### 주요 지표
- **사용자 레벨**: 1-10 단계의 종합 실력 평가
- **성공률**: 전체 제출 대비 정답률
- **연속 해결**: 학습 지속성 측정
- **태그별 성취도**: 알고리즘 영역별 숙련도

### 분석 리포트
- **진도 보고서**: 종합적인 학습 현황 분석
- **약점 분석**: 개선이 필요한 영역 식별
- **성장 트렌드**: 시간에 따른 실력 변화 추이

## 🔧 확장 가능한 아키텍처

### 모듈화된 설계
- **독립적인 컴포넌트**: 각 기능이 독립적으로 동작
- **플러그인 구조**: 새로운 기능 쉽게 추가 가능
- **인터페이스 기반**: 표준화된 인터페이스로 확장성 확보

### 데이터 관리
- **JSON 기반 저장**: 인간이 읽기 쉬운 데이터 형식
- **캐싱 시스템**: 효율적인 데이터 접근
- **백업 및 복구**: 안전한 데이터 관리

## 🚀 향후 개발 계획

### 단기 계획 (1-2개월)
- [ ] 웹 인터페이스 개발
- [ ] 실시간 협업 기능
- [ ] 모바일 앱 개발

### 중기 계획 (3-6개월)
- [ ] AI 기반 문제 생성
- [ ] 머신러닝 성능 예측
- [ ] 소셜 기능 (친구, 랭킹)

### 장기 계획 (6개월 이상)
- [ ] VR/AR 학습 환경
- [ ] 블록체인 기반 인증
- [ ] 글로벌 플랫폼 확장

## 🤝 기여하기

이 프로젝트는 오픈소스이며, 모든 기여를 환영합니다!

### 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 가이드라인
- 코드 스타일: PEP 8 준수
- 문서화: 모든 함수와 클래스에 docstring 작성
- 테스트: 새로운 기능에 대한 테스트 코드 작성
- 타입 힌트: 모든 함수에 타입 힌트 추가

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**알고리즘 문제 풀이 시스템**으로 더 나은 개발자가 되어보세요! 🚀