# PostgreSQL版セットアップ手順

## 1. PostgreSQL DB作成
```bash
sudo -u postgres psql -f deploy/postgresql/init_databases.sql
```

## 2. Python依存関係
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Close側
```bash
cp deploy/postgresql/close.env.example close_side/.env
set -a
source close_side/.env
set +a
cd close_side
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8001
```

## 4. Open側
```bash
cp deploy/postgresql/open.env.example open_side/.env
set -a
source open_side/.env
set +a
cd open_side
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8002
```
