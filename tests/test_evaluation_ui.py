"""Exercise the actual Streamlit form through evaluation and draft planning."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def demo():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.button[0].click().run()
    assert not app.exception
    return app


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_researcher_can_compare_select_and_generate_fictional_plan():
    app = demo()
    assert button(app, "Generate cited plan").disabled
    next(s for s in app.selectbox if s.label == "Researcher decision").select("M1")
    next(t for t in app.text_area if t.label.startswith("Why select")).set_value(
        "Illustrate a matched-condition comparison using fictional evidence.")
    button(app, "Save method evaluation").click().run()
    assert not app.exception
    app.checkbox[0].check().run()
    assert not button(app, "Generate cited plan").disabled
    button(app, "Generate cited plan").click().run()
    assert not app.exception
    run = app.session_state["frontier_result"]
    assert run.evaluation["selected_candidate_id"] == "M1"
    assert run.plan["status"] == "SYNTHETIC_TEST_ONLY"
    assert run.plan["selected_method"]["open_checks"]


def test_researcher_can_defer_with_no_comparable_methods():
    app = demo()
    app.number_input[0].set_value(0).run()
    next(t for t in app.text_area if t.label.startswith("Why select")).set_value(
        "There are no comparable methods supported by the available evidence.")
    button(app, "Save method evaluation").click().run()
    assert not app.exception
    app.checkbox[0].check().run()
    assert button(app, "Generate cited plan").disabled
    run = app.session_state["frontier_result"]
    assert run.evaluation["status"] == "DEFERRED_INSUFFICIENT_COMPARISON"
    assert run.plan is None

