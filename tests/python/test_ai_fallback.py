import os
import pytest
from unittest.mock import patch, MagicMock
from ai.providers.factory import ProviderFactory
from ai.providers.fallback_ai import FallbackAIProvider
from ai.advisory import AdvisoryEngine

def test_fallback_provider_generation():
    provider = FallbackAIProvider()
    
    # Test Storage analysis
    res_storage = provider.generate_recommendation("Queue Tasks:\n- Module 'apt' claims it can reclaim 50.0 MB\nTotal estimated savings: 50.0 MB.")
    assert "response" in res_storage
    assert "Reclaimable Storage Analysis" in res_storage["response"]
    assert "50.0 MB" in res_storage["response"]
    
    # Test Docker analysis
    res_docker = provider.generate_recommendation("Docker State:\nImages:\nubuntu:latest (100MB)\nContainers:\ntest-container - Exited\nVolumes:\n")
    assert "response" in res_docker
    assert "Docker Optimization Analysis" in res_docker["response"]
    assert "Prune Stopped Containers" in res_docker["response"]

    # Test APT analysis
    res_apt = provider.generate_recommendation("Apt State:\nManually installed packages summary:\ncurl\nAutoremove simulation:\nRemv python3-dev [3.11.2]\n")
    assert "response" in res_apt
    assert "APT Package Management Analysis" in res_apt["response"]
    assert "Run Autoremove" in res_apt["response"]

@patch('ai.providers.ollama.OllamaProvider.generate_recommendation')
def test_factory_fallback_on_error(mock_generate):
    # Mock Ollama returning a ConnectionError
    mock_generate.return_value = {"error": "ConnectionError", "recommendation": "None"}
    
    with patch.dict(os.environ, {"SYSCLEAN_AI_PROVIDER": "ollama"}):
        provider = ProviderFactory.get_provider()
        res = provider.generate_recommendation("Docker State:\n")
        
        assert "response" in res
        assert "Heuristics" in res["response"] or "Docker Optimization Analysis" in res["response"]

def test_factory_fallback_on_exception():
    # If the provider raises an exception
    mock_provider = MagicMock()
    mock_provider.generate_recommendation.side_effect = Exception("Service unavailable")
    
    from ai.providers.factory import SafeFallbackWrapperProvider
    wrapper = SafeFallbackWrapperProvider(mock_provider)
    res = wrapper.generate_recommendation("Docker State:\n")
    
    assert "response" in res
    assert "Docker Optimization Analysis" in res["response"]
