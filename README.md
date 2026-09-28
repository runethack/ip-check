# ip-check

IP Address Checker - валидация и проверка IP-адресов через публичные сервисы.

## Что умеет

- Проверять корректность IPv4 и IPv6 адресов
- Определять тип адреса:
  - private
  - public
  - loopback
  - multicast
  - reserved
  - unspecified
- Проверять, является ли IP «реальным» по базовым правилам адресации
- Выполнять базовый lookup через публичные сервисы, если они доступны
- Работать как через Python, так и через CLI

## Установка

```bash
git clone https://github.com/runethack/ip-check.git
cd ip-check
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Использование

### Python

```python
from ip_checker import IPChecker

ips = ["8.8.8.8", "127.0.0.1", "2001:4860:4860::8888", "not-an-ip"]
for ip in ips:
    print(ip, IPChecker.validate(ip))
```

### CLI

```bash
python ip_checker.py --ip 8.8.8.8
python ip_checker.py --ip 2001:4860:4860::8888 --json
python ip_checker.py --ip 192.168.1.1 --services
```

## Пример результата

```json
{
  "input": "8.8.8.8",
  "is_valid": true,
  "version": 4,
  "normalized": "8.8.8.8",
  "is_private": false,
  "is_public": true,
  "is_reserved": false,
  "is_loopback": false,
  "is_multicast": false
}
```

## Примечание про сервисы

Проверка через сторонние сервисы — это дополнительный lookup. Они могут быть недоступны, ограничивать количество запросов или требовать API key. Скрипт корректно обрабатывает такие случаи и не падает при ошибках сервиса.

## Лицензия

MIT
