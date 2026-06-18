# GitHub Actions 자동 배포 (봇)

`main` 브랜치에 봇 코드(`run/`, `main.py`, `Dockerfile`, `requirements.txt`)가 push되면
`.github/workflows/deploy-bot.yml` 워크플로가 자동으로 빌드 → Artifact Registry push → VM 컨테이너 재시작을 수행한다.
로컬 `make deploy` 와 동일한 동작을 GitHub 러너에서 대신 실행하는 구조라, 클라우드 세션이나 어디서든 main 머지만으로 배포된다.

수동 실행: GitHub Actions 탭 > "Deploy Bot" > Run workflow.

---

## 1회 셋업 (거노가 GCP/GitHub에서 직접)

### A. 배포용 서비스계정 생성 + 권한 부여

```bash
PROJECT_ID=ironic-objectivist-465713-a6
SA_NAME=github-deployer
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project "$PROJECT_ID"

# 서비스계정 생성
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="GitHub Actions deployer"

# 이미지 push 권한 (Artifact Registry)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

# VM SSH 권한 (os-login + sudo 가능한 admin 로그인 — 컨테이너 재시작에 sudo docker 사용)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/compute.osAdminLogin"

# VM 메타데이터/인스턴스 조회 (gcloud compute ssh 가 내부적으로 사용)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/compute.viewer"

# IAP 터널로 SSH (공개 IP/방화벽 관리 회피)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iap.tunnelResourceAccessor"
```

### B. IAP SSH 방화벽 허용 (한 번만)

IAP 터널이 VM 22번 포트로 들어오도록 허용. (이미 있으면 생략)

```bash
gcloud compute firewall-rules create allow-iap-ssh \
  --project="$PROJECT_ID" \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20
```

### C. 서비스계정 키 발급 → GitHub Secret 등록

```bash
gcloud iam service-accounts keys create /tmp/gh-deployer-key.json \
  --iam-account="$SA_EMAIL"
```

GitHub 레포 > Settings > Secrets and variables > Actions > New repository secret:

- Name: `GCP_SA_KEY`
- Value: `/tmp/gh-deployer-key.json` 파일 **내용 전체** 붙여넣기

등록 후 로컬 키 파일은 삭제: `rm /tmp/gh-deployer-key.json`

> 보안 참고: SA JSON 키는 장기 자격증명이라 유출 시 위험. 더 안전하게 가려면
> Workload Identity Federation(키 없는 인증)으로 전환 가능 — 필요하면 워크플로의
> `auth` 스텝을 `workload_identity_provider` + `service_account` 방식으로 바꾸면 된다.

---

## 동작 / 범위

- 트리거: `main` push + 위 paths 변경, 또는 수동 실행.
- 컨테이너는 **VM의 `.env`** (`--env-file $VM_PATH/.env`)를 그대로 사용 — CI는 `.env`를 건드리지 않는다.
- 따라서 Secret Manager ↔ VM `.env` 동기화는 기존처럼 `scripts/sync_env.sh` 로 관리.
  (로컬 `make deploy` 의 `deploy-env-guard` 3-way 드리프트 체크는 CI에는 없음 — env를 바꿨다면 배포 전 `make sync-check` 로 확인할 것.)
- 의존성(`requirements.txt`/`Dockerfile`)이 안 바뀌고 `.py`만 바뀌어도 이 워크플로는 전체 리빌드를 한다.
  (로컬의 `make deploy-quick` 같은 코드만-교체 경로는 CI에 별도 구현하지 않음 — 안정성 우선.)

## 확인

셋업 후 동작 검증: Actions 탭에서 "Deploy Bot" 수동 실행 → 그린이면 완료.
실패 시 로그에서 어느 스텝(auth / push / ssh)인지 확인. VM에서 `sudo docker` 권한 문제면
`roles/compute.osAdminLogin` 부여 여부를 다시 확인.
