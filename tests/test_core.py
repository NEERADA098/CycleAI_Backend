import pytest
from app.services.safety_filter import safety_filter
from app.services.prediction_service import prediction_service

def test_safety_filter_flags_heavy_bleeding():
    result = safety_filter.check("I have been bleeding for more than 10 days")
    assert result.is_safe == False
    assert result.flag_matched == "heavy_bleeding_duration"

def test_safety_filter_passes_normal_question():
    result = safety_filter.check("What is a normal cycle length?")
    assert result.is_safe == True
    assert result.requires_urgent_care == False

def test_safety_filter_flags_severe_pain():
    result = safety_filter.check("I have unbearable pain right now")
    assert result.is_safe == False

def test_prediction_returns_valid_range():
    result = prediction_service.predict_next_cycle([28, 27, 29, 28, 30])
    assert 21 <= result["predicted_days"] <= 45

def test_prediction_handles_empty_history():
    result = prediction_service.predict_next_cycle([])
    assert result["predicted_days"] == 28
    assert result["method"] == "default"
