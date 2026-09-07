from marketsage_core.contracts import ENDPOINTS, build_schema, render_schema, schema_path
from marketsage_eval import api_eval


def test_committed_schema_matches_the_models():
    committed = schema_path().read_text(encoding="utf-8")

    assert committed == render_schema(build_schema()), "run `npm run contracts` and commit"


def test_every_endpoint_response_validates_against_its_schema(tmp_path):
    with api_eval.seeded_client(tmp_path) as api:
        responses = api_eval.run_tool_chain(api)

    report = api_eval.contracts_report(responses)

    assert report["failures"] == []
    assert report["validated"] == len(ENDPOINTS) == len(responses)


def test_every_envelope_carries_provenance_fields(tmp_path):
    with api_eval.seeded_client(tmp_path) as api:
        responses = api_eval.run_tool_chain(api)

    report = api_eval.envelope_report(responses)

    assert report["incomplete"] == []


def test_every_tool_call_writes_exactly_one_audit_row(tmp_path):
    with api_eval.seeded_client(tmp_path) as api:
        responses = api_eval.run_tool_chain(api)

    report = api_eval.audit_report(tmp_path, responses)

    assert report["request_ids_matched"] == report["calls"]
    assert report["orphan_rows"] == 0
    assert report["error_rows"] == 0
