# Requirements-Traceability 작성

Requirements traceability · BRD→PRD→AC→Evidence

> starter\_id: `encore.chapter1.brd-prd-requirements-workshop.starter`
> starter\_version: `v1`
> 
> 작성 규칙: `TODO-LEARNER` 대표 4행을 완성한 뒤 전체 Must 행의 빈 연결을 검사한다.
> 

implementation branch를 채울 때에는 Day 21 Git Flow의 `<type>/<ticket>-<topic>` 규칙을 따른다. 예: `feature/DATA-105-run-entrypoint`, `docs/DOC-302-observability-evidence`.

|business need|BRD objective|user need|PRD requirement|AC|implementation|test/evidence|due|evidence\_status|
|-|-|-|-|-|-|-|-|-|
|`BR-NEED-001`|`BR-OBJ-001`|`UN-AN-001`|`FR-VEH-COLLECT-001`|`AC-VEH-COLLECT-001`|`feature/DATA-101-vehicle-ingestion`|`evidence/day22-evidence.md`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-001`|`UN-AN-001`|`FR-VEH-TRANSFORM-001`|`AC-VEH-TRANSFORM-001`|`feature/DATA-101-vehicle-ingestion`|`output/<run\_id>/quality-report.json`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-002`|`UN-FAQ-001`|`FR-FAQ-COLLECT-001`|`AC-FAQ-COLLECT-001`|`feature/DATA-201-faq-ingestion`|`evidence/day22-evidence.md`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-003`|`UN-OPS-001`|`FR-RUN-001`|`AC-RUN-001`|`feature/DATA-105-run-entrypoint`|`evidence/day21-smoke.txt`|Day 21|planned|
|`BR-NEED-001`|`BR-OBJ-001`|`UN-AN-001`|`FR-VEH-LOAD-001`|`AC-VEH-LOAD-001`|`feature/DATA-102-vehicle-storage`|`output/<run\_id>/quality-report.json`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-002`|`UN-FAQ-001`|`FR-FAQ-LOAD-001`|`AC-FAQ-LOAD-001`|`feature/DATA-202-faq-storage`|`evidence/day22-evidence.md`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-001`·`BR-OBJ-002`|`UN-AN-001`·`UN-FAQ-001`|`FR-QUERY-001`|`AC-QUERY-001`|`feature/DATA-301-final-queries`|`evidence/final-verification.md`|Day 23|planned|
|`BR-NEED-001`|`BR-OBJ-003`|`UN-OPS-001`|`FR-SCHEDULE-001`|`AC-SCHEDULE-001`|`feature/OPS-301-scheduler`|`evidence/scheduler-run.md`|Day 23|planned|
|`BR-NEED-001`|`BR-OBJ-001 · BR-OBJ-004`|`UN-AN-001`|`DR-VEH-001`|`AC-VEH-DATA-001`|`feature/DATA-103-vehicle-quality`|`output/<run\_id>/quality-report.json`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-001 · BR-OBJ-004`|`UN-FAQ-001`|`DR-FAQ-001`|`AC-FAQ-DATA-001`|`feature/DATA-203-faq-quality`|`evidence/day22-evidence.md`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-003`|`UN-OPS-001`|`NFR-IDEMP-001`|`AC-IDEMP-001`|`feature/OPS-302-idempotency`|`evidence/retry-idempotency.md`|Day 23|planned|
|`BR-NEED-001`|`BR-OBJ-001`·`BR-OBJ-002`·`BR-OBJ-003`|`UN-OPS-001`|`NFR-SOURCE-001`|`AC-SOURCE-001`|`feature/DATA-104-source-guard`|`evidence/day22-evidence.md`|Day 22|planned|
|`BR-NEED-001`|`BR-OBJ-004`|`UN-AUD-001`|`NFR-SECRET-001`|`AC-SECRET-001`|`docs/DOC-301-security-review`|`evidence/requirements-review.md`|Day 23|planned|
|`BR-NEED-001`|`BR-OBJ-003` · `BR-OBJ-004`|`UN-AUD-001`|`NFR-OBS-001`|`AC-OBS-001`|`docs/DOC-302-observability-evidence`|logs/sanitized-success.jsonl<br />evidence/retry-idempotency.md|Day 23|planned|
|`BR-NEED-001`|`BR-OBJ-003`|`UN-OPS-001`|`NFR-RETRY-001`|`AC-RETRY-001`|`feature/OPS-303-retry-policy`|`evidence/retry-idempotency.md`|Day 23|planned|

## Link integrity review

* must\_requirement\_count: `15`
* must\_with\_ac\_count: 15
* orphan\_must\_requirement\_count: 0
* premature\_pass\_count: 0
* reviewer\_role: 김세진
* reviewed\_at: 2026-08-11:(ISO 8601)
* link\_integrity\_review: `PASS`

통과 기준은 `must\_with\_ac\_count=15`, `orphan\_must\_requirement\_count=0`, `premature\_pass\_count=0`이다.

