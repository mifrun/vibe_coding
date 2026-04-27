# vibe_coding

Стартовый Python-проект с управлением зависимостями через Poetry.

## Первый запуск

Установить зависимости:

```bash
make install
```

Активировать окружение:

```bash
eval $(poetry env activate)
```

Проверить, что используется Python проекта:

```bash
make python
```

Проверить конфигурацию Poetry:

```bash
make check
```

## CrewAI-команда для кода

Запустить локальную команду агентов:

```bash
make agents task="Добавь FastAPI endpoint /health"
```

Runner использует CrewAI и переменные из `.env`:

```bash
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
```

В команде участвуют агенты:

```text
project_manager
lead_analyst
system_analyst
tech_lead
developer
qa
```

Конфиг команды лежит здесь:

```text
src/vibe_coding/config/agents.yaml
src/vibe_coding/config/tasks.yaml
```

Агенты могут читать файлы проекта, писать файлы проекта, запускать команды и смотреть `git diff`. Runner блокирует доступ к `.env`, `.venv` и `.git`.

## Переменные окружения

Локальные секреты лежат в `.env`. Этот файл не попадает в git.

Сейчас ожидаются переменные:

```bash
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
```

## Как добавлять зависимости

Основные зависимости:

```bash
make add pkg=package-name
```

Зависимости для разработки:

```bash
make add-dev pkg=package-name
```

После добавления зависимостей Poetry обновит `pyproject.toml` и `poetry.lock`.
