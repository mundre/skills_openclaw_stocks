#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ALLOWED_STATUSES = {"draft", "enabled", "paused", "archived"}
REPORT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ALLOWED_DELIVERY_CHANNELS = {"email", "conversation", "thread", "webhook", "folder"}
ALLOWED_TRIGGER_TYPES = {"hourly", "daily", "weekly", "monthly"}
ALLOWED_WEEK_DAYS = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
DATA_DEFINITION_SIGNAL_KEYS = {
    "datasetRef",
    "jobRef",
    "pipelineRef",
    "query",
    "queryFile",
    "sourceRef",
    "storedProcedure",
}
RENDERING_DEFINITION_SIGNAL_KEYS = {
    "chart",
    "charts",
    "layout",
    "rendererConfig",
    "sections",
    "sheets",
    "template",
    "workbook",
}
KNOWN_BACKEND_SKILLS = {
    "mssql": {"mssql"},
}
KNOWN_DELIVERY_SKILLS = {
    "email": {"imap-smtp-mail"},
}
KNOWN_OUTPUT_RENDERERS = {
    "pdf": {"pdf-report"},
    "excel": {"excel-export"},
    "xlsx": {"excel-export"},
    "image": {"chart-mpl"},
    "png": {"chart-mpl"},
    "svg": {"chart-mpl"},
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_required_string(
    obj: dict[str, object],
    key: str,
    errors: list[str],
    path: str,
) -> str | None:
    value = obj.get(key)
    if not is_non_empty_string(value):
        add_error(errors, f"{path}.{key} must be a non-empty string")
        return None
    return value.strip()


def validate_required_object(
    obj: dict[str, object],
    key: str,
    errors: list[str],
    path: str,
) -> dict[str, object] | None:
    value = obj.get(key)
    if not isinstance(value, dict):
        add_error(errors, f"{path}.{key} must be an object")
        return None
    return value


def validate_non_empty_object(
    obj: dict[str, object],
    key: str,
    errors: list[str],
    path: str,
) -> dict[str, object] | None:
    value = validate_required_object(obj, key, errors, path)
    if value is not None and not value:
        add_error(errors, f"{path}.{key} must be a non-empty object")
        return None
    return value


def infer_skill_from_backend(backend: str | None) -> str | None:
    mapping = {
        "mssql": "mssql",
    }
    if not backend:
        return None
    return mapping.get(backend.strip().lower())


def infer_skill_from_rendering(kind: str | None, output_type: str | None) -> str | None:
    kind_mapping = {
        "pdf-report": "pdf-report",
        "excel-export": "excel-export",
        "chart-mpl": "chart-mpl",
    }
    output_mapping = {
        "pdf": "pdf-report",
        "excel": "excel-export",
        "xlsx": "excel-export",
        "image": "chart-mpl",
        "png": "chart-mpl",
        "svg": "chart-mpl",
    }
    if kind and kind.strip().lower() in kind_mapping:
        return kind_mapping[kind.strip().lower()]
    if output_type:
        return output_mapping.get(output_type.strip().lower())
    return None


def infer_skill_from_delivery(channel: str | None) -> str | None:
    mapping = {
        "email": "imap-smtp-mail",
    }
    if not channel:
        return None
    return mapping.get(channel.strip().lower())


def collect_list_of_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result


def is_int_like(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_time_string(value: object, path: str, errors: list[str]) -> str | None:
    if not is_non_empty_string(value):
        add_error(errors, f"{path} must be a non-empty string in HH:MM format")
        return None
    normalized = str(value).strip()
    if not TIME_RE.match(normalized):
        add_error(errors, f"{path} must use HH:MM 24-hour format")
        return None
    return normalized


def validate_timezone_name(value: object, path: str, errors: list[str]) -> str | None:
    if not is_non_empty_string(value):
        add_error(errors, f"{path} must be a non-empty IANA timezone name")
        return None
    normalized = str(value).strip()
    try:
        ZoneInfo(normalized)
    except ZoneInfoNotFoundError:
        add_error(errors, f"{path} must be a valid IANA timezone name")
        return None
    return normalized


def validate_non_empty_day_list(value: object, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        add_error(errors, f"{path} must be a non-empty list of weekday codes")
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not is_non_empty_string(item):
            add_error(errors, f"{path}[{index}] must be a non-empty weekday code")
            continue
        day = str(item).strip().upper()
        if day not in ALLOWED_WEEK_DAYS:
            add_error(
                errors,
                f"{path}[{index}] must be one of: {', '.join(sorted(ALLOWED_WEEK_DAYS))}",
            )
            continue
        if day in seen:
            add_error(errors, f"{path}[{index}] duplicates weekday {day}")
            continue
        seen.add(day)
        normalized.append(day)
    return normalized


def validate_trigger(trigger: dict[str, object], errors: list[str]) -> None:
    trigger_type = validate_required_string(
        trigger, "type", errors, "definition.schedule.trigger"
    )
    if trigger_type is None:
        return

    normalized_type = trigger_type.lower()
    if normalized_type not in ALLOWED_TRIGGER_TYPES:
        add_error(
            errors,
            "definition.schedule.trigger.type must be one of: "
            + ", ".join(sorted(ALLOWED_TRIGGER_TYPES)),
        )
        return

    if normalized_type == "hourly":
        interval_hours = trigger.get("intervalHours", 1)
        if not is_int_like(interval_hours) or int(interval_hours) < 1:
            add_error(
                errors,
                "definition.schedule.trigger.intervalHours must be an integer >= 1 for hourly schedules",
            )
        minute = trigger.get("minute")
        if minute is not None and (not is_int_like(minute) or int(minute) < 0 or int(minute) > 59):
            add_error(
                errors,
                "definition.schedule.trigger.minute must be an integer between 0 and 59 for hourly schedules",
            )
        return

    if normalized_type == "daily":
        validate_time_string(
            trigger.get("time"),
            "definition.schedule.trigger.time",
            errors,
        )
        return

    if normalized_type == "weekly":
        validate_non_empty_day_list(
            trigger.get("days"),
            "definition.schedule.trigger.days",
            errors,
        )
        validate_time_string(
            trigger.get("time"),
            "definition.schedule.trigger.time",
            errors,
        )
        return

    if normalized_type == "monthly":
        day_of_month = trigger.get("dayOfMonth")
        if not is_int_like(day_of_month) or int(day_of_month) < 1 or int(day_of_month) > 31:
            add_error(
                errors,
                "definition.schedule.trigger.dayOfMonth must be an integer between 1 and 31 for monthly schedules",
            )
        validate_time_string(
            trigger.get("time"),
            "definition.schedule.trigger.time",
            errors,
        )
        return

def validate_data_definition(value: object, errors: list[str]) -> dict[str, object] | None:
    if not isinstance(value, dict):
        add_error(errors, "definition.data.definition must be an object")
        return None
    if not value:
        add_error(errors, "definition.data.definition must be a non-empty object")
        return None

    actionable = False
    for key in DATA_DEFINITION_SIGNAL_KEYS:
        candidate = value.get(key)
        if is_non_empty_string(candidate):
            actionable = True
            break

    if not actionable:
        add_error(
            errors,
            "definition.data.definition must contain at least one deterministic data key with a non-empty value: "
            + ", ".join(sorted(DATA_DEFINITION_SIGNAL_KEYS)),
        )
        return None
    return value


def validate_rendering_definition(value: object, errors: list[str]) -> dict[str, object] | None:
    if not isinstance(value, dict):
        add_error(errors, "definition.rendering.definition must be an object")
        return None
    if not value:
        add_error(errors, "definition.rendering.definition must be a non-empty object")
        return None

    checks = (
        is_non_empty_string(value.get("template")),
        isinstance(value.get("sections"), list) and bool(value.get("sections")),
        isinstance(value.get("sheets"), list) and bool(value.get("sheets")),
        isinstance(value.get("charts"), list) and bool(value.get("charts")),
        isinstance(value.get("workbook"), dict) and bool(value.get("workbook")),
        isinstance(value.get("chart"), dict) and bool(value.get("chart")),
        isinstance(value.get("layout"), dict) and bool(value.get("layout")),
        isinstance(value.get("rendererConfig"), dict) and bool(value.get("rendererConfig")),
    )
    if not any(checks):
        add_error(
            errors,
            "definition.rendering.definition must contain deterministic rendering keys with non-empty values: "
            + ", ".join(sorted(RENDERING_DEFINITION_SIGNAL_KEYS)),
        )
        return None
    return value


def validate_delivery_target(
    target: dict[str, object],
    channel: str,
    errors: list[str],
) -> None:
    if channel == "email":
        to_list = collect_list_of_strings(target.get("to"))
        contact = target.get("contact")
        if not to_list and not is_non_empty_string(contact):
            add_error(
                errors,
                "definition.delivery.target must contain to[] or contact for email delivery",
            )
        return

    if channel in {"conversation", "thread"}:
        if not (
            is_non_empty_string(target.get("conversationId"))
            or is_non_empty_string(target.get("threadId"))
        ):
            add_error(
                errors,
                "definition.delivery.target must contain conversationId or threadId for conversation delivery",
            )
        return

    if channel == "webhook":
        if not (
            is_non_empty_string(target.get("endpointAlias"))
            or is_non_empty_string(target.get("url"))
        ):
            add_error(
                errors,
                "definition.delivery.target must contain endpointAlias or url for webhook delivery",
            )
        return

    if channel == "folder":
        if not is_non_empty_string(target.get("path")):
            add_error(
                errors,
                "definition.delivery.target must contain path for folder delivery",
            )
        return


def validate_definition(payload: object, input_path: Path) -> tuple[bool, dict[str, object]]:
    errors: list[str] = []
    inferred_skills: set[str] = set()

    if not isinstance(payload, dict):
        return False, {
            "valid": False,
            "input": str(input_path),
            "errors": ["Top-level JSON value must be an object"],
        }

    report_id = validate_required_string(payload, "reportId", errors, "definition")
    if report_id and not REPORT_ID_RE.match(report_id):
        add_error(
            errors,
            "definition.reportId must contain only lowercase letters, digits, hyphens, or underscores",
        )

    name = validate_required_string(payload, "name", errors, "definition")
    purpose = validate_required_string(payload, "purpose", errors, "definition")

    owner = validate_required_object(payload, "owner", errors, "definition")
    if owner is not None:
        owner_id = owner.get("id")
        owner_name = owner.get("displayName")
        if not is_non_empty_string(owner_id) and not is_non_empty_string(owner_name):
            add_error(errors, "definition.owner must contain id or displayName")

    status = validate_required_string(payload, "status", errors, "definition")
    if status and status not in ALLOWED_STATUSES:
        add_error(
            errors,
            f"definition.status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}",
        )

    schedule = validate_required_object(payload, "schedule", errors, "definition")
    schedule_summary = None
    if schedule is not None:
        validate_timezone_name(schedule.get("timezone"), "definition.schedule.timezone", errors)
        schedule_summary = validate_required_string(schedule, "summary", errors, "definition.schedule")
        trigger = validate_non_empty_object(schedule, "trigger", errors, "definition.schedule")
        if trigger is not None:
            validate_trigger(trigger, errors)

    delivery = validate_required_object(payload, "delivery", errors, "definition")
    delivery_channel = None
    delivery_skill_name = None
    if delivery is not None:
        delivery_channel = validate_required_string(
            delivery, "channel", errors, "definition.delivery"
        )
        target = validate_required_object(delivery, "target", errors, "definition.delivery")
        if target is not None and delivery_channel:
            normalized_channel = delivery_channel.lower()
            if normalized_channel not in ALLOWED_DELIVERY_CHANNELS:
                add_error(
                    errors,
                    "definition.delivery.channel must be one of: "
                    + ", ".join(sorted(ALLOWED_DELIVERY_CHANNELS)),
                )
            else:
                validate_delivery_target(target, normalized_channel, errors)

        delivery_skill = delivery.get("executionSkill")
        if is_non_empty_string(delivery_skill):
            delivery_skill_name = str(delivery_skill).strip()
            inferred_skills.add(delivery_skill_name)
        else:
            delivery_skill_name = infer_skill_from_delivery(delivery_channel)
            if delivery_skill_name:
                inferred_skills.add(delivery_skill_name)

        if delivery_channel:
            allowed_delivery_skills = KNOWN_DELIVERY_SKILLS.get(delivery_channel.lower())
            if (
                allowed_delivery_skills
                and delivery_skill_name
                and delivery_skill_name.lower() not in allowed_delivery_skills
            ):
                add_error(
                    errors,
                    "definition.delivery.executionSkill must be compatible with definition.delivery.channel",
                )

    output = validate_required_object(payload, "output", errors, "definition")
    output_type = None
    if output is not None:
        output_type = validate_required_string(output, "type", errors, "definition.output")

    data = validate_required_object(payload, "data", errors, "definition")
    backend = None
    data_skill_name = None
    if data is not None:
        backend = validate_required_string(data, "backend", errors, "definition.data")
        validate_data_definition(data.get("definition"), errors)

        data_skill = data.get("executionSkill")
        if is_non_empty_string(data_skill):
            data_skill_name = str(data_skill).strip()
            inferred_skills.add(data_skill_name)
        else:
            data_skill_name = infer_skill_from_backend(backend)
            if data_skill_name:
                inferred_skills.add(data_skill_name)

        if backend:
            allowed_backend_skills = KNOWN_BACKEND_SKILLS.get(backend.lower())
            if allowed_backend_skills and data_skill_name and data_skill_name not in allowed_backend_skills:
                add_error(
                    errors,
                    "definition.data.executionSkill must be compatible with definition.data.backend",
                )

    rendering = validate_required_object(payload, "rendering", errors, "definition")
    rendering_kind = None
    rendering_skill_name = None
    if rendering is not None:
        rendering_kind = validate_required_string(
            rendering, "kind", errors, "definition.rendering"
        )
        validate_rendering_definition(rendering.get("definition"), errors)

        rendering_skill = rendering.get("executionSkill")
        if is_non_empty_string(rendering_skill):
            rendering_skill_name = str(rendering_skill).strip()
            inferred_skills.add(rendering_skill_name)
        else:
            rendering_skill_name = infer_skill_from_rendering(rendering_kind, output_type)
            if rendering_skill_name:
                inferred_skills.add(rendering_skill_name)

    normalized_output_type = output_type.lower() if output_type else None
    normalized_rendering_kind = rendering_kind.lower() if rendering_kind else None
    if normalized_output_type:
        allowed_renderers = KNOWN_OUTPUT_RENDERERS.get(normalized_output_type)
        if allowed_renderers:
            if normalized_rendering_kind and normalized_rendering_kind not in allowed_renderers:
                add_error(
                    errors,
                    "definition.rendering.kind must be compatible with definition.output.type",
                )
            if rendering_skill_name and rendering_skill_name.lower() not in allowed_renderers:
                add_error(
                    errors,
                    "definition.rendering.executionSkill must be compatible with definition.output.type",
                )

    post_processing = payload.get("postProcessing")
    if isinstance(post_processing, dict):
        charts = post_processing.get("charts")
        if isinstance(charts, list):
            for index, chart in enumerate(charts):
                if not isinstance(chart, dict):
                    add_error(
                        errors,
                        f"definition.postProcessing.charts[{index}] must be an object",
                    )
                    continue
                chart_skill = chart.get("executionSkill")
                if is_non_empty_string(chart_skill):
                    inferred_skills.add(str(chart_skill).strip())
                else:
                    inferred_skills.add("chart-mpl")
                if not is_non_empty_string(chart.get("kind")):
                    add_error(
                        errors,
                        f"definition.postProcessing.charts[{index}].kind must be a non-empty string",
                    )

    result = {
        "valid": not errors,
        "input": str(input_path),
        "reportId": report_id,
        "name": name,
        "purpose": purpose,
        "status": status,
        "scheduleSummary": schedule_summary,
        "deliveryChannel": delivery_channel,
        "outputType": output_type,
        "requiredSkills": sorted(inferred_skills),
        "errors": errors,
    }
    return not errors, result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a saved scheduled-report definition."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the JSON report definition to validate",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    payload = load_json(input_path)
    valid, result = validate_definition(payload, input_path)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
