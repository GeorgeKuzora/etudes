#!/usr/bin/env python3
"""
Скрипт для обновления документов в Elasticsearch по doc_id.

Конфигурация ТОЛЬКО через переменные окружения:
    ELASTIC_HOST       — хост ES (дефолт: http://localhost:9200)
    ELASTIC_INDEX_NAME — имя индекса (дефолт: documents)
    DOC_IDS_LIST       — список ID через запятую или перенос строки (обязательно)
"""
from operator import add
from returns.pointfree import bind
from returns.curry import partial
from returns.pipeline import pipe
from returns.result import Result, Failure, Success
from functools import reduce
from collections import deque, defaultdict
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import StrEnum, Enum, auto
from typing import Any, Generator, Iterable, Self, Callable, Protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)


ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://localhost:9200")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX_NAME", "documents")

doc_ids_raw = os.getenv("DOC_IDS_LIST")

if not doc_ids_raw:
    print("ERROR: переменная окружения DOC_IDS_LIST не задана", file=sys.stderr)
    sys.exit(1)

DOC_IDS = [item.strip() for item in re.split(r"[,\n]+", doc_ids_raw) if item.strip()]


@dataclass(frozen=True)
class ElasticResponse:
    """Сырой ответ elastic."""

    doc_id: str
    status: int
    body: str


@dataclass(frozen=True)
class ElasticDocument:
    """Документ elastic."""

    doc_id: str
    document: dict[str, Any]

@dataclass(frozen=True)
class Payload:
    """Payload для отправки."""

    doc_id: str
    original_images_qnt: int
    payload: dict[str, dict[str, list]]

class Endpoint(StrEnum):
    """Эндпоинт клиента elastic."""

    doc = "_doc"
    update = "_update"


class Error(Enum):
    """Типы ошибок работы скрипта."""

    failure = auto()
    not_found = auto()
    skipped = auto()


@dataclass(frozen=True)
class Config():
    """Конфигурация клиента."""

    host: str
    index: str
    timeout_in_sec: int

class ElasticClient:
    """Клиент для отправки HTTP-запросов в Elasticsearch с использованием urllib."""

    def __init__(self, config: Config) -> None:
        self.host = config.host.rstrip("/")
        self.index = config.index
        self.timeout_in_sec = config.timeout_in_sec
        self.headers = {"Content-Type": "application/json", "Connection": "close"}

    def send_request(self, request: urllib.request.Request) -> tuple[int, str]:
        """Отправляет запрос, возвращает (status_code, response_body)."""
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_in_sec) as response:
                return response.status, response.read().decode("utf-8", errors="replace").strip()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace").strip()
        except urllib.error.URLError as e:
            raise ConnectionError(f"Network error: {e.reason}") from e

    def create_get_request(self, url_path: str) -> urllib.request.Request:
        """Создаёт GET-запрос."""
        return urllib.request.Request(
            f"{self.host}{url_path}",
            method="GET",
            headers=self.headers
        )

    def create_post_request(self, url_path: str, body: dict[str, Any]) -> urllib.request.Request:
        """Создаёт POST-запрос с JSON-кодированным телом."""
        data = json.dumps(body).encode("utf-8")
        return urllib.request.Request(
            f"{self.host}{url_path}",
            data=data,
            method="POST",
            headers=self.headers
        )

    def build_url(self, doc_id: str, endpoint: str) -> str:
        """Создаёт путь URL для документа. По умолчанию `_doc` для GET/полной замены, `_update` для частичного обновления."""
        return f"/{self.index}/{endpoint}/{urllib.parse.quote(doc_id, safe='')}"

    def fetch_document(self, doc_id: str) -> ElasticResponse:
        """GET /<index>/_doc/<doc_id>"""

        url = self.build_url(doc_id, endpoint=Endpoint.doc)
        req = self.create_get_request(url)
        status, body = self.send_request(req)
        return ElasticResponse(
            doc_id=doc_id,
            status=status,
            body=body,
        )

    def update_document(self, doc_id: str, payload: dict[str, Any]) -> ElasticResponse:
        """POST /<index>/_update/<doc_id> с JSON-телом."""
        url = self.build_url(doc_id, endpoint=Endpoint.update)
        req = self.create_post_request(url, payload)
        status, body = self.send_request(req)
        return ElasticResponse(
            doc_id=doc_id,
            status=status,
            body=body,
        )


def get_doc(fetch_document: Callable, doc_id: str) -> Result:
    """Обрабатывает один ответ от elastic."""
    try:
        fetch_resp = fetch_document(doc_id=doc_id)
    except ConnectionError as e:
        log.error("Получение документов: ошибка соединения для '%s': %s", doc_id, e)
        return Failure(Error.failure)
    except TimeoutError as e:
        log.error("Получение документов: таймаут для '%s': %s", doc_id, e)
        return Failure(Error.failure)
    except Exception as e:
        log.error("Получение документов: Неожиданная ошибка для '%s': %s: %s", doc_id, type(e).__name__, e)
        return Failure(Error.failure)

    return Success(fetch_resp)

def prepare_document(elastic_response: ElasticResponse) -> Result:
    """Подготавливает документы для обрабоки."""
    if elastic_response.status == 404:
        log.warning("Не найдено: doc_id=%s (HTTP 404)", elastic_response.doc_id)
        return Failure(Error.not_found)

    if elastic_response.status != 200:
        log.error(
            "Ошибка получения: doc_id=%s (HTTP %d) — %s",
            elastic_response.doc_id, elastic_response.status, elastic_response.body[:200]
        )
        return Failure(Error.failure)

    try:
        doc_data = json.loads(elastic_response.body)
    except json.JSONDecodeError as e:
        log.error("Не удалось распарсить ответ для doc_id=%s: %s", elastic_response.doc_id, e)
        return Failure(Error.failure)

    if not isinstance(doc_data, dict):
        log.error("Oтвет не является dict для doc_id=%s", elastic_response.doc_id)
        return Failure(Error.failure)

    document = ElasticDocument(doc_id=elastic_response.doc_id, document=doc_data)

    return Success(document)


def prepare_update_payload(es_get_response: dict) -> dict[str, dict[str, list]]:
    """
    Принимает ответ GET из Elasticsearch, оставляет только последний элемент
    в массиве 'images' (если существует более одного), и возвращает полезную нагрузку для API _update.
    """
    source = es_get_response.get("_source", {})
    images = source.get("images", [])

    if not isinstance(images, list):
        return {"doc": {"images": []}}

    if len(images) > 1:
        images = [images[-1]]

    return {"doc": {"images": images}}


def prepare_payload(elastic_doc: ElasticDocument) -> Result:
    """Подготавливает payload для elastic."""
    original_images_qnt = len(elastic_doc.document.get("_source", {}).get("images", []))

    if original_images_qnt <= 1:
        log.info(
            "Пропущено (нет изменений): doc_id=%s, images_count=%d",
            elastic_doc.doc_id, original_images_qnt,
        )
        return Failure(Error.skipped)

    update_payload = prepare_update_payload(elastic_doc.document)

    payload = Payload(
        doc_id=elastic_doc.doc_id,
        original_images_qnt=original_images_qnt,
        payload=update_payload,
    )

    return Success(payload)


def update_doc(update_document: Callable, payload: Payload) -> Result:
    """Обновляет документ в elastic."""
    try:
        upd_resp = update_document(
            doc_id=payload.doc_id,
            payload=payload.payload,
        )
    except ConnectionError as e:
        log.error("Обновление документа: ошибка соединения для '%s': %s", payload.doc_id, e)
        return Failure(Error.failure)
    except TimeoutError as e:
        log.error("Обновление документа: таймаут для '%s': %s", payload.doc_id, e)
        return Failure(Error.failure)
    except Exception as e:
        log.error("Обновление документа: Неожиданная ошибка для '%s': %s: %s", payload.doc_id, type(e).__name__, e)
        return Failure(Error.failure)

    if upd_resp.status != 200:
        log.error(
            "Ошибка обновления: doc_id=%s (HTTP %d) — %s",
            payload.doc_id, upd_resp.status, upd_resp.body[:200],
        )
        return Failure(Error.failure)

    log.info(
        "Обновлено: doc_id=%s, было_изображений=%d",
        payload.doc_id, payload.original_images_qnt,
    )
    return Success(payload)


@dataclass
class Stats:
    total: int = 0
    success: int = 0
    failure: int = 0
    not_found: int = 0
    skipped: int = 0

    def __add__(self, other: Stats) -> Stats:
        """Складывает две статистики."""
        return Stats(
            total=self.total + other.total,
            success=self.success + other.success,
            failure=self.failure + other.failure,
            not_found=self.not_found + other.not_found,
            skipped=self.skipped + other.skipped,
        )


def result_to_stats(result: Result) -> Stats:
    """Обрабатывает значение ошибки"""
    match result:
        case Success():
            return Stats(total=1, success=1)
        case Failure(Error.failure):
            return Stats(total=1, failure=1)
        case Failure(Error.not_found):
            return Stats(total=1, not_found=1)
        case Failure(Error.skipped):
            return Stats(total=1, skipped=1)
        case _:
            return Stats(total=1, failure=1)


def main() -> int:
    """Точка входа: конфигурирует и запускает пакетное обновление документов."""
    log.info("Старт: index=%r host=%r, задач: %d", ELASTIC_INDEX, ELASTIC_HOST, len(DOC_IDS))

    config = Config(
        host=ELASTIC_HOST,
        index=ELASTIC_INDEX,
        timeout_in_sec=10
    )

    client = ElasticClient(config)
    get_docs_from_elastic = partial(get_doc, client.fetch_document)
    update_docs_in_elastic = partial(update_doc, client.update_document)

    pipeline = pipe(
        get_docs_from_elastic,
        bind(prepare_document),
        bind(prepare_payload),
        bind(update_docs_in_elastic),
    )

    results = (pipeline(doc_id) for doc_id in DOC_IDS)

    stats = reduce(add, map(result_to_stats, results), Stats())

    log.info("Итог: всего=%d, успешно=%d, пропущено=%d, не_найдено=%d, ошибок=%d",
             stats.total, stats.success, stats.skipped, stats.not_found, stats.failure)

    return 1 if stats.failure > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
