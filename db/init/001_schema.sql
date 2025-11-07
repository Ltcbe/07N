-- MariaDB schema for iRail ingestion (no 'connections' data stored)

CREATE TABLE IF NOT EXISTS stations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  station_id VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6),
  raw_json JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trips (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id VARCHAR(64) NOT NULL,
  date DATE NOT NULL,
  delay_sec INT DEFAULT 0,
  last_stop_planned DATETIME NOT NULL,
  last_stop_real DATETIME NULL,
  immutable_after DATETIME NOT NULL,
  is_immutable BOOLEAN DEFAULT FALSE,
  raw_json JSON,
  UNIQUE KEY u_trip (vehicle_id, date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trip_stops (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  trip_id BIGINT NOT NULL,
  stop_seq INT NOT NULL,
  station_id VARCHAR(64) NOT NULL,
  planned_arr DATETIME NULL,
  real_arr DATETIME NULL,
  arr_delay_sec INT NULL,
  planned_dep DATETIME NULL,
  real_dep DATETIME NULL,
  dep_delay_sec INT NULL,
  platform VARCHAR(16) NULL,
  canceled BOOLEAN DEFAULT FALSE,
  raw_json JSON,
  FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
  INDEX ix_tripstop_tripseq (trip_id, stop_seq)
) ENGINE=InnoDB;

DELIMITER $$
CREATE TRIGGER trips_prevent_update_after_immutable
BEFORE UPDATE ON trips FOR EACH ROW
BEGIN
  IF (OLD.is_immutable = TRUE) OR (NOW() >= OLD.immutable_after) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Trip is immutable';
  END IF;
END$$

CREATE TRIGGER tripstops_prevent_update_after_immutable
BEFORE UPDATE ON trip_stops FOR EACH ROW
BEGIN
  DECLARE parent_immutable DATETIME;
  SELECT immutable_after INTO parent_immutable FROM trips WHERE id = NEW.trip_id;
  IF (NOW() >= parent_immutable) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Trip stops are immutable';
  END IF;
END$$
DELIMITER ;
