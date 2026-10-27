"""No network credentials or scientific datasets are required for these tests."""
import pytest
from frontierlab.quantitative import inverse_variance_heterogeneity

def test_synthetic_heterogeneity_matches_wolfram():
    r = inverse_variance_heterogeneity([0.4, -0.3], [0.15, 0.1])
    assert r["pooled_effect"] == pytest.approx(-0.08461538461538458)
    assert r["Q"] == pytest.approx(15.076923076923077)
    assert r["I2"] == pytest.approx(0.9336734693877552)
    assert r["degrees_of_freedom"] == 1

def test_agreement_has_zero_heterogeneity():
    r = inverse_variance_heterogeneity([0.2, 0.2], [0.1, 0.1])
    assert r["Q"] == pytest.approx(0)
    assert r["I2"] == pytest.approx(0)

@pytest.mark.parametrize("effects,ses", [
    ([1], [0.1]), ([0.1, 0.2], [0.1]), ([0.1, 0.2], [0, 0.1]),
    ([0.1, float("nan")], [0.1, 0.2]), ([0.1, 0.2], [float("inf"), 0.1]),
])
def test_malformed_heterogeneity_inputs_rejected(effects, ses):
    with pytest.raises(ValueError):
        inverse_variance_heterogeneity(effects, ses)
