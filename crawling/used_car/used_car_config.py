from pathlib import Path


# 서버 기본 주소
BASE_URL = "http://192.168.0.51:4000"

# 현재 파이썬 파일과 data 폴더 경로
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# JSON 및 상태 파일 저장 위치
OUTPUT_FILE = DATA_DIR / "used_car.json"
STATE_FILE = DATA_DIR / "crawl_state.json"

# API 요청 설정
PAGE_LIMIT = 500
INCREMENTAL_MAX_ITEMS = 500
SERVER_RETRY_SECONDS = 300

# 차량 식별용 필드명
API_LISTING_NUMBER_FIELD = "listingNumber"
