CREATE TABLE IF NOT EXISTS fixed_expenses (
  id INT NOT NULL AUTO_INCREMENT,
  parent_id INT NULL,
  name VARCHAR(500) NOT NULL,
  note TEXT NULL,
  period_text VARCHAR(255) NULL,
  annual_amount DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  sort_order INT NOT NULL DEFAULT 0,
  source_row INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_fixed_parent (parent_id),
  CONSTRAINT fk_fixed_parent FOREIGN KEY (parent_id) REFERENCES fixed_expenses (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
  id INT NOT NULL AUTO_INCREMENT,
  expense_id INT NOT NULL,
  seq_no INT NOT NULL,
  amount DECIMAL(14,2) NOT NULL,
  paid_on DATE NULL,
  remark VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_pay_expense (expense_id),
  CONSTRAINT fk_pay_expense FOREIGN KEY (expense_id) REFERENCES fixed_expenses (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monthly_categories (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uniq_category_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monthly_expenses (
  id INT NOT NULL AUTO_INCREMENT,
  `year` SMALLINT NOT NULL,
  `month` TINYINT NOT NULL,
  category_id INT NOT NULL,
  amount DECIMAL(14,2) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uniq_month (year, month, category_id),
  CONSTRAINT fk_month_cat FOREIGN KEY (category_id) REFERENCES monthly_categories (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO monthly_categories (name, sort_order) VALUES
  ('电费', 1),
  ('水费', 2),
  ('天燃气', 3),
  ('集体宿舍', 4),
  ('王明旭宿舍', 5),
  ('快递费', 6),
  ('电话费', 7),
  ('系统维护费', 8),
  ('货拉拉', 9);
