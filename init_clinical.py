import os, psycopg2

DDL = r"""
CREATE TABLE IF NOT EXISTS titan.allergies(
  allergy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES titan.users(user_id) ON DELETE CASCADE,
  allergen TEXT NOT NULL,
  reaction TEXT,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS titan.medications(
  med_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES titan.users(user_id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  dose TEXT,
  route TEXT,
  freq TEXT,
  status TEXT NOT NULL DEFAULT 'current',
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS titan.labs(
  lab_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES titan.users(user_id) ON DELETE CASCADE,
  test_code TEXT,
  test_name TEXT NOT NULL,
  value TEXT NOT NULL,
  unit TEXT,
  ref_range TEXT,
  result_date DATE NOT NULL,
  source_note UUID,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS titan.procedures(
  proc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES titan.users(user_id) ON DELETE CASCADE,
  proc_type TEXT NOT NULL,
  proc_date DATE,
  result_text TEXT,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS titan.cardio_tests(
  ct_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES titan.users(user_id) ON DELETE CASCADE,
  modality TEXT NOT NULL,
  test_date DATE,
  ef_percent NUMERIC,
  findings TEXT,
  rbbb BOOLEAN,
  lbbb BOOLEAN,
  av_block TEXT,
  axis TEXT,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE VIEW titan.v_latest_lab AS
SELECT DISTINCT ON (user_id, test_code)
  user_id, test_code, test_name, value, unit, result_date
FROM titan.labs
WHERE result_date IS NOT NULL
ORDER BY user_id, test_code, result_date DESC, recorded_at DESC;

CREATE OR REPLACE VIEW titan.v_latest_procedure AS
SELECT DISTINCT ON (user_id, proc_type)
  user_id, proc_type, proc_date, result_text
FROM titan.procedures
ORDER BY user_id, proc_type, COALESCE(proc_date, '1900-01-01') DESC, recorded_at DESC;

CREATE OR REPLACE VIEW titan.v_latest_cardio AS
SELECT DISTINCT ON (user_id, modality)
  user_id, modality, test_date, ef_percent, findings, rbbb, lbbb, av_block, axis
FROM titan.cardio_tests
ORDER BY user_id, modality, COALESCE(test_date, '1900-01-01') DESC, recorded_at DESC;
"""

dsn = os.environ["DATABASE_URL"]
with psycopg2.connect(dsn) as c, c.cursor() as cur:
    cur.execute(DDL)
    c.commit()
print("OK: clinical tables & views created")
