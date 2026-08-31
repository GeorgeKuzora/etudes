from series_set.rules_engine import RulesEngine
import itertools
from dataclasses import fields
from series_set.models import Series, RestorationDecision, SeriesPostprocessBranches, Rule, Scope
from itertools import product

import pytest

@pytest.fixture
def generate_all_series_candidate_states() -> list[Series]:
    """Generates all 128 possible boolean combinations for the Series dataclass."""
    # Get the names of all fields in the dataclass dynamically
    field_names = [f.name for f in fields(Series)]

    bool_combinations = itertools.product([True, False], repeat=len(field_names))

    variants = []
    for combination in bool_combinations:
        kwargs = dict(zip(field_names, combination))

        variants.append(Series(**kwargs))

    return variants


@pytest.fixture
def rules_engine():
    """Получает движок правил для постпроцессора серии документа документа.

    :param series_postprocessor: Постпроцессор серии документа
    :return: Настроенный движок правил
    """
    engine = RulesEngine(
        default_decision=RestorationDecision(
            series=None,
            fixed_by=None,
            branch=SeriesPostprocessBranches.valid_series_not_contained_in_candidates
        )
    )
    engine.add_rule(
        Rule(
            expected={"is_aa",},
            scope=Scope.double_letters_group,
            decision=RestorationDecision(
                series="aa_series",
                fixed_by="aa_series",
                branch=SeriesPostprocessBranches.aa_series_contained_in_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_ac",},
            scope=Scope.double_letters_group,
            decision=RestorationDecision(
                series="ac_series",
                fixed_by="ac_series",
                branch=SeriesPostprocessBranches.ac_series_contained_in_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_ab",},
            scope=Scope.double_letters_group,
            decision=RestorationDecision(
                series="ab_series",
                fixed_by="ab_series",
                branch=SeriesPostprocessBranches.ab_series_contained_in_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_aa", "is_ab", "issue_date"},
            scope=Scope.valid_date_with_mixed_candidates_group,
            decision=RestorationDecision(
                series="ab_series",
                fixed_by="ab_series",
                branch=SeriesPostprocessBranches.ab_valid_date_with_mixed_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_aa", "is_ab"},
            scope=Scope.valid_date_with_mixed_candidates_group,
            decision=RestorationDecision(
                series="aa_series",
                fixed_by="aa_series",
                branch=SeriesPostprocessBranches.aa_valid_date_with_mixed_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_a",},
            scope=Scope.single_letter_group,
            decision=RestorationDecision(
                series="aa_series",
                fixed_by="a_letter",
                branch=SeriesPostprocessBranches.a_letter_contained_in_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_c",},
            scope=Scope.single_letter_group,
            decision=RestorationDecision(
                series="ac_series",
                fixed_by="c_letter",
                branch=SeriesPostprocessBranches.c_letter_contained_in_candidates,
            ),
        ),
    )
    engine.add_rule(
        Rule(
            expected={"is_b",},
            scope=Scope.single_letter_group,
            decision=RestorationDecision(
                series="ab_series",
                fixed_by="b_letter",
                branch=SeriesPostprocessBranches.b_letter_contained_in_candidates,
            ),
        ),
    )
    return engine



def match_pattern(
    state_flags: set,
    group: set,
    pattern: set,
) -> bool:
    """Проверяет подходит ли тестовый случай под паттерн."""
    return state_flags & group == pattern


def test_make_candidate_decision(
    rules_engine,
    generate_all_series_candidate_states: list[Series],
):
    """Тестирует принятие решений о восстановлении серии документа.

    :param series_rules_engine: Движок правил для принятия решений
    :param generate_all_series_candidate_states: Все возможные состояния кандидатов
    """
    for state in generate_all_series_candidate_states:
        decision = rules_engine.make_decision(state)
        series = state.to_set()

        if match_pattern(series, Scope.double_letters_group, {"is_aa",}):
            assert decision == RestorationDecision(
                series="aa_series",
                fixed_by="aa_series",
                branch=SeriesPostprocessBranches.aa_series_contained_in_candidates,
            )
        elif match_pattern(series, Scope.double_letters_group, {"is_ac",}):
            assert decision == RestorationDecision(
                series="ac_series",
                fixed_by="ac_series",
                branch=SeriesPostprocessBranches.ac_series_contained_in_candidates,
            )
        elif match_pattern(series, Scope.double_letters_group, {"is_ab",}):
            assert decision == RestorationDecision(
                series="ab_series",
                fixed_by="ab_series",
                branch=SeriesPostprocessBranches.ab_series_contained_in_candidates,
            )
        elif match_pattern(series, Scope.valid_date_with_mixed_candidates_group, {"is_aa", "is_ab", "issue_date"}):
            assert decision == RestorationDecision(
                series="ab_series",
                fixed_by="ab_series",
                branch=SeriesPostprocessBranches.ab_valid_date_with_mixed_candidates,
            )
        elif match_pattern(series, Scope.valid_date_with_mixed_candidates_group, {"is_aa", "is_ab"}):
            assert decision == RestorationDecision(
                series="aa_series",
                fixed_by="aa_series",
                branch=SeriesPostprocessBranches.aa_valid_date_with_mixed_candidates,
            )
        elif match_pattern(series, Scope.single_letter_group, {"is_a",}):
            assert decision == RestorationDecision(
                series="aa_series",
                fixed_by='a_letter',
                branch=SeriesPostprocessBranches.a_letter_contained_in_candidates,
            )
        elif match_pattern(series, Scope.single_letter_group, {"is_c",}):
            assert decision == RestorationDecision(
                series="ac_series",
                fixed_by='c_letter',
                branch=SeriesPostprocessBranches.c_letter_contained_in_candidates,
            )
        elif match_pattern(series, Scope.single_letter_group, {"is_b",}):
            assert decision == RestorationDecision(
                series="ab_series",
                fixed_by='b_letter',
                branch=SeriesPostprocessBranches.b_letter_contained_in_candidates,
            )
        else:
            assert decision == RestorationDecision(
                fixed_by=None,
                series=None,
                branch=SeriesPostprocessBranches.valid_series_not_contained_in_candidates,
            )

