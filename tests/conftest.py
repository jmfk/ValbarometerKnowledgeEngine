import pytest
import os

# vibe-tools non-intrusive testing policy is enforced automatically via the pytest plugin.
# The following environment variables are set by default:
# VIBE_TEST_MODE=1
# VIBE_AGENT_ACTIVE=1

@pytest.fixture(autouse=True)
def setup_vibe_test_env(monkeypatch):
    # Local project specific test setup
    pass
