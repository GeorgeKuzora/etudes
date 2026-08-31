from dataclasses import dataclass, make_dataclass, fields
from enum import IntFlag, StrEnum, auto
from typing import Any


class SeriesPostprocessBranches(StrEnum):
    """Идентификаторы веток алгоритма постобработки серии документа."""

    aa_series_contained_in_candidates = auto()
    ab_series_contained_in_candidates = auto()
    ac_series_contained_in_candidates = auto()
    a_letter_contained_in_candidates = auto()
    b_letter_contained_in_candidates = auto()
    c_letter_contained_in_candidates = auto()
    aa_valid_date_with_mixed_candidates = auto()
    ab_valid_date_with_mixed_candidates = auto()
    valid_series_not_contained_in_candidates = auto()

@dataclass
class SeriesCandidate:
    """Класс для кандидатов в серию."""

    series: str | None
    source: str
    found: bool = False

    @property
    def second_letter(self) -> str | None:
        """Возвращает вторую букву в series."""
        try:
            return self.series[1]  # type: ignore[index]
        except (TypeError, ValueError, IndexError):
            return None

    def __eq__(self, other: object) -> bool:
        """Определяем оператор сравнения, чтобы использовать в in."""
        variants = {self.series}
        if self.second_letter is not None:
            variants.add(self.second_letter)
        return other in variants


@dataclass(frozen=True)
class Series:
    """Серии документа."""

    is_aa: bool
    is_ab: bool
    is_ac: bool
    issue_date: bool
    is_a: bool
    is_b: bool
    is_c: bool

    def to_set(self) -> set[str]:
        """Возвращает множество названий флагов, которые установлены в True."""
        return {field.name for field in fields(self) if getattr(self, field.name)}

class Scope:
    double_letters_group = {"is_aa", "is_ab", "is_ac"}
    valid_date_with_mixed_candidates_group = double_letters_group | {"issue_date",}
    single_letter_group = {"is_a", "is_b", "is_c"}


@dataclass
class RestorationDecision:
    """Решение по восстановлению серии документа."""

    series: str | None
    fixed_by: str | None
    branch: SeriesPostprocessBranches


@dataclass
class Rule:
    """Правило для определения серии документа.

    :param pattern: Определяет какие серии должны быть True при проверки группы
    :param group: Группа серий которая будет проверяться на соответствие паттерну
    :param decision: Решение соответствующее паттерну и группе
    """

    expected: set
    scope: set
    decision: RestorationDecision

    def match(self, series: set) -> bool:
        """Проверяет, соответствуют ли серии правилу и группе."""
        return (series & self.scope) == self.expected
