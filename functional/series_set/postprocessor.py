import logging
from dataclasses import dataclass
from datetime import datetime

from core.api.common_schemas import FieldChange
from core.api.types import PostprocessRequest
from core.context import AlgoBranchWrapper
from core.fields import CoreFieldName, PreparedDocumentFieldName, SourceName
from core.postprocess.change_field import change_field
from core.postprocess.consts import AA_SERIES, AB_SERIES, AC_SERIES, AB_SERIES_APPEAR_DATE
from core.postprocess.postprocessors.abstract import Postprocessor
from core.postprocess.postprocessors.common import get_mrz_field_value, get_visual_field_value
from core.postprocess.postprocessors.dates.parsers import iso8601_date_parser
from series_set import models
from series_set.rules_engine import RulesEngine


@dataclass
class SeriesPostprocessor(Postprocessor):
    """Восстанавливает серию для документов."""

    # валидные серии
    _aa_series = AA_SERIES
    _ac_series = AC_SERIES
    _ab_series = AB_SERIES
    _a_letter = _aa_series[1]
    _c_letter = _ac_series[1]
    _b_letter = _ab_series[1]

    def __post_init__(self) -> None:
        """Инициализирует движок правил для восстановления серии документа."""
        self._rules_engine = RulesEngine(
            models.RestorationDecision(
                fixed_by=None,
                series=None,
                branch=models.SeriesPostprocessBranches.valid_series_not_contained_in_candidates,
            ),
        )
        self._build_rules()

    def make_changes(  # noqa: WPS210
        self,
        current_date: datetime,
        request_data: PostprocessRequest,
    ) -> list[FieldChange]:
        """Восстанавливает серию для документов."""
        (
            visual_series,
            mrz_series,
            perforation_series,
        ) = self._extract_series_from_core(request_data)

        fixed_series, source = self._fix_series(
            visual_series=visual_series,
            mrz_series=mrz_series,
            perforation_series=perforation_series,
            issue_date=request_data.prepared_document.fields.issue_date,
        )

        changed_field = change_field(
            request_data=request_data,
            field_name=PreparedDocumentFieldName.document_series,
            postprocessed_value=fixed_series,
            source=source,
        )

        return [changed_field] if changed_field else []

    @property
    def target_fields(self) -> frozenset[PreparedDocumentFieldName]:
        """Список полей, которые может изменить постпроцессор."""
        return frozenset((PreparedDocumentFieldName.document_series,))

    def _fix_series(
        self,
        visual_series: str | None,
        mrz_series: str | None,
        perforation_series: str | None,
        issue_date: str | None,
    ) -> tuple[str | None, SourceName | None]:
        """Проверяет разные поля системы на наличие признаков серии.

         - Если в кандидатах есть только "AA", "AB" или "AC", то отдает соотвтетствующие серии;
         - Если в кандадатах есть "AA" и "AB", то оценивает по дате выдаче. Если дата выдачи есть и
        она более AB_SERIES_APPEAR_DATE, то отдает серию "AB", в противном случае "AA";
         - Если в кандидатах нет полного названия серий, ориентируется по наличию характерных букв.
        При наличии в кандидатах букв "A", "B" или "C", отдает соотвтетствующие серии;
         - При невыполнении ни одного из условий, отдает None.

         :param visual_series: Серия из визуальной части ответа системы
         :param mrz_series:  Серия из мрз части ответа системы
         :param perforation_series: Серия из поля перфорации ответа системы
         :param issue_date: Дата выдачи документа из итогового поля ответа системы
         :returns: Серию и поле, из которого восстановили значение
        """
        all_candidates = [
            # порядок в списке влияет на тип source,
            # который будет выбран при одинаковых значениях в полях
            models.SeriesCandidate(series=mrz_series, source=SourceName.mrz_fields),
            models.SeriesCandidate(series=visual_series, source=SourceName.visual_fields),
            models.SeriesCandidate(
                series=perforation_series, source=SourceName.perforation_number,
            ),
        ]
        issue_date_dt = iso8601_date_parser.str_to_date(issue_date)
        series_status = models.SeriesFoundInCandidates(
            is_aa=self._aa_series in all_candidates,
            is_ab=self._ab_series in all_candidates,
            is_ac=self._ac_series in all_candidates,
            is_a=self._a_letter in all_candidates,
            is_b=self._b_letter in all_candidates,
            is_c=self._c_letter in all_candidates,
            issue_date=issue_date_dt is not None
            and issue_date_dt > AB_SERIES_APPEAR_DATE,
        )

        restoration_decision = self._rules_engine.make_decision(series_status)

        series = restoration_decision.series
        fixed_by = restoration_decision.fixed_by
        branch = restoration_decision.branch

        source = self._get_source(all_candidates, fixed_by)

        logging.info(
            {
                'selector': 'series_postprocessor',
                'message': f'Restored {series=} by series/letter: {fixed_by}',
                'branch': branch.name,
                'candidates': f'Candidates: {mrz_series=}, {visual_series=}, {perforation_series=}',
            },
        )
        AlgoBranchWrapper.log_branch(
            branch, field=PreparedDocumentFieldName.document_series,
        )

        return series, source

    def _get_source(
        self,
        all_candidates: list[models.SeriesCandidate],
        fixed_by: str | None,
    ) -> SourceName | None:
        """Определяет источник серии."""
        for candidate in all_candidates:
            if fixed_by == candidate:
                return candidate.source
        return None

    def _extract_series_from_core(
        self,
        request_data: PostprocessRequest,
    ) -> tuple[str | None, str | None, str | None]:
        """Извлекает значения серии из mrz, visual и perforation_number полей."""
        mrz_series = get_mrz_field_value(request_data, CoreFieldName.series)
        visual_series = get_visual_field_value(request_data, CoreFieldName.series)
        perforation_number = get_visual_field_value(
            request_data, CoreFieldName.perforation_number,
        )
        try:
            perforation_series = perforation_number[:2]  # type: ignore[index]
        except (IndexError, TypeError):
            perforation_series = None

        return visual_series, mrz_series, perforation_series

    def _build_rules(self) -> None:
        """Создает набор правил для определения серии документа."""
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_aa,
                group=models.Series.double_letters_group,
                decision=models.RestorationDecision(
                    series=self._aa_series,
                    fixed_by=self._aa_series,
                    branch=models.SeriesPostprocessBranches.aa_series_contained_in_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_ac,
                group=models.Series.double_letters_group,
                decision=models.RestorationDecision(
                    series=self._ac_series,
                    fixed_by=self._ac_series,
                    branch=models.SeriesPostprocessBranches.ac_series_contained_in_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_ab,
                group=models.Series.double_letters_group,
                decision=models.RestorationDecision(
                    series=self._ab_series,
                    fixed_by=self._ab_series,
                    branch=models.SeriesPostprocessBranches.ab_series_contained_in_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_aa | models.Series.is_ab | models.Series.issue_date,
                group=models.Series.valid_date_with_mixed_candidates_group,
                decision=models.RestorationDecision(
                    series=self._ab_series,
                    fixed_by=self._ab_series,
                    branch=models.SeriesPostprocessBranches.ab_valid_date_with_mixed_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_aa | models.Series.is_ab,
                group=models.Series.valid_date_with_mixed_candidates_group,
                decision=models.RestorationDecision(
                    series=self._aa_series,
                    fixed_by=self._aa_series,
                    branch=models.SeriesPostprocessBranches.aa_valid_date_with_mixed_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_a,
                group=models.Series.single_letter_group,
                decision=models.RestorationDecision(
                    series=self._aa_series,
                    fixed_by=self._a_letter,
                    branch=models.SeriesPostprocessBranches.a_letter_contained_in_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_c,
                group=models.Series.single_letter_group,
                decision=models.RestorationDecision(
                    series=self._ac_series,
                    fixed_by=self._c_letter,
                    branch=models.SeriesPostprocessBranches.c_letter_contained_in_candidates,
                ),
            ),
        )
        self._rules_engine.add_rule(
            models.Rule(
                pattern=models.Series.is_b,
                group=models.Series.single_letter_group,
                decision=models.RestorationDecision(
                    series=self._ab_series,
                    fixed_by=self._b_letter,
                    branch=models.SeriesPostprocessBranches.b_letter_contained_in_candidates,
                ),
            ),
        )
