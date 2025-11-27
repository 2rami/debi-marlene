# Claude Code 가이드

## 코딩 규칙

### Agent 병렬 작업
- 독립적인 여러 작업을 동시에 처리 가능
- 예: 대규모 리팩토링, 코드 탐색 + 계획 수립, 테스트 + 문서화

### TODO 관리
- 복잡한 작업은 TodoWrite로 단계별 추적
- 코드 수정 시 claude's question (선택하는거) 적극적으로 사용
- 작업 많을 시 여러 에이전트 기용하는 기능 적극적으로 사용
- dak gg 사용가능한 api endpoint.md 많이 참고

**중요: 이모지 사용 금지**
- 코드에서 이모지 절대 사용하지 말 것
- Discord 임베드, 메시지, 로그 등 모든 곳에서 이모지 금지
- 대신 텍스트나 기호 사용 (#1, [TOP], *, - 등)
- 디버그 로그 추가하고 해결되면 삭제

## 역할 구분 원칙

| 계층 | 역할 | 예시 |
|------|------|------|
| api_client | 순수 데이터 추출/변환, API 호출 | extract_team_members_info |
| views | Discord embed/UI 포맷팅 | format_teammate_info |

---

## 배포 환경

- **클라우드 플랫폼**: Google Cloud Platform (GCP)
- **컨테이너 실행**: Cloud Run (서버리스)
- **스토리지**: Cloud Storage (`debi-marlene-settings` 버킷)
- **이미지 저장소**: Google Container Registry (GCR)
- **로깅**: Cloud Logging
- **리전**: asia-northeast3 (서울)

### 주요 컴포넌트
- **Discord Bot**: Python 기반, Cloud Run에서 컨테이너로 실행
- **Google Cloud Run**: 서버리스 컨테이너 실행 환경
- **Google Cloud Storage (GCS)**: 봇 설정 및 DM 채널 정보 저장
- **Google Container Registry (GCR)**: Docker 이미지 저장소
- **Cloud Logging**: 로그 수집 및 모니터링

## 배포 방법

### .dockerignore 설정
- **webpanel/** 폴더가 제외 설정됨
- Docker 이미지 빌드 시 webpanel은 자동으로 제외됩니다

### **중요: 로컬 도커 오류 시 배포 방법**
**코드 수정했다고 바로 배포 금지!!! 로컬에서 사용자가 우선 테스트**

```bash
# 1. 로컬 코드를 VM에 업로드
gcloud compute scp --recurse . debi-marlene-bot:~/debi-marlene/ --zone=asia-northeast3-a

# 2. VM에서 Docker 이미지 빌드
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="cd ~/debi-marlene && docker build -t debi-marlene-bot ."

# 3. 기존 컨테이너 중지 및 제거
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="docker stop debi-marlene || true && docker rm debi-marlene || true"

# 4. 새 컨테이너 실행
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="docker run -d --name debi-marlene -p 5000:5000 -p 8080:8080 debi-marlene-bot"
```

### Docker 이미지 빌드 및 배포 (Cloud Run)
```bash
# 봇 이미지 빌드
cd /Users/kasa/Desktop/momewomo/debi-marlene
docker build --no-cache --platform linux/amd64 -f Dockerfile -t gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 .

# GCR에 푸시
docker push gcr.io/[PROJECT_ID]/debi-marlene-bot:v1

# Cloud Run 배포
gcloud run deploy debi-marlene-bot \
  --image gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 \
  --platform managed \
  --region asia-northeast3 \
  --set-env-vars DISCORD_TOKEN=[TOKEN],YOUTUBE_API_KEY=[KEY] \
  --memory 512Mi \
  --cpu 1
```

## GCS 인증 설정

```bash
# 로컬 개발 환경
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 또는 gcloud CLI 인증
gcloud auth application-default login

# GCS 버킷 확인
gsutil ls gs://debi-marlene-settings/
gsutil cat gs://debi-marlene-settings/settings.json
```

## 트러블슈팅

### 자주 발생하는 문제들

1. **ModuleNotFoundError: No module named 'google.cloud.storage'**
   ```bash
   pip install google-cloud-storage
   # 또는
   pip install --break-system-packages google-cloud-storage  # macOS
   ```

2. **GCS 인증 실패 (403 Forbidden)**
   ```bash
   # 로컬: 환경변수 설정
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

   # Cloud Run: IAM 권한 부여
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
     --member="serviceAccount:[SERVICE_ACCOUNT]@[PROJECT_ID].iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

3. **DM 채널이 저장되지 않음**
   - 봇에게 DM 메시지 전송 → 자동으로 GCS에 저장됨
   - GCS `settings.json`의 `users` 섹션에 `dm_channel_id` 확인

4. **배포 후 변경사항 미반영**
   ```bash
   # Docker 이미지 캐시 없이 재빌드
   docker build --no-cache --platform linux/amd64 -f Dockerfile -t gcr.io/[PROJECT_ID]/bot:v2 .

   # Cloud Run 최신 리비전으로 트래픽 전환
   gcloud run services update-traffic debi-marlene-bot --to-latest
   ```

## 모니터링 명령어

```bash
# Cloud Run 서비스 상태 확인
gcloud run services list
gcloud run services describe debi-marlene-bot --region asia-northeast3

# 로그 확인
gcloud run services logs read debi-marlene-bot --region=asia-northeast3 --limit=50
gcloud run services logs tail debi-marlene-bot --region=asia-northeast3  # 실시간

# GCS 설정 확인
gsutil cat gs://debi-marlene-settings/settings.json
```
