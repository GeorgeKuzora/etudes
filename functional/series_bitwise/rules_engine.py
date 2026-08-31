from series_bitwise.models import (
    RestorationDecision,
    Rule,
    SeriesFoundInCandidates,
)


class RulesEngine:
    """Движок правил для определения серии документа."""

    def __init__(self, default_decision: RestorationDecision) -> None:
        """Инициализирует движок правил."""
        self._default_decision = default_decision
        self.rules: list[Rule] = []

    def make_decision(
        self,
        series_status: SeriesFoundInCandidates,  # type: ignore
    ) -> RestorationDecision:
        """Принимает решение о восстановлении серии на основе состояния кандидата."""
        series = series_status.to_series()  # type: ignore

        for rule in self.rules:
            if rule.match(series):
                return rule.decision

        return self._default_decision

    def add_rule(self, rule: Rule) -> None:
        """Добавляет правило в движок."""
        self.rules.append(rule)
