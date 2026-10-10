## streamstats
Простой потоковый анализатор логов для CSV и JSONL.

## Установка
pip install -e .

## Как запускать
python -m streamstats analyze input.jsonl --format jsonl --output report.json
python -m streamstats analyze input.jsonl --format jsonl --skip-invalid

## Как запустить тесты
python -m pytest