-- Çözüm Oto Elektrik — MySQL şeması (production)
SET NAMES utf8mb4;
SET foreign_key_checks = 0;

CREATE TABLE IF NOT EXISTS users (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name          VARCHAR(120) NOT NULL,
    email         VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(30)  NOT NULL DEFAULT 'admin',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS settings (
    `key`   VARCHAR(80) NOT NULL,
    `value` TEXT NULL,
    PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS services (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    slug             VARCHAR(160) NOT NULL UNIQUE,
    title            VARCHAR(200) NOT NULL,
    summary          VARCHAR(500) NULL,
    body             MEDIUMTEXT NULL,
    icon             VARCHAR(80) NULL,
    image            VARCHAR(255) NULL,
    meta_title       VARCHAR(200) NULL,
    meta_description VARCHAR(320) NULL,
    sort_order       INT NOT NULL DEFAULT 0,
    is_active        TINYINT(1) NOT NULL DEFAULT 1,
    enable_districts TINYINT(1) NOT NULL DEFAULT 1,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS districts (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    slug       VARCHAR(120) NOT NULL UNIQUE,
    name       VARCHAR(120) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hizmet x İlçe için isteğe bağlı özel içerik override'ı.
CREATE TABLE IF NOT EXISTS service_district (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    service_id       INT UNSIGNED NOT NULL,
    district_id      INT UNSIGNED NOT NULL,
    body             MEDIUMTEXT NULL,
    meta_title       VARCHAR(200) NULL,
    meta_description VARCHAR(320) NULL,
    is_active        TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uniq_service_district (service_id, district_id),
    CONSTRAINT fk_sd_service  FOREIGN KEY (service_id)  REFERENCES services(id)  ON DELETE CASCADE,
    CONSTRAINT fk_sd_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pages (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    slug             VARCHAR(160) NOT NULL UNIQUE,
    title            VARCHAR(200) NOT NULL,
    body             MEDIUMTEXT NULL,
    meta_title       VARCHAR(200) NULL,
    meta_description VARCHAR(320) NULL,
    is_active        TINYINT(1) NOT NULL DEFAULT 1,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS faqs (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    service_id INT UNSIGNED NULL,
    question   VARCHAR(300) NOT NULL,
    answer     TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_faq_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS gallery (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    title      VARCHAR(200) NULL,
    file_path  VARCHAR(255) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name       VARCHAR(160) NOT NULL,
    phone      VARCHAR(40) NULL,
    email      VARCHAR(160) NULL,
    subject    VARCHAR(200) NULL,
    body       TEXT NOT NULL,
    is_read    TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET foreign_key_checks = 1;
