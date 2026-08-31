# Functional Fun

Тренировка паттернов функционального программирования на реальных production-задачах.

## Цель

Этот репозиторий — playground для изучения FP в Python. Здесь берётся императивный код из продакшена и переписывается шаг за шагом в сторону функциональной парадигмы: от мутабельного состояния к монадам, от batch-обработки к lazy-streaming пайплайнам, от `if/else` ошибок к `Result` ADT.

## Эволюция кода

Каждый шаг рефакторинга задокументирован в [HISTORY.md](./HISTORY.md). Текущая архитектура — результат пяти итераций:

### 1. Императивная версия — `update_records.py`

Классический батч-процессор с мутабельными счётчиками (`self.stats`), циклами `for`, и накоплением промежуточных списков на каждом этапе пайплайна:

```
fetch docs → prepare documents → build payloads → update docs
  [list]        [list]             [list]           (mutates self.stats)
```

### 2. Streaming Pipeline — вторая итерация

Переход к ленивым генераторам: `map` + `filter_none` вместо коллекций, каждый документ течёт через stages one-by-one. Но ошибки всё ещё моделируются через `None` + отдельный `filter_none`.

### 3. Result Monad — третья итерация

Собственная реализация `Result`, `curry`, `compose`, `chain` в `library.py`. Ошибки как first-class значения, `Success`/`Failure` вместо `None`.

### 4. Standard Library — четвёртая итерация

Замена кастомной `library.py` на пакет [`returns`](https://returns.readthedocs.io/):

- **`compose`/`chain` → `pipe`/`bind`** — pointfree композиции из `returns.pointfree`
- **`Success.of()`/`Failure(value=...)` → `Success()`/`Failure()`** — API согласовано с returns
- **Generator expression вместо list comprehension** — восстановлен streaming режим, memory usage constant
- **Удалена `library.py`** — 92 строки self-hosted монад заменены на проверенную библиотеку
- **Добавлен mypy плагин** — type inference над Result типами

```python
from returns.pipeline import pipe
from returns.pointfree import bind
from returns.curry import partial

# returns pipeline: каждый шаг принимает Result, short-circuit на Failure
pipeline = pipe(
    partial(get_doc, client.fetch_document),
    bind(prepare_document),
    bind(prepare_payload),
    bind(update_doc, client.update_document),
)

results = (pipeline(fid) for fid in DOC_IDS)
```

### 5. Monoid Stats — пятая итерация (текущая)

`Stats` реализует monoid через `__add__`, stats вычисляются через классический map-reduce:

- **`Stats` как монатоид** — `__add__` суммирует все поля, `Stats()` (все нули) — identity элемент
- **Разделение transform + combine**: `result_to_stats(Result) → Stats` затем `reduce(add, ..., Stats())`
- **Чистый reducer** — `operator.add` вместо кастомной логики с `+= 1` мутациями
- **`Config` dataclass** — три аргумента клиента объединены в один immutable объект
- **Убраны мутации** — ни одной `stats.field += 1` в коде, полный functional purity (кроме логов)

```python
from operator import add

def result_to_stats(result: Result) -> Stats:
    match result:
        case Success(): return Stats(total=1, success=1)
        case Failure(Error.failure): return Stats(total=1, failure=1)
        case Failure(Error.not_found): return Stats(total=1, not_found=1)
        case Failure(Error.skipped): return Stats(total=1, skipped=1)

stats = reduce(add, map(result_to_stats, results), Stats())
```

## Архитектура

```
┌──────────────────────────────────────────────────────┐
│                  DOC_IDS_LIST                         │
│              (env variable, required)                 │
└────────────────────┬─────────────────────────────────┘
                     ▼
       ┌─────────────────────────┐
       │     string -> Result     │  get_docs_from_elastic
       │      ElasticResponse     │
       └────────────┬────────────┘
                    │ bind()
                    ▼
       ┌─────────────────────────┐
       │    Result[ElasticDoc]    │  prepare_document
       │     or Failure[Error]    │     404, parse errors
       └────────────┬────────────┘
                    │ bind()
                    ▼
       ┌─────────────────────────┐
       │     Result[Payload]      │  prepare_payload
       │                         │  skip if ≤1 images
       └────────────┬────────────┘
                    │ bind()
                    ▼
       ┌─────────────────────────┐
       │   Result[UpdateResp]     │  update_docs_in_elastic
       │                         │  POST to ES _update
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │    reduce(+, Stats())    │  aggregate all results
       └─────────────────────────┘
```

## Используемые концепции

| Концепция | Где применяется |
|---|---|
| **Algebraic Data Types** | `Result` = `Success` \|\ `Failure` с tagged union |
| **Functor** | `Success.map(f)` / `Failure.map(f)` из `returns` |
| **Monad** | `.chain()` / `bind()` для комозиии монадических функций |
| **Function Composition** | `pipe(f, g, h)(x)` = `f(g(h(x)))` |
| **Currying / Partial Application** | `partial(fn, arg)` для привязки аргументов |
| **Lazy Evaluation** | Generator expressions `(pipeline(fid) for fid in ids)` |
| **Fold / Reduce** | `reduce(add, ..., Stats())` для агрегации без мутаций |
| **Pure Functions** | Трансформации данных без побочек (кроме логов) |
| **Immutable Data** | `@dataclass(frozen=True)` для всех DTO типов |

## Стек

- **Python 3.14**
- **[returns](https://returns.readthedocs.io)** — монады для Python (`Result`, `Maybe`, pointfree combinators)
- **mypy** с плагином `returns.contrib.mypy.returns_plugin` для type-checking монадических типов
- **ruff** — linting
- **pytest** — тестирование

## Запуск

```bash
poetry install
DOC_IDS_LIST=id1,id2,id3 python functional_update_records.py
```

Конфигурация: только переменные окружения (`ELASTIC_HOST`, `ELASTIC_INDEX_NAME`, `DOC_IDS_LIST`).

## Что дальше

В HISTORY.md описаны оставшиеся проблемы — следующая волна рефакторинга: IO monad для инкапсуляции side effects (логирование), более детальные типы ошибок вместо collapse в `Error.failure`, и возможно переход к async для concurrent execution pipeline stages. Unused imports (`deque`, `defaultdict`, `Self`, `Callable`, `Protocol`) также ждут очистки.
