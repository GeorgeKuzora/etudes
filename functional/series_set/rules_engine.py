from series_set.models import Series, RestorationDecision, Rule


class RulesEngine:
    """Движок правил для определения серии документа."""

    def __init__(self, default_decision: RestorationDecision) -> None:
        """Инициализирует движок правил."""
        self._default_decision = default_decision
        self.rules: list[Rule] = []

    def make_decision(
        self,
        series: Series,
    ) -> RestorationDecision:
        """Принимает решение о восстановлении серии на основе состояния кандидата."""
        set_series = series.to_set()

        for rule in self.rules:
            if rule.match(set_series):
                return rule.decision

        return self._default_decision

    def add_rule(self, rule: Rule) -> None:
        """Добавляет правило в движок."""
        self.rules.append(rule)
