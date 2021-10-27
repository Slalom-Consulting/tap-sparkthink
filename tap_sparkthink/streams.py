"""Stream type classes for tap-sparkthink."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sparkthink.client import ProjectBasedStream, sparkthinkStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class MyProjectsStream(sparkthinkStream):
    """Define custom stream."""
    name = "my_projects"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("id", th.StringType),
        th.Property("email", th.StringType),
        th.Property(
            "projects",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("title", th.StringType),
                    th.Property("__typename", th.StringType),
                )
            )
        ),
        # th.Property("project_id", th.StringType),
    ).to_dict()
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.data.me"

    query = """
        query {
            me { 
                id
                name
                email
                projects {
                    id
                    title
                    __typename
                }
            }
        }
        """


class ProjectsListStream(sparkthinkStream):
    """Define custom stream."""
    name = "projects_list"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("clientName", th.StringType),
        th.Property("coverImageUrl", th.StringType),
        th.Property("description", th.StringType),
        th.Property(
            "metadata",
            th.ObjectType(
                th.Property(
                    "createdBy", 
                    th.ObjectType(
                        th.Property("id", th.StringType),        
                        th.Property("name", th.StringType),       
                        th.Property("email", th.StringType),
                    )
                ), 
                th.Property("createdUTC", th.DateTimeType),
                th.Property("lastModifiedUTC", th.DateTimeType),             
            )
        ),
        th.Property("participantCount", th.StringType),
        th.Property(
            "responseMetrics",
            th.ObjectType(
                th.Property("completedUsers", th.IntegerType),
                th.Property("inProgressUsers", th.IntegerType),
                th.Property("invitedUsers", th.IntegerType),
            )
        ),
        th.Property("status", th.StringType),
        th.Property("theme", th.StringType),
        th.Property("title", th.StringType),
        th.Property("__typename", th.StringType),
    ).to_dict()
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.data.projects[*]"

    @property
    def query(self) -> str:
        return """
            query ProjectsList {
                """  \
             + "projects" + """ {
                    id
                    clientName
                    coverImageUrl
                    description
                    metadata {
                        createdBy {
                            id
                            name
                            email
                        }
                        createdUTC
                        lastModifiedUTC
                    } 
                    ...on Survey {
                        responseMetrics {
                            completedUsers
                            inProgressUsers
                            invitedUsers
                        }
                    }
                    ...on Workshop {
                        participantCount
                    }
                    status
                    theme
                    title
                    __typename
                }
            }
            """

class ProjectStream(ProjectBasedStream):
    """Define custom stream."""
    name = "project"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("clientName", th.StringType),
        th.Property("coverImageUrl", th.StringType),
        th.Property("description", th.StringType),
        th.Property(
            "metadata",
            th.ObjectType(
                th.Property(
                    "createdBy", 
                    th.ObjectType(
                        th.Property("id", th.StringType),        
                        th.Property("name", th.StringType),       
                        th.Property("email", th.StringType),
                    )
                ), 
                th.Property("createdUTC", th.DateTimeType),
                th.Property("lastModifiedUTC", th.DateTimeType),             
            )
        ),
        th.Property("participantCount", th.StringType),
        th.Property(
            "responseMetrics",
            th.ObjectType(
                th.Property("completedUsers", th.IntegerType),
                th.Property("inProgressUsers", th.IntegerType),
                th.Property("invitedUsers", th.IntegerType),
            )
        ),
        th.Property("status", th.StringType),
        th.Property("theme", th.StringType),
        th.Property("title", th.StringType),
        th.Property("__typename", th.StringType),
    ).to_dict()
    primary_keys = ["project_id"]
    replication_key = None
    records_jsonpath = "$.data.project"

    @property
    def query(self) -> str:
        return """
            query ProjectDetails($project_id: ID!) {
                """  \
             + "project(id: $project_id, type: Survey)" + """{
                    clientName
                    coverImageUrl
                    description
                    metadata {
                        createdBy {
                            id
                            name
                            email
                        }
                        createdUTC
                        lastModifiedUTC
                    } 
                    ...on Survey {
                        responseMetrics {
                            completedUsers
                            inProgressUsers
                            invitedUsers
                        }
                    }
                    ...on Workshop {
                        participantCount
                    }
                    status
                    theme
                    title
                    __typename
                }
            }
            """


class TeamMembersStream(ProjectBasedStream):
    """Define custom stream."""
    name = "teamMembers"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("role", th.StringType),
    ).to_dict()
    primary_keys = ["project_id", "id"]
    replication_key = None
    records_jsonpath = "$.data.project.teamMembers[*]"

    @property
    def query(self) -> str:
        return """
            query TeamMemberDetails($project_id: ID!) {
                """  \
            + f"project(id: $project_id, type: Survey)" + """{
                    teamMembers{
                        id
                        name
                        email
                        role
                    }
                }
            }
            """    


class RespondentsStream(ProjectBasedStream):
    """Define custom stream."""
    name = "respondents"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("userId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("collectorId", th.StringType),
        th.Property("collectorTitle", th.StringType),
        th.Property("projectId", th.StringType), # todo: check if this matches project_id in all cases
        th.Property(
            "attributes",
            th.ArrayType(
                th.ObjectType(
                    th.Property("key", th.StringType),
                    th.Property("value", th.StringType),
                )
            )
        ),
    ).to_dict()
    primary_keys = ["project_id", "userId"]
    replication_key = None
    records_jsonpath = "$.data.project.respondents[*]"

    @property
    def query(self) -> str:
        return """
            query RespondentDetails($project_id: ID!) {
                """  \
            + f"project(id: $project_id)" + """{
                    respondents {
                        userId
                        name
                        email
                        collectorId
                        collectorTitle
                        projectId
                        attributes {
                            key
                            value
                        }
                    }
                }
            }
            """    



class ResponsesStream(ProjectBasedStream):
    """Define custom stream."""
    name = "responses"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("id", th.StringType),
        th.Property("__typename", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("locale", th.StringType),
        th.Property(
            "metadata",
            th.ObjectType(
                th.Property(
                    "createdBy", 
                    th.ObjectType(
                        th.Property("id", th.StringType),        
                        th.Property("name", th.StringType),       
                        th.Property("email", th.StringType),
                    )
                ), 
                th.Property("createdUTC", th.DateTimeType),
                th.Property("lastModifiedUTC", th.DateTimeType),             
            )
        ),
        th.Property("questionId", th.StringType),
        th.Property(
            "NestedOptionResponseOptions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("label", th.StringType),
                    th.Property(
                        "value", 
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("id", th.StringType),
                                th.Property("label", th.StringType),
                                th.Property("additionalUserInput", th.StringType),
                            )
                        )
                    )
                )
            )
        ),
        th.Property(
            "OptionResponseValue",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("label", th.StringType),
                    th.Property("additionalUserInput", th.StringType),
                )
            )
        ),
        th.Property("NumericResponseValue", th.IntegerType),
        th.Property("TextResponseValue",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("userInput", th.StringType),
                )
            )
        ),
        th.Property(
            "ListResponseValue",
            th.ArrayType(th.StringType)
        ),
    ).to_dict()
    primary_keys = ["project_id", "id"]
    replication_key = None
    records_jsonpath = "$.data.project.responses.edges[*].node"
    next_page_token_jsonpath = "$.data.project.responses.edges[-1:].cursor"

    @property
    def query(self) -> str:
        return """
            query Responses($project_id: ID!, $response_batch_size: Int, $cursor: String) {
                """  \
            + f"project(id: $project_id)" + """{
                    responses(first: $response_batch_size, after: $cursor) {
                                edges {
                                    node {
                                        id
                                        __typename
                                        active
                                        locale
                                        metadata {
                                            createdBy {
                                                id
                                                name
                                                email
                                            }
                                            createdUTC
                                            lastModifiedUTC
                                        }
                                        questionId
                                        ... on NestedOptionResponse {
                                            NestedOptionResponseOptions: options {
                                                id
                                                label
                                                value {
                                                    id
                                                    label
                                                    additionalUserInput
                                                }
                                            }
                                        }
                                        ... on TextResponse {
                                            TextResponseValue: value {
                                                id 
                                                userInput
                                            }
                                        }
                                        ... on NumericResponse {
                                            NumericResponseValue: value
                                        }
                                        ... on OptionResponse {
                                            OptionResponseValue: value {
                                                id
                                                label
                                                additionalUserInput
                                            }
                                        }
                                        ... on ListResponse {
                                            ListResponseValue: value
                                        }
                                    }
                                    cursor
                                }
                            }
                        }
                    }
                    """


class QuestionsStream(ProjectBasedStream):
    """Define custom stream."""
    name = "questions"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("id", th.StringType),
        th.Property("__typename", th.StringType),
        th.Property("required", th.BooleanType),
        th.Property(
            "metadata",
            th.ObjectType(
                th.Property(
                    "createdBy", 
                    th.ObjectType(
                        th.Property("id", th.StringType),        
                        th.Property("name", th.StringType),       
                        th.Property("email", th.StringType),
                    )
                ), 
                th.Property("createdUTC", th.DateTimeType),
                th.Property("lastModifiedUTC", th.DateTimeType),             
            )
        ),
        th.Property(
            "content",
            th.ObjectType(
                th.Property("__typename", th.StringType),
                th.Property("allowMultiple", th.BooleanType),
                th.Property(
                    "answers", 
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("label", th.StringType),
                        )
                    )
                ),
                th.Property("backgroundImageUrl", th.StringType),
                th.Property(
                    "columns", 
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("hasFollowUp", th.BooleanType),
                            th.Property("followUpQuestion", th.StringType),
                            th.Property("label", th.StringType),
                        )
                    )
                ),
                th.Property("description", th.StringType),
                th.Property("inputs", th.IntegerType),
                th.Property(
                    "labels", 
                    th.ObjectType(
                        th.Property("left", th.StringType),
                        th.Property("middle", th.StringType),
                        th.Property("right", th.StringType),
                    )
                ),
                th.Property("moreInfoText", th.StringType),
                th.Property("multipleChoiceMaxSelectionCount", th.IntegerType),
                th.Property("multipleChoiceStackContentMaxSelectionCount", th.StringType),
                th.Property(
                    "placeholderText", 
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("label", th.StringType),
                        )
                    )
                ),
                th.Property("randomizeAnswers", th.BooleanType),
                th.Property(
                    "rows", 
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("title", th.StringType),
                            th.Property("description", th.StringType),
                        )
                    )
                ),
                th.Property("showLabels", th.BooleanType),
                th.Property("showOther", th.BooleanType),
                th.Property(
                    "subQuestions", 
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.StringType),
                            th.Property("title", th.StringType),
                            th.Property("description", th.StringType),
                        )
                    )
                ),
                th.Property("steps", th.IntegerType),
                th.Property("title", th.StringType),
            )
        ),
        th.Property("hidden", th.BooleanType),
        th.Property(
            "logic",
            th.ObjectType(
                th.Property(
                    "preLogicRules",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("logicRuleId", th.StringType),
                            th.Property(
                                "action", 
                                th.ObjectType(
                                    th.Property("contextItemId", th.StringType),
                                    th.Property("contextItemType", th.StringType),
                                    th.Property("targetItemId", th.StringType),
                                    th.Property("targetItemType", th.StringType),
                                    th.Property("verb", th.StringType),
                                )
                            ),
                            th.Property(
                                "condition", 
                                th.ObjectType(
                                    th.Property("compareOperator", th.StringType),
                                    th.Property("compareValue", th.StringType),
                                    th.Property("contextItemId", th.StringType),
                                    th.Property("contextItemType", th.StringType),
                                    th.Property("sourceItemId", th.StringType),
                                    th.Property("sourceItemType", th.StringType),
                                )
                            ),
                        )
                    )
                ),
                th.Property(
                    "postLogicRules",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("logicRuleId", th.StringType),
                            th.Property(
                                "action", 
                                th.ObjectType(
                                    th.Property("contextItemId", th.StringType),
                                    th.Property("contextItemType", th.StringType),
                                    th.Property("targetItemId", th.StringType),
                                    th.Property("targetItemType", th.StringType),
                                    th.Property("verb", th.StringType),
                                )
                            ),
                            th.Property(
                                "condition", 
                                th.ObjectType(
                                    th.Property("compareOperator", th.StringType),
                                    th.Property("compareValue", th.StringType),
                                    th.Property("contextItemId", th.StringType),
                                    th.Property("contextItemType", th.StringType),
                                    th.Property("sourceItemId", th.StringType),
                                    th.Property("sourceItemType", th.StringType),
                                )
                            ),
                        )
                    )
                ),
                th.Property(
                    "otherwiseLogicRule",
                    th.ObjectType(
                        th.Property("contextItemId", th.StringType),
                        th.Property("contextItemType", th.StringType),
                        th.Property("targetItemId", th.StringType),
                        th.Property("targetItemType", th.StringType),
                        th.Property("verb", th.StringType),
                    )
                ),
            )
        ),
    ).to_dict()
    primary_keys = ["project_id", "id"]
    replication_key = None
    records_jsonpath = "$.data.project.questions[*]"

    @property
    def query(self) -> str:
        return """
            query SurveyQuestions($project_id: ID!) {
                """  \
            + f"project(id: $project_id)" + """{
                ... on Survey {
                    questions {
                        id
                        __typename
                        ... on MatrixQuestion {
                            required
                        }
                        ... on MultipleChoiceQuestion {
                            required
                        }
                        ... on MultipleChoiceStackQuestion {
                            required
                        }
                        ... on RankingQuestion {
                            required
                        }
                        ... on RatingQuestion {
                            required
                        }
                        ... on SliderQuestion {
                            required
                        }
                        ... on TextEntryQuestion {
                            required
                        }
                        content {
                            backgroundImageUrl
                            description
                            title
                            __typename
                            ... on MatrixQuestionContent{
                                columns {
                                    id
                                    hasFollowUp
                                    followUpQuestion
                                    label
                                }
                                moreInfoText
                                rows {
                                    id
                                    title
                                    description
                                }
                            }
                            ... on MultipleChoiceContent {
                                allowMultiple
                                answers {
                                    id
                                    label
                                }
                                multipleChoiceMaxSelectionCount: maxSelectionCount
                                moreInfoText
                                showOther
                            }
                            ... on MultipleChoiceStackContent {
                                allowMultiple
                                answers {
                                    id
                                    label
                                }
                                multipleChoiceStackContentMaxSelectionCount: maxSelectionCount
                                moreInfoText
                                showOther
                                subQuestions {
                                    id
                                    title
                                    description
                                }
                            }
                            ... on RankingQuestionContent {
                                answers {
                                    id
                                    label
                                }
                                randomizeAnswers
                                showOther
                            }
                            ... on SliderQuestionContent{
                                labels {
                                    left
                                    middle
                                    right
                                }
                                showLabels
                                steps
                            }
                            ... on TextEntryQuestionContent{
                                inputs
                                placeholderText {
                                    id
                                    label
                                }
                            }
                        }
                        hidden
                        logic {
                            preLogicRules {
                                logicRuleId
                                action {
                                    contextItemId
                                    contextItemType
                                    targetItemId
                                    targetItemType
                                    verb
                                }
                                condition {
                                    compareOperator
                                    compareValue
                                    contextItemId
                                    contextItemType
                                    sourceItemId
                                    sourceItemType
                                }
                            }
                            postLogicRules {
                                logicRuleId
                                action {
                                    contextItemId
                                    contextItemType
                                    targetItemId
                                    targetItemType
                                    verb
                                }
                                condition {
                                    compareOperator
                                    compareValue
                                    contextItemId
                                    contextItemType
                                    sourceItemId
                                    sourceItemType
                                }
                            }
                            otherwiseLogicRule {
                                contextItemId
                                contextItemType
                                targetItemId
                                targetItemType
                            }
                        }
                        metadata {
                            createdBy {
                                id
                                name
                                email
                            }
                            createdUTC
                            lastModifiedUTC
                        }
                    }
                }
            }
        }
        """

