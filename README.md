# 1) 프로젝트 개요



# 2) 디렉토리 구조
```
/GDGoC-Team1-SeoulFestRecommender
├── .env                                    # 공통 환경 변수 (DB 접속 정보)
├── docker-compose.yml                      # 통합 서비스 실행 설정
├── Makefile                                # 빌드/실행 자동화
├── README.md
│
├── backend/                
│   ├── Dockerfile                          # 백엔드 전용 이미지 빌드
│   ├── pyproject.toml                      # Poetry 의존성
│   ├── poetry.lock
│   │
│   └── app/                                # FastAPI 애플리케이션 코어
│       ├── __init__.py
│       ├── main.py                         # 앱 진입점 (라우터 등록, DB 초기화)
│       │
│       └── api/                            # API 라우터
│           └── festival.py                 
│       ├── core/                          
│       │   ├── config.py                   # 환경 변수 로드
│       │   └── dependencies.py             # DB 세션 의존성 주입
│       │
│       ├── db/                             # DB 연결 및 초기화
│       │   ├── database.py                 # SQLAlchemy 엔진 생성
│       │   └── init_db.py                  # 테이블 생성 및 샘플 데이터 삽입
│       │
│       ├── entity/                         # DB 테이블 스키마
│       │   ├── base_entity.py
│       │   └── festival_entity.py        
│       │
│       ├── models/                         # Pydantic 모델 (API I/O)
│       │   └── festival.py             
│       │
│       ├── repository/                     # 데이터 접근 (CRUD)
│       │   ├── base_repo.py
│       │   └── festival_repo.py
│       │
│       └── service/                        # AI
│           └── llm_service.py    
│
└── frontend/                               # 프론트엔드 서비스 
    └── (empty)
```

# 3) 가상환경 세팅방법
```bash
# 1. Poetry 가상 환경 초기 설정 및 의존성 업데이트 (의존성 바뀔때마다 재실행)
make setup

# 2. Poetry 가상 환경 쉘 활성화 (가상환경 접속)
make shell
```

# 4) 사용방법
```bash
# 1. Docker 이미지 빌드
make build

# 2. Docker 서버 실행
make run

# 3. 코드 수정 후 서버 재시작
make rebuild

# 4. Docker 서버 중지
make stop

# 5. Docker 볼륨 및 이미지 정리
make clean

```

