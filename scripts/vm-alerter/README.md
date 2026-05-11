# vm-alerter

debi-marlene-bot VM 메모리 모니터. 임계 초과 시 Discord webhook 으로 알림.

## 구성
- **alert.sh** — alpine 컨테이너 안에서 영구 실행. /proc 마운트로 host 메모리 읽음.
- **임계**: 메모리 85% 5분 지속 → 알림 / 30분 쿨다운

## 셋업 (1회)
1. Discord 채널에 webhook 만들고 URL 받기
2. GCP Secret Manager 에 저장:
   ```bash
   echo -n "<webhook_url>" | gcloud secrets create vm-alerter-webhook \
     --data-file=- --project=ironic-objectivist-465713-a6
   ```
3. VM 에 스크립트 배포:
   ```bash
   gcloud compute scp scripts/vm-alerter/alert.sh \
     debi-marlene-bot:/home/2rami/debi-marlene/alert.sh \
     --zone=asia-northeast3-a
   ```
4. VM 에서 컨테이너 띄우기:
   ```bash
   gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="
     WEBHOOK=\$(gcloud secrets versions access latest --secret=vm-alerter-webhook)
     sudo docker run -d --name vm-alerter --restart unless-stopped \
       --pid=host \
       -v /home/2rami/debi-marlene/alert.sh:/alert.sh:ro \
       -e WEBHOOK_URL=\"\$WEBHOOK\" \
       alpine sh /alert.sh
   "
   ```

## 운영
- 로그: `docker logs -f vm-alerter` (VM 안에서)
- 임계 변경: `docker stop vm-alerter && docker rm vm-alerter` 후 환경변수 바꿔서 다시 run
- 테스트 알림: `THRESHOLD=10` 으로 잠깐 띄워서 확인 후 정상 복구

## 환경변수
| 변수 | 기본 | 설명 |
|---|---|---|
| WEBHOOK_URL | (필수) | Discord webhook |
| THRESHOLD | 85 | 메모리 사용률 % |
| SUSTAINED_MIN | 5 | 임계 초과 지속 분 |
| COOLDOWN_MIN | 30 | 알림 후 쿨다운 분 |
