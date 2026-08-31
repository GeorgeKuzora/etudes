from dataclasses import dataclass, make_dataclass
from enum import IntFlag, StrEnum, auto
from typing import Any

from core.fields import SourceName

_INT32 = 32
_SERIES_COUNT = (1 << count for count in range(_INT32))


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


class Series(IntFlag):
    """Серии документа.

    При добавлении новых серий, необходимо добавить новый вариант
    в конец перечисления, аналогично уже существующим
    Пример:
    is_ad = next(_SERIES_COUNT)
    """

    is_aa = next(_SERIES_COUNT)
    is_ab = next(_SERIES_COUNT)
    is_ac = next(_SERIES_COUNT)
    issue_date = next(_SERIES_COUNT)
    is_a = next(_SERIES_COUNT)
    is_b = next(_SERIES_COUNT)
    is_c = next(_SERIES_COUNT)

    # Группы серий
    # Группы можно объединять через `|`
    # Пример:
    # general_group = double_letters_group | single_letter_group  # noqa: E800
    # При добавлении новой серии нужно добавить ее в группу
    # в которой эта серия должна проверяться, либо создать новую группу
    double_letters_group = is_aa | is_ab | is_ac
    valid_date_with_mixed_candidates_group = double_letters_group | issue_date
    single_letter_group = is_a | is_b | is_c


@dataclass
class SeriesCandidate:
    """Класс для кандидатов в серию."""

    series: str | None
    source: SourceName
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


def to_series(self: Any) -> Series:
    """Возвращает серии и их статусы в виде флагов серий.

    Для серий найденных в кандидитах устанавливается флаг - 1
    Для серий не найденных в кандидитах устанавливается флаг - 0

    :param self: Объект датакласса c полями типа bool
    :return: Представление серий и их статусов в виде флагов
    """
    flags = Series(0)
    for series, found in self.__dict__.items():
        if found:
            flags |= Series[series].value
    return flags


# Статус фактического наличия серии в кандидатах
SeriesFoundInCandidates = make_dataclass(
    'SeriesFoundInCandidates',
    [(str(part.name), bool) for part in Series],
    namespace={
        'to_series': to_series,
    },
)


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

    pattern: Series
    group: Series
    decision: RestorationDecision

    def match(self, series: Series) -> bool:
        """Проверяет, соответствуют ли серии правилу и группе.

        Из всех серий выбирает те которые входят в группу.
        Сравнивает серии в группе с заданным паттерном.

        :param series: Статус серий в формате флагов.
        :return: Сответствуют ли серии правилу и группе.
        """
        return (series & self.group) == self.pattern
