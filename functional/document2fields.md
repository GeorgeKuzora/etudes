Проводя код-ревью, я натолкнулся в коде на одну пятимерную функцию из циклов и условий... После пережитого шока меня посетила муза, и я написал небольшой комментарий к этой проблеме.

Надеюсь, кто-нибудь найдет мои мысли познавательными.

# Как уйти от глубокой вложенности

## Описание проблемы

Существуют разные подходы как уйти от конструкций содержащих глубокую вложенность выражений `if` и `for`. Подглядев какие паттерны существуют в современных языках программирования, таких как Rust, видим что часто предпочтение отдается работе с итераторами, функциями и декларативному стилю.

На примере этой функции я хочу показать как можно применять подобный подход в своих рассуждениях.

Сейчас в этой функции пять уровней вложенных циклов и условий.

```python
def _gather_document2fields_dict(
    docs: tuple[DocumentLayout],
) -> MappingProxyType[str, MappingProxyType[str, bool]]:
    """
    Для каждого типа документа создаёт словарь полей со значениями их атрибутов.
    """
    doc2fields = {}
    for doc in docs:  # 1
        doc_code = doc.code.value
        doc2fields[doc_code] = {}
        if doc.parts:  # 2
            for p in doc.parts:  # 3
                for f in p.fields:  # 4
                    doc2fields[doc_code][f.key.value] = MappingProxyType(  # 5
                        {
                            'optional': f.optional,
                            'recognizable': f.recognizable,
                            'multiline': f.multiline,
                            'regexp': f.regexp,
                        }
                    )
    return MappingProxyType(doc2fields)
```

При достаточно простой логике реализуемой в функции, сложно проследить в уме как преобразуются значения.

## Как можно рассуждать о проблеме

В подобных алгоритмах происходит ряд преобразований данных:

1. Мы отфильтровываем список `docs` по условию:

```python
if doc.parts:
```

2. Мы преобразуем документ `doc` в части документа `doc_part`:

```python
for p in doc.parts:
```

3. Мы преобразуем часть документа `doc_part` в поля документа `field`:

```python
for f in p.fields:
```

4. Из поля документа `field` мы создаем `MappingProxyType`:

```python
MappingProxyType(
    {
        'optional': f.optional,
        'recognizable': f.recognizable,
        'multiline': f.multiline,
        'regexp': f.regexp,
    }
)
```

5. Мы записываем `MappingProxyType` в словарь `doc2fields`:

```python
doc2fields[doc_code][f.key.value] = MappingProxyType(...)
```

Всего пять шагов. Кстати столько же, сколько и уровней вложенности. Совпадение? Не думаю!

Каждый из этих шагов можно описать отдельной функцией. Такие функции будут работать не со списками, а с одиночным значениями того типа, из которого состоят списки.

Вот эти функции:

1. docs --filter--> doc_with_parts

```python
docs_with_parts = (doc for doc in docs if doc.parts)
```

C фильтром проще всего это просто comprehension создающие итератор с отфильтрованными значениями.

2. doc_with_parts -> doc_part

```python
doc_to_part = lambda doc: ((p, doc.code.value) for p in doc.parts)
```

Очень простая функция, я даже записал ее в виде lambda выражения для краткости. Из документа нам также нужно получить `doc_code`, поэтому я добавил его в кортеж.

Функция создает итератор по значениями из списка `doc.parts`. Итератор на каждом из своих циклов возвращает отдельный `part` вместе с `doc_type`

3. doc_part -> doc_field

```python
part_to_field = lambda part, code: ((f, code) for f in part.fields)
```

Функция аналогичная предыдущей. Отличие только в том, что `doc_code` приходит как аргумент, а итератор проходит по `field` в списке `part.fields`.

4. doc_field -> mappingproxytype

```python
def field_to_mapping(field, code) -> tuple:
    """Преобразует поле в MappingProxyType + code + key."""
    mapping = MappingProxyType(
        {
            'optional': field.optional,
            'recognizable': field.recognizable,
            'multiline': field.multiline,
            'regexp': field.regexp,
        }
    )
    return mapping, code, field.key.value
```

Здесь функция потолще, просто потому что нужно заполнить много полей в `MappingProxyType`. Но в тоже время она уже не должна возвращать итератор, так-как `field` преобразуется в `MappingProxyType` один к одному. Мы также возвращаем кортеж значений.

5. mappingproxytype --fold-> doc2fields

```python
def to_dict_by_code_by_key(acum: dict, mapping: tuple) -> dict:
    """Собирает mapping в словарь по code и key."""
    mapping_value, doc_code, field_key = mapping
    doc = acum.get(doc_code, {})
    doc[field_key] = mapping_value
    acum[doc_code] = doc
    return acum
```

Функция принимает `acum` - словарь в который записывается значение `mapping`. Кортеж `mapping` перед этим распаковываем на отдельные переменные.

Итого эти пять функций описывают все преобразования данных. Каждая из них работает с одиночным значением. Каждая из них явно описывает как данные меняются от шага к шагу. Каждую из них можно протестировать отдельно.

Теперь нужно лишь соединить их в основной функции `gather_document2fields_dict`.

Напомню, мы работаем с итераторами. Поэтому воспользуемся модулем из стандартной библиотеки `itertools`, плюс нам будет нужна функция `reduce`:

```python
from functools import reduce
from itertools import chain, starmap
```

Функции `starmap` преобразовывает значения внутри итераторов: `doc` -> `part` -> `field` -> `MappingProxyType`. Для этого она применяет написанные нами функции к каждому из значений внутри итератора, и возвращает итератор с преобразованными значениями.

После применения функции `starmap` для `doc` и `part` будут созданы итераторы содержащие итераторы значений. Для того, чтобы создать единый итератор со значениями, нужно использовать `chain.from_iterable`. Эта функция извлекает значения из каждого из вложенных итераторов и объединяет их в плоскую структуру.

Функция `reduce` сворачивает финальный итератор `mappings` в словарь, согласно алгоритму описанному в функции `to_dict_by_code_by_key`.

```python
def gather_document2fields_dict(
    docs: tuple[DocumentLayout],
) -> MappingProxyType[str, MappingProxyType[str, bool]]:
    docs_with_parts = (doc for doc in docs if doc.parts)
    parts = chain.from_iterable(starmap(doc_to_part, docs_with_parts))
    fields = chain.from_iterable(starmap(part_to_field, parts))
    mappings = starmap(field_to_mapping, fields)

    return MappingProxyType(reduce(to_dict_by_code_by_key, mappings, {}))
```

Итого весь алгоритм свелся к пяти последовательным шагам, по преобразованию одних значений в другие. При этом теперь можно с уверенностью судить о каждом шаге. В написанных функциях явно видны преобразования данных. Каждая из функций очень простая. При необходимости их можно использовать в других местах в коде.

Важно заметить, что так-как везде используются итераторы, не происходит лишних выделений памяти на списки данных, и производительность алгоритма остается на высоком уровне.

## Итог

Может возникнуть вопрос: зачем использовать специальные функции, если привычные циклы и так справляются, а логика `_gather_document2fields_dict` вполне проста? Однако на практике часто встречаются задачи, где приходится работать со сложными, глубоко вложенными структурами данных. В таких ситуациях можно выбрать один из двух подходов к мышлению. Первый — императивный: `Как написать функцию с несколькими циклами, чтобы поэтапно обработать этот список?`. Второй — декларативный: `Какие преобразования необходимо применить к данным, чтобы они приняли нужную форму?`. Сдвиг фокуса с вопроса `как перебрать` на вопрос `как преобразовать` иногда позволяет находить более чистые, читаемые и масштабируемые решения.

