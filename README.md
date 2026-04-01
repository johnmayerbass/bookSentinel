# bookSentinel

캠핑장 잔여석 모니터링 및 텔레그램 알람 서비스

## 기술 스택

### Infrastructure
- OS: Ubuntu Server 24.04.4
- Container: Docker 29.3.1
- Orchestration: Docker Compose 5.1.1

### Backend
- Language: Python 3.10.12
- Browser Automation: Playwright 1.58.0
- HTTP Client: Requests
- Env 관리: python-dotenv

### Notification
- Telegram Bot API

## 프로젝트 구조

```
bookSentinel/
├── Dockerfile
├── docker-compose-sentinel.yml
├── requirements.txt
├── .env
└── main.py
```

## 주요 기능

- 인터파크 티켓 캠핑장 페이지 모니터링
- 지정한 날짜 / 기간의 오토캠핑존 잔여석 체크
- 잔여석 0 → 1 이상 변경 시 텔레그램 알람 전송
- 60초 주기 스케줄링
- 팝업 자동 제거 및 동적 페이지 처리 (JS 렌더링)

## 환경 변수

| 변수명 | 설명 |
|---|---|
| TELEGRAM_BOT_TOKEN | 텔레그램 봇 토큰 |
| TELEGRAM_CHAT_ID | 텔레그램 채팅 ID |
| TARGET_URL | 모니터링할 URL |
| TARGET_MONTH | 체크할 월 |
| TARGET_DAY | 체크할 일 |
| CHECK_INTERVAL | 체크 주기 (초) |


