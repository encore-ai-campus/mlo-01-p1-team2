from used_car_api import get_api_headers, request_page
from used_car_config import (
    API_LISTING_NUMBER_FIELD,
    BASE_DIR,
    BASE_URL,
    DATA_DIR,
    INCREMENTAL_MAX_ITEMS,
    OUTPUT_FILE,
    PAGE_LIMIT,
    SERVER_RETRY_SECONDS,
    STATE_FILE,
)
from used_car_crawler import initial_crawl, incremental_crawl, main
from used_car_state import get_last_id, get_state, is_initial_complete, save_state
from used_car_storage import clean_value, load_existing_data, save_to_json


# 이 파일을 직접 실행했을 때만 main() 실행
if __name__ == "__main__":
    main()
