import asyncio

import pytest


@pytest.mark.asyncio
async def test_connection(server):
    loop = server
    await asyncio.sleep(30)
