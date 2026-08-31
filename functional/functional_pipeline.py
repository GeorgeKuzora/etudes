import logging
from functools import partial, reduce
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Callable, Self, Any


class Applications(StrEnum):
    """Приложения, для которых строятся пайплайны."""

    first = auto()
    second = auto()


@dataclass
class Context:
    """Контекст для работы пайплайна, содержит все необходимые данные."""
    application: Applications
    images: list
    responses: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Result:
    """Хранит значение контекста (value) и возможные ошибки (error)."""

    value: Context
    error: str | None = None

    @classmethod
    def ok(cls, value: Context) -> "Result":
        return cls(value=value)

    @classmethod
    def err(cls, error: str, value: Context) -> "Result":
        return cls(error=error, value=value)

    def map(self, func: Callable[[Context], Context]) -> "Result":
        if self.error:
            return self
        try:
            return Result.ok(func(self.value))
        except Exception as e:
            return Result.err(str(e), self.value)


def step(
    context: Context,
    adapter: Callable,
    execute: Callable,
    write: Callable,
):
    """
    Шаг пайплайна:
    1. adapter извлекает данные из контекста
    2. execute выполняет бизнес-логику
    3. write записывает результат обратно в контекст
    """
    kwargs = adapter(context)
    if isinstance(kwargs, dict):
        data = execute(**kwargs)
    else:
        data = execute(*kwargs)

    return write(data, context)


def gather(data: Any, context: Context, keys: list[str]) -> Context:
    ...

def build_responses(images, application) -> Any:
    ...

def is_normal_image(images) -> Any:
    ...

def is_images(images) -> Any:
    if not len(images):
        raise ValueError


def get_shape(images):
    ...

def pipe(*functions):
    def _compose(arg):
        # Проходим функции справа налево, передавая результат следующей
        return reduce(lambda acc, fn: fn(acc), functions, arg)
    return _compose

def create_pipeline():
    pipeline = [
        partial(
            step,
            adapter=lambda c: {'images': c.images, 'application': c.application},
            execute=build_responses,
            write=partial(gather, keys=['key1', 'key2']),
        ),
        partial(
            step,
            adapter=lambda c: {'images': c.images},
            execute=is_normal_image,
            write=partial(gather, keys=['key3']),
        ),
        partial(
            step,
            adapter=lambda c: {'images': c.images},
            execute=is_images,
            write=lambda context, data: context,
        ),
        partial(
            step,
            adapter=lambda c: {'images': c.images},
            execute=get_shape,
            write=partial(gather, keys=['key4']),
        ),
    ]
    return pipe(*pipeline)


def run(images, application, pipelines: dict[str, Callable]):
    context = Context(
        application=application,
        images=images,
    )
    result = Result.ok(context)

    pipeline = pipelines[application]

    final_result = result.map(pipeline)

    if final_result.error:
        logging.error(final_result.error)

    return [response_item.response() for response_item in final_result.value.responses]
