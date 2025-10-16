"""
Configuration spécifique pour les tests async
Évite les imports problématiques des anciens modules
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def cleanup_sessions():
    """Cleanup aiohttp sessions after each test"""
    yield
    # Cleanup will be handled by individual test fixtures