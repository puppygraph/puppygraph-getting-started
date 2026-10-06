-- Tiny payments dataset for the PuppyGraph x Omnigent demo.
-- Plain relational tables: PuppyGraph queries them in place as a graph (no ETL).
CREATE SCHEMA fraud;

CREATE TABLE fraud.account (
  id         TEXT PRIMARY KEY,
  owner_name TEXT NOT NULL,
  country    TEXT NOT NULL,
  status     TEXT NOT NULL,          -- 'active' | 'flagged'
  opened_at  TIMESTAMP NOT NULL
);

CREATE TABLE fraud.device (
  id          TEXT PRIMARY KEY,
  fingerprint TEXT NOT NULL,
  os          TEXT NOT NULL
);

CREATE TABLE fraud.uses_device (
  id         TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES fraud.account(id),
  device_id  TEXT NOT NULL REFERENCES fraud.device(id),
  first_seen TIMESTAMP NOT NULL
);

CREATE TABLE fraud.transfer (
  id      TEXT PRIMARY KEY,
  from_id TEXT NOT NULL REFERENCES fraud.account(id),
  to_id   TEXT NOT NULL REFERENCES fraud.account(id),
  amount  DOUBLE PRECISION NOT NULL,
  ts      TIMESTAMP NOT NULL
);

INSERT INTO fraud.account VALUES
  ('acc_001','Alice Moreno','US','active','2024-01-10'),
  ('acc_002','Bruno Keller','DE','active','2024-02-03'),
  ('acc_003','Chen Wei','SG','active','2024-02-21'),
  ('acc_004','Dana Okafor','NG','active','2024-03-15'),
  ('acc_005','Eli Novak','CZ','active','2024-04-01'),
  ('acc_006','Farah Haddad','AE','active','2024-04-18'),
  ('acc_007','Gus Lindqvist','SE','flagged','2025-06-02'),
  ('acc_008','Hana Sato','JP','active','2025-06-03'),
  ('acc_009','Ivan Petrov','BG','active','2025-06-03'),
  ('acc_010','Jade Liu','HK','active','2025-06-04'),
  ('acc_011','Kofi Mensah','GH','active','2024-05-09'),
  ('acc_012','Lena Fischer','AT','active','2024-06-12'),
  ('acc_013','Mateo Rossi','IT','active','2024-07-07'),
  ('acc_014','Nia Brooks','US','active','2024-08-19'),
  ('acc_015','Omar Aziz','MA','active','2025-06-05');

INSERT INTO fraud.device VALUES
  ('dev_01','fp-9f2c','iOS 18'),
  ('dev_02','fp-1a7e','Android 15'),
  ('dev_03','fp-77b0','Windows 11'),
  ('dev_04','fp-c3d9','macOS 15'),
  ('dev_05','fp-e81f','Android 14'),   -- shared "burner" device of the ring
  ('dev_06','fp-0b44','iOS 17');

INSERT INTO fraud.uses_device VALUES
  ('ud_01','acc_001','dev_01','2024-01-10'),
  ('ud_02','acc_002','dev_02','2024-02-03'),
  ('ud_03','acc_003','dev_03','2024-02-21'),
  ('ud_04','acc_004','dev_04','2024-03-15'),
  ('ud_05','acc_005','dev_02','2024-04-01'),
  ('ud_06','acc_006','dev_06','2024-04-18'),
  ('ud_07','acc_007','dev_05','2025-06-02'),
  ('ud_08','acc_008','dev_05','2025-06-03'),
  ('ud_09','acc_009','dev_05','2025-06-03'),
  ('ud_10','acc_010','dev_05','2025-06-04'),
  ('ud_11','acc_011','dev_03','2024-05-09'),
  ('ud_12','acc_012','dev_04','2024-06-12'),
  ('ud_13','acc_013','dev_01','2024-07-07'),
  ('ud_14','acc_014','dev_06','2024-08-19'),
  ('ud_15','acc_015','dev_02','2025-06-05');

INSERT INTO fraud.transfer VALUES
  -- normal activity
  ('tx_001','acc_001','acc_002',  120.00,'2025-05-01 09:00'),
  ('tx_002','acc_002','acc_003',   75.50,'2025-05-02 10:30'),
  ('tx_003','acc_003','acc_004',  300.00,'2025-05-03 14:10'),
  ('tx_004','acc_004','acc_001',   42.00,'2025-05-04 08:45'),
  ('tx_005','acc_011','acc_012',  990.00,'2025-05-05 16:20'),
  ('tx_006','acc_013','acc_014',   60.00,'2025-05-06 12:00'),
  ('tx_007','acc_006','acc_005',  210.00,'2025-05-07 11:11'),
  -- the ring: fast layering through fresh accounts sharing dev_05, then out and back
  ('tx_101','acc_007','acc_008', 9500.00,'2025-06-06 01:02'),
  ('tx_102','acc_008','acc_009', 9400.00,'2025-06-06 01:09'),
  ('tx_103','acc_009','acc_010', 9300.00,'2025-06-06 01:15'),
  ('tx_104','acc_010','acc_015', 9200.00,'2025-06-06 01:22'),
  ('tx_105','acc_015','acc_007', 9100.00,'2025-06-06 01:30'),
  ('tx_106','acc_010','acc_005', 4000.00,'2025-06-06 01:40'),
  ('tx_107','acc_005','acc_006', 3900.00,'2025-06-06 02:05');
