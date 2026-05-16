import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python'))

from intelligence.health import HealthScorer, HealthReport

def test_health_scorer_perfect_score():
    scorer = HealthScorer()
    report = scorer.calculate(0, 0, 0, 0)
    assert report.score == 100
    assert report.storage_pressure == 0
    assert report.cache_bloat == 0
    assert report.docker_bloat == 0
    assert report.repo_entropy == 0

def test_health_scorer_max_penalty():
    scorer = HealthScorer()
    # High pressure across the board
    report = scorer.calculate(100, 100, 100, 100)
    # Penalties sum to 100
    assert report.score == 0

def test_health_scorer_partial_penalty():
    scorer = HealthScorer()
    # 50 * 0.35 = 17.5
    # 10 * 0.20 = 2.0
    # 20 * 0.25 = 5.0
    # 5 * 0.20 = 1.0
    # Total penalties = 25.5 => 25
    # Score = 100 - 25 = 75
    report = scorer.calculate(50, 10, 20, 5)
    assert report.score == 75

def test_health_scorer_zero_floor():
    scorer = HealthScorer()
    # Massive pressure should not result in negative score
    report = scorer.calculate(1000, 1000, 1000, 1000)
    assert report.score == 0
