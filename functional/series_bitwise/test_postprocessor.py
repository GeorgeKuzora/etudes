from itertools import product

import pytest

from core.api.common_schemas import FieldChange
from core.api.schemas import UniversalPostprocessRequest
from core.fields import PreparedDocumentFieldName
from core.postprocess.consts import AA_SERIES, AB_SERIES, AC_SERIES
from series_bitwise.models import (
    SeriesFoundInCandidates,
    Series,
    RestorationDecision,
    SeriesPostprocessBranches,
)


@pytest.mark.parametrize_from_csv('data/series_postprocessor_test_data.csv')
def test_series_postprocessor(
    current_algorithm_branch,
    postprocessing_request: UniversalPostprocessRequest,
    field_changes: list[FieldChange],
    expected_branches,
    series_postprocessor,
):
    """Тестирует постпроцессор серии документа.

    :param current_algorithm_branch: Фикстура для отслеживания веток алгоритма
    :param postprocessing_request: Запрос на постобработку
    :param field_changes: Ожидаемые изменения полей
    :param expected_branches: Ожидаемые ветки алгоритма
    :param series_postprocessor: Постпроцессор серии документа
    """
    postprocessor_result = series_postprocessor.make_changes(
        request_data=postprocessing_request,
        current_date=None,
    )
    assert postprocessor_result == field_changes
    assert current_algorithm_branch.get() == {
        PreparedDocumentFieldName.document_series: expected_branches,
    }


@pytest.fixture
def generate_all_series_candidate_states() -> list[SeriesFoundInCandidates]:
    """Генерирует все возможные варианты SeriesFoundInCandidates.

    :return: Список из 128 объектов SeriesFoundInCandidates со всеми возможными
        комбинациями булевых значений.
    """
    boolean_values = [False, True]

    field_names = [series.name for series in Series]

    all_states = []
    for values in product(boolean_values, repeat=len(field_names)):
        state_kwargs = dict(zip(field_names, values))
        all_states.append(SeriesFoundInCandidates(**state_kwargs))

    return all_states


@pytest.fixture
def series_rules_engine(series_postprocessor):
    """Получает движок правил для постпроцессора серии документа.

    :param series_postprocessor: Постпроцессор серии документа
    :return: Настроенный движок правил
    """
    return series_postprocessor._rules_engine


def match_pattern(
    state_flags: Series,
    group: Series,
    pattern: Series,
) -> bool:
    """Проверяет подходит ли тестовый случай под паттерн."""
    return state_flags & group == pattern


def test_make_candidate_decision(
    series_rules_engine,
    generate_all_series_candidate_states: list[SeriesFoundInCandidates],
):
    """Тестирует принятие решений о восстановлении серии документа.

    :param series_rules_engine: Движок правил для принятия решений
    :param generate_all_series_candidate_states: Все возможные состояния кандидатов
    """
    for state in generate_all_series_candidate_states:
        decision = series_rules_engine.make_decision(state)
        series = state.to_series()

        if match_pattern(series, Series.double_letters_group, Series.is_aa):
            assert decision == RestorationDecision(
                series=AA_SERIES,
                fixed_by=AA_SERIES,
                branch=SeriesPostprocessBranches.aa_series_contained_in_candidates,
            )
        elif match_pattern(series, Series.double_letters_group, Series.is_ac):
            assert decision == RestorationDecision(
                series=AC_SERIES,
                fixed_by=AC_SERIES,
                branch=SeriesPostprocessBranches.ac_series_contained_in_candidates,
            )
        elif match_pattern(series, Series.double_letters_group, Series.is_ab):
            assert decision == RestorationDecision(
                series=AB_SERIES,
                fixed_by=AB_SERIES,
                branch=SeriesPostprocessBranches.ab_series_contained_in_candidates,
            )
        elif match_pattern(series, Series.valid_date_with_mixed_candidates_group, Series.is_aa | Series.is_ab | Series.issue_date):
            assert decision == RestorationDecision(
                series=AB_SERIES,
                fixed_by=AB_SERIES,
                branch=SeriesPostprocessBranches.ab_valid_date_with_mixed_candidates,
            )
        elif match_pattern(series, Series.valid_date_with_mixed_candidates_group, Series.is_aa | Series.is_ab):
            assert decision == RestorationDecision(
                series=AA_SERIES,
                fixed_by=AA_SERIES,
                branch=SeriesPostprocessBranches.aa_valid_date_with_mixed_candidates,
            )
        elif match_pattern(series, Series.single_letter_group, Series.is_a):
            assert decision == RestorationDecision(
                series=AA_SERIES,
                fixed_by='A',
                branch=SeriesPostprocessBranches.a_letter_contained_in_candidates,
            )
        elif match_pattern(series, Series.single_letter_group, Series.is_c):
            assert decision == RestorationDecision(
                series=AC_SERIES,
                fixed_by='C',
                branch=SeriesPostprocessBranches.c_letter_contained_in_candidates,
            )
        elif match_pattern(series, Series.single_letter_group, Series.is_b):
            assert decision == RestorationDecision(
                series=AB_SERIES,
                fixed_by='B',
                branch=SeriesPostprocessBranches.b_letter_contained_in_candidates,
            )
        else:
            assert decision == RestorationDecision(
                fixed_by=None,
                series=None,
                branch=SeriesPostprocessBranches.valid_series_not_contained_in_candidates,
            )
