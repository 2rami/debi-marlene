# GitHub Actions 자동 배포

모바일/타 기기에서 `main` 에 push 만 하면 자동 배포되도록 구성. 로컬 `make deploy-*` 를 미러링한다.

## 워크플로우 2종

| 파일 | 트리거 경로 | 하는 일 | 미러링 |
|---|---|---|---|
| `.github/workflows/deploy-dashboard.yml` | `dashboard/frontend/**`, `dashboard/backend/**`, `run/**` | npm build → VM `docker cp` → nginx reload + 백엔드 scp → gunicorn restart + CF 퍼지 | `make deploy-dashboard-quick` |
| `.github/workflows/deploy-bot.yml` | `run/**`, `main.py`, `Dockerfile`, `requirements.txt` | docker build → Artifact Registry push → VM 컨테이너 재시작 | `make deploy` |

수동 실행: GitHub Actions 탭 > 해당 워크플로우 > **Run workflow**.

> `run/**` 이 두 워크플로우 모두에 걸려 있다 — 봇 로직과 대시보드 백엔드가 같은 `run/` 모듈을 공유하기 때문. 봇 코드만 바꿨다면 대시보드 배포는 무해하게 한 번 더 도는 정도.

## 필요한 GitHub Secrets

| Secret | 용도 |
|---|---|
| `GCP_DEPLOY_SA_KEY` | 배포 전용 SA(`deploy-actions`) JSON 키. **봇·대시보드 공통** |
| `VITE_DISCORD_CLIENT_ID` | 대시보드 프론트 빌드 주입 (디스코드 로그인) |
| `VITE_TOSS_CLIENT_KEY` | (선택) 토스 충전 키. 없으면 충전 비활성 빌드 |
| `CF_API_TOKEN` | Cloudflare 캐시 퍼지 |

> 기존 `GCP_SA_KEY` 는 `daily-feed-actions` SA 키(배포 권한 없음)라 **재사용 불가**. 그래서 별도 `GCP_DEPLOY_SA_KEY` 를 만들었고, 기존 키는 건드리지 않는다.

## 1회 셋업 (이미 완료 — 재현/복구용 기록)

```bash
P=ironic-objectivist-465713-a6
SA="deploy-actions@$P.iam.gserviceaccount.com"

# 1) 배포 전용 SA 생성
gcloud iam service-accounts create deploy-actions \
  --display-name="Deploy GitHub Actions (bot+dashboard)" --project=$P

# 2) 권한
for ROLE in roles/artifactregistry.writer roles/compute.osAdminLogin roles/iam.serviceAccountUser roles/iap.tunnelResourceAccessor; do
  gcloud projects add-iam-policy-binding $P --member="serviceAccount:$SA" --role="$ROLE" --condition=None
done

# 2-1) VM OS Login 활성화 — SA 는 메타데이터 SSH 키를 못 써서(권한 없음) 이게 없으면
#      gcloud compute ssh 가 "Could not add SSH key to instance metadata" 로 막힌다.
gcloud compute instances add-metadata debi-marlene-bot --zone=asia-northeast3-a --metadata enable-oslogin=TRUE

# 3) SA 키 → GitHub Secret (값은 로그에 안 남게 stdin/파일)
gcloud iam service-accounts keys create /tmp/deploy-sa-key.json --iam-account=$SA
gh secret set GCP_DEPLOY_SA_KEY --repo 2rami/debi-marlene < /tmp/deploy-sa-key.json
rm -f /tmp/deploy-sa-key.json

# 4) 빌드/퍼지 secrets (로컬 .env 값 주입)
printf '%s' "$(grep -E '^DISCORD_CLIENT_ID=' .env | cut -d= -f2- | tr -d '\"'\'' ')" | gh secret set VITE_DISCORD_CLIENT_ID --repo 2rami/debi-marlene
printf '%s' "$(grep -E '^CF_API_TOKEN=' .env | cut -d= -f2- | tr -d '\"'\'' ')"      | gh secret set CF_API_TOKEN --repo 2rami/debi-marlene
```

## 인프라 전제 / 함정

- **OS Login 필수**: SA 는 SSH 키를 인스턴스/프로젝트 메타데이터에 쓸 권한이 없어, 끄면 `gcloud compute ssh` 가 `Could not add SSH key to instance metadata` 로 막힌다. 그래서 이 VM 은 OS Login 을 켜뒀고(`enable-oslogin=TRUE`, VM 레벨) SA 에 `compute.osAdminLogin`(sudo 가능) + `iam.serviceAccountUser` 를 줬다.
  - **부작용**: 로컬에서 `gcloud compute ssh` 도 OS Login username 으로 들어간다. 그 username 은 `docker` 그룹이 아니라서, `make logs`/`make deploy`/`make status` 처럼 sudo 없이 `docker` 를 호출하는 로컬 타깃은 `permission denied` 가 난다. 로컬에선 `sudo docker`(조회) 또는 `sudo -u 2rami docker`(pull 포함) 를 쓰거나, 그냥 워크플로우로 배포할 것.
- **docker 권한 두 갈래** (이게 봇/대시보드 차이의 핵심):
  - 대시보드 = `sudo docker cp`/`exec`. 이미지 pull 이 없어서 root 로 충분.
  - 봇 = `sudo -u 2rami docker pull/run`. pull 은 Artifact Registry 인증이 필요한데 **root(그냥 `sudo docker`)는 인증이 없어 `Unauthenticated request ... downloadArtifacts` 로 실패**한다. `2rami` 만 `~/.docker` credHelper + docker 그룹을 가진다 (Makefile restart 와 동일 context).
- **봇 워크플로우 리스크**: 프로덕션 봇을 `stop -> start` 한다. `start`(특히 pull) 실패 시 봇이 stop+rm 된 채 안 떠서 다운된다. 대시보드 워크플로우는 nginx reload/gunicorn restart 라 봇에 영향 없음 — 그래서 대시보드부터 검증한다. **복구**: VM 로컬 캐시 이미지로 `sudo docker run -d --name debi-marlene ... :latest` (pull 없이 즉시).
- **봇 `.env`**: VM 의 `/home/2rami/debi-marlene/.env` 를 `--env-file` 로 사용. CI 는 봇 `.env` 를 만지지 않는다 (단일 진실: VM).
- **외부IP SSH**: 방화벽 `default-allow-ssh`(0.0.0.0/0 → tcp:22) 가 열려 있어 IAP 없이 접속. 추후 좁히려면 워크플로우 SSH 에 `--tunnel-through-iap` + `allow-iap-ssh`(35.235.240.0/20 → tcp:22) 방화벽 추가 후 0.0.0.0/0 규칙을 닫으면 된다. SA 에 `iap.tunnelResourceAccessor` 는 이미 있다.
