"""Module docstring."""
PROFILES = {
    "developer": {
        "aggressive_cache_cleanup": False,
        "docker_cleanup": True
    },

    "blockchain": {
        "protect_chain_data": True,
        "aggressive_cache_cleanup": False,
        "docker_cleanup": True
    },

    "ai-workstation": {
        "protect_models": True,
        "analyze_embeddings": True
    }
}
