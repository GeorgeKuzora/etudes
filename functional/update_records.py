#!/usr/bin/env python3
"""
Скрипт для обновления документов в Elasticsearch по doc_id.

Конфигурация ТОЛЬКО через переменные окружения:
    ELASTIC_HOST       — хост ES (дефолт: http://localhost:9200)
    ELASTIC_INDEX_NAME — имя индекса (дефолт: documents)
    DOC_IDS_LIST       — список ID через запятую или перенос строки (обязательно)
"""
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

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
class ElasticPayload:
    """Документ elastic."""

    doc_id: str
    original_images_qnt: int
    payload: dict[str, dict[str, list]]

class Endpoint(StrEnum):
    """Эндпоинт клиента elastic."""

    doc = "_doc"
    update = "_update"



class ElasticClient:
    """Клиент для отправки HTTP-запросов в Elasticsearch с использованием urllib."""

    def __init__(self, host: str, index: str, timeout_in_sec: int) -> None:
        self.host = host.rstrip("/")
        self.index = index
        self.timeout_in_sec = timeout_in_sec
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


class ElasticService:
    """Обрабатывает ответы elastic."""

    def __init__(self, client: ElasticClient) -> None:
        """Инициализирует класс."""
        self.client = client
        self.stats = {"success": 0, "skipped": 0, "failed": 0, "not_found": 0}

    def get_docs_from_elastic(self, doc_ids: list[str]) -> list[ElasticResponse]:
        """Обрабатывает один ответ от elastic."""
        elastic_responses = []
        for doc_id in doc_ids:
            try:
                fetch_resp = self.client.fetch_document(doc_id=doc_id)
            except ConnectionError as e:
                log.error("Получение документов: ошибка соединения для '%s': %s", doc_id, e)
                self.stats["failed"] += 1
            except TimeoutError as e:
                log.error("Получение документов: таймаут для '%s': %s", doc_id, e)
                self.stats["failed"] += 1
            except Exception as e:
                log.error("Получение документов: Неожиданная ошибка для '%s': %s: %s", doc_id, type(e).__name__, e)
                self.stats["failed"] += 1
            else:
                elastic_responses.append(fetch_resp)
        return elastic_responses

    def prepare_documents(self, elastic_responses: list[ElasticResponse]) -> list[ElasticDocument]:
        """Подготавливает документы для обрабоки."""

        elastic_documents = []

        for fetch_resp in elastic_responses:
            if fetch_resp.status == 404:
                log.warning("Не найдено: doc_id=%s (HTTP 404)", fetch_resp.doc_id)
                self.stats["not_found"] += 1
                continue

            if fetch_resp.status != 200:
                log.error(
                    "Ошибка получения: doc_id=%s (HTTP %d) — %s",
                    fetch_resp.doc_id, fetch_resp.status, fetch_resp.body[:200]
                )
                self.stats["failed"] += 1
                continue

            try:
                doc_data = json.loads(fetch_resp.body)
            except json.JSONDecodeError as e:
                log.error("Не удалось распарсить ответ для doc_id=%s: %s", fetch_resp.doc_id, e)
                self.stats["failed"] += 1
                continue

            if not isinstance(doc_data, dict):
                log.error("Oтвет не является dict для doc_id=%s", fetch_resp.doc_id)
                self.stats["failed"] += 1
                continue

            document = ElasticDocument(doc_id=fetch_resp.doc_id, document=doc_data)
            elastic_documents.append(document)

        return elastic_documents

    def prepare_payloads(self, elastic_documents: list[ElasticDocument]) -> list[ElasticPayload]:
        """Подготавливает payload для elastic."""
        payloads = []
        for elastic_doc in elastic_documents:
            original_images_qnt = len(elastic_doc.document.get("_source", {}).get("images", []))

            if original_images_qnt <= 1:
                log.info(
                    "Пропущено (нет изменений): doc_id=%s, images_count=%d",
                    elastic_doc.doc_id, original_images_qnt,
                )
                self.stats["skipped"] += 1
                continue

            update_payload = self.prepare_update_payload(elastic_doc.document)
            payload = ElasticPayload(
                doc_id=elastic_doc.doc_id,
                original_images_qnt=original_images_qnt,
                payload=update_payload,
            )
            payloads.append(payload)
        return payloads

    def prepare_update_payload(self, es_get_response: dict) -> dict[str, dict[str, list]]:
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

    def update_docs_in_elastic(self, payloads: list[ElasticPayload]) -> None:
        """Обновляет документ в elastic."""
        for ep in payloads:
            try:
                upd_resp = self.client.update_document(
                    doc_id=ep.doc_id,
                    payload=ep.payload,
                )
            except ConnectionError as e:
                log.error("Обновление документа: ошибка соединения для '%s': %s", ep.doc_id, e)
                self.stats["failed"] += 1
                continue
            except TimeoutError as e:
                log.error("Обновление документа: таймаут для '%s': %s", ep.doc_id, e)
                self.stats["failed"] += 1
                continue
            except Exception as e:
                log.error("Обновление документа: Неожиданная ошибка для '%s': %s: %s", ep.doc_id, type(e).__name__, e)
                self.stats["failed"] += 1
                continue

            if upd_resp.status != 200:
                log.error(
                    "Ошибка обновления: doc_id=%s (HTTP %d) — %s",
                    ep.doc_id, upd_resp.status, upd_resp.body[:200],
                )
                self.stats["failed"] += 1
            else:
                log.info(
                    "Обновлено: doc_id=%s, было_изображений=%d",
                    ep.doc_id, ep.original_images_qnt,
                )
                self.stats["success"] += 1


def main() -> int:
    """Точка входа: конфигурирует и запускает пакетное обновление документов."""
    log.info("Старт: index=%r host=%r, задач: %d", ELASTIC_INDEX, ELASTIC_HOST, len(DOC_IDS))

    client = ElasticClient(host=ELASTIC_HOST, index=ELASTIC_INDEX, timeout_in_sec=10)

    service = ElasticService(client)

    raw_docs = service.get_docs_from_elastic(DOC_IDS)
    prepared_docs = service.prepare_documents(raw_docs)
    payloads = service.prepare_payloads(prepared_docs)
    service.update_docs_in_elastic(payloads)

    total = len(DOC_IDS)
    log.info("Итог: всего=%d, успешно=%d, пропущено=%d, не_найдено=%d, ошибок=%d",
             total, service.stats["success"], service.stats["skipped"], service.stats["not_found"], service.stats["failed"])

    return 1 if service.stats["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
