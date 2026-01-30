set -e

if [ -f "migrations/env.py" ]; then
  echo "Aplicando migrações..."
  flask db upgrade || true
fi

exec gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
