-- Firestore → MySQL 백업 스키마
-- 운영 진실 = Firestore. 여기는 백업 + 분석/리포트 용도.
-- 첫 컨테이너 시작 시 자동 적용 (mysql/docker-entrypoint-initdb.d).

USE debi_marlene_backup;

-- ─────── 1. 길드 백업 ───────
CREATE TABLE IF NOT EXISTS guilds_backup (
    guild_id VARCHAR(20) PRIMARY KEY,
    guild_name VARCHAR(200),
    member_count INT,
    announcement_channel_id VARCHAR(20),
    chat_channel_id VARCHAR(20),
    tts_channel_id VARCHAR(20),
    status VARCHAR(20),
    snapshot_at DATETIME NOT NULL,
    raw_json JSON,                     -- 원본 Firestore doc 통째로 (스키마 변경 안전망)
    INDEX idx_snapshot (snapshot_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────── 2. 사용자 백업 ───────
CREATE TABLE IF NOT EXISTS users_backup (
    user_id VARCHAR(20) PRIMARY KEY,
    user_name VARCHAR(200),
    youtube_subscribed BOOLEAN DEFAULT FALSE,
    dm_channel_id VARCHAR(20),
    interaction_count INT DEFAULT 0,
    last_interaction DATETIME,
    last_dm DATETIME,
    snapshot_at DATETIME NOT NULL,
    raw_json JSON,
    INDEX idx_youtube_subs (youtube_subscribed),
    INDEX idx_snapshot (snapshot_at),
    INDEX idx_interaction_count (interaction_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────── 3. 전역 설정 백업 ───────
CREATE TABLE IF NOT EXISTS global_backup (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value JSON,                -- 값이 string/number/object 다 들어올 수 있음
    snapshot_at DATETIME NOT NULL,
    INDEX idx_snapshot (snapshot_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────── 4. 백업 실행 이력 (DBA 사고방식 — 백업 자체를 추적) ───────
CREATE TABLE IF NOT EXISTS backup_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    guilds_count INT DEFAULT 0,
    users_count INT DEFAULT 0,
    global_count INT DEFAULT 0,
    status ENUM('running', 'success', 'partial', 'failed') DEFAULT 'running',
    error_message TEXT,
    duration_seconds INT,
    INDEX idx_started (started_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────── 분석용 뷰 샘플 ───────
-- 활성 사용자 통계
CREATE OR REPLACE VIEW v_active_users AS
SELECT
    COUNT(*) AS total_users,
    SUM(CASE WHEN youtube_subscribed = TRUE THEN 1 ELSE 0 END) AS youtube_subscribers,
    SUM(CASE WHEN interaction_count > 0 THEN 1 ELSE 0 END) AS active_users,
    AVG(interaction_count) AS avg_interactions
FROM users_backup;

-- 활성 길드 통계 (status 살아있는 것만)
CREATE OR REPLACE VIEW v_active_guilds AS
SELECT
    COUNT(*) AS total_guilds,
    SUM(CASE WHEN announcement_channel_id IS NOT NULL THEN 1 ELSE 0 END) AS with_announcement,
    SUM(CASE WHEN chat_channel_id IS NOT NULL THEN 1 ELSE 0 END) AS with_chat,
    SUM(CASE WHEN tts_channel_id IS NOT NULL THEN 1 ELSE 0 END) AS with_tts
FROM guilds_backup
WHERE status IS NULL OR status != '삭제됨';
