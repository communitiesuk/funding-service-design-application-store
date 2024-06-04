import inspect
from dataclasses import dataclass
from typing import Optional


@dataclass
class FeedbackSurveyConfig:
    has_feedback_survey: bool = False
    is_feedback_survey_optional: bool = True
    has_section_feedback: bool = False
    is_section_feedback_optional: bool = True
    has_research_survey: bool = False
    is_research_survey_optional: bool = True

    @staticmethod
    def from_json(d: dict):
        # Filter unknown fields from JSON dictionary
        return FeedbackSurveyConfig(
            **{k: v for k, v in d.items() if k in inspect.signature(FeedbackSurveyConfig).parameters}
        )


@dataclass
class Round:
    id: str
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str
    contact_email: str
    title_json: str
    project_name_field_id: Optional[str] = None
    mark_as_complete_enabled: bool = False
    is_expression_of_interest: bool = False
    feedback_survey_config: FeedbackSurveyConfig = None

    def __post_init__(self):
        if isinstance(self.feedback_survey_config, dict):
            self.feedback_survey_config = FeedbackSurveyConfig.from_json(self.feedback_survey_config)
        elif self.feedback_survey_config is None:
            self.feedback_survey_config = FeedbackSurveyConfig()

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data["title"],
            id=data["id"],
            fund_id=data["fund_id"],
            short_name=data["short_name"],
            opens=data["opens"],
            deadline=data["deadline"],
            assessment_deadline=data["assessment_deadline"],
            project_name_field_id=data.get("project_name_field_id", None),
            contact_email=data.get("contact_email", None),
            feedback_survey_config=data.get("feedback_survey_config") or FeedbackSurveyConfig(),
            mark_as_complete_enabled=data.get("mark_as_complete_enabled") or False,
            is_expression_of_interest=data.get("is_expression_of_interest") or False,
            title_json=data["title_json"],
        )
