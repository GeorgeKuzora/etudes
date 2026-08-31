from memory_profiler import profile
import time
from enum import StrEnum
from functools import reduce
from itertools import chain, starmap
from dataclasses import dataclass
from types import MappingProxyType

class DocType(StrEnum):
    """Holds list of all known document types, including different versions of a single document."""

    any_document = 'any_document'
    not_document = 'not_document'

class DocField(StrEnum):
    """Список возможных полей в сегметации полей."""
    separator = 'separator'
    wide_issue_date = 'wide_issue_date'
    wide_expiration_date = 'wide_expiration_date'
    allowed_dates_of_stay = 'allowed_dates_of_stay'
    authority_eng = 'authority_eng'
    authority_nat = 'authority_nat'
    birth_date = 'birth_date'
    birth_place_eng = 'birth_place_eng'
    birth_place_nat = 'birth_place_nat'
    expiration_date = 'expiration_date'
    gender = 'gender'
    issue_code = 'issue_code'
    issue_date = 'issue_date'
    mrz = 'mrz'
    name_eng = 'name_eng'
    name_nat = 'name_nat'
    nationality_eng = 'nationality_eng'
    nationality_nat = 'nationality_nat'
    series = 'series'
    number = 'number'
    patronymic_eng = 'patronymic_eng'
    patronymic_nat = 'patronymic_nat'
    surname_eng = 'surname_eng'
    surname_nat = 'surname_nat'
    additional_number = 'additional_number'
    personal_number = 'personal_number'
    perforation_number = 'perforation_number'
    portrait_photo = 'portrait_photo'
    country_code = 'country_code'
    nationality_code = 'nationality_code'
    mrz_doc_code = 'mrz_doc_code'
    purpose_of_visit = 'purpose_of_visit'  # цель визита

@dataclass
class DocumentLayoutField:
    key: DocField
    regexp: str = '.*'
    output_keys: tuple | None = None
    multiline: bool = False  # является ли поле многострочным
    join_char: str = ' '  # символ, через который объединяются многострочные поля
    optional: bool = False
    recognizable: bool = True
    steps_config: dict | None = None
    gather_to_process: bool = True  # добавлять ли в ожидаемые поля, используется в REQUIRED_OUT_FIELDS
@dataclass
class DocumentLayoutPart:
    fields: list[DocumentLayoutField]


@dataclass
class DocumentLayout:
    code: DocType
    parts: list[DocumentLayoutPart]
    description: str

# @profile
def gather_document2fields_dict_old_version(
    docs: tuple[DocumentLayout],
) -> MappingProxyType[str, MappingProxyType[str, bool]]:
    """
    Для каждого типа документа создаёт словарь полей со значениями их атрибутов.
    """
    doc2fields = {}
    for doc in docs:
        doc_code = doc.code
        doc2fields[doc_code] = {}
        if doc.parts:
            for p in doc.parts:
                for f in p.fields:
                    doc2fields[doc_code][f.key] = MappingProxyType(
                        {
                            'optional': f.optional,
                            'recognizable': f.recognizable,
                            'multiline': f.multiline,
                            'regexp': f.regexp,
                        }
                    )
    return MappingProxyType(doc2fields)

###### NEW VERSION

doc_to_part = lambda doc: ((p, doc.code) for p in doc.parts)

part_to_field = lambda part, code: ((f, code) for f in part.fields)

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
    return mapping, code, field.key

def to_dict_by_code_by_key(acum: dict, mapping: tuple) -> dict:
    """Собирает mapping в словарь по code и key."""
    mapping_value, doc_code, field_key = mapping
    doc = acum.get(doc_code, {})
    doc[field_key] = mapping_value
    acum[doc_code] = doc
    return acum

# @profile
def gather_document2fields_dict_new_version(
    docs: tuple[DocumentLayout],
) -> MappingProxyType[str, MappingProxyType[str, bool]]:
    # docs_with_parts = (doc for doc in docs if doc.parts)
    #
    # parts = ((p, doc.code) for doc in docs_with_parts for p in doc.parts)
    # fields = ((f, code) for p, code in parts for f in p.fields)
    # mappings = (field_to_mapping(f, c) for f, c in fields)

    # parts = chain.from_iterable(map(doc_to_part, docs_with_parts))
    # fields = chain.from_iterable(starmap(part_to_field, parts))
    # mappings = starmap(field_to_mapping, fields)
    #
    # return MappingProxyType(reduce(to_dict_by_code_by_key, mappings, {}))

    return MappingProxyType({
        doc.code: (
            MappingProxyType({
                f.key: MappingProxyType({
                    'optional': f.optional,
                    'recognizable': f.recognizable,
                    'multiline': f.multiline,
                    'regexp': f.regexp,
                })
                for p in doc.parts
                for f in p.fields
            })
        ) if doc.parts else {}
        for doc in docs
    })

def create_document_layouts(count: int = 1, pcount: int = 1, fcount: int = 1) -> list[DocumentLayout]:
    base_fields = [
        DocumentLayoutField(key=field_enum)
        for field_enum in DocField
    ]
    repeated_fields = (base_fields * (-(-fcount // len(base_fields))))[:fcount]
    parts = [
        DocumentLayoutPart(fields=list(repeated_fields))
        for _ in range(pcount)
    ]
    return [
        DocumentLayout(
            code=DocType.any_document,
            parts=parts,
            description=f'document_{i}',
        )
        for i in range(count)
    ]

def main():
    data = create_document_layouts(100, 100, 10)


    start = time.perf_counter()
    new_data = gather_document2fields_dict_new_version(data)
    new_time = time.perf_counter() - start

    start = time.perf_counter()
    old_data = gather_document2fields_dict_old_version(data)
    old_time = time.perf_counter() - start

    ratio = old_time / new_time if new_time > 0 else float('inf')
    print(f'Old version: {old_time:.4f}s')
    print(f'New version: {new_time:.4f}s')
    print(f'Speedup:     {ratio:.2f}x')

    assert old_data == new_data, "Results mismatch"

if __name__ == "__main__":
    main()
