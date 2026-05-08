# api_client.py
import httpx
import asyncio
import random

# Network-level errors that are safe to retry
_RETRYABLE_ERRORS = (
    httpx.ReadError,
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
)

def _make_client(timeout: float) -> httpx.AsyncClient:
    """
    Create an AsyncClient that:
    - Forces HTTP/1.1  (server at fasih-sm.bps.go.id does not advertise HTTP/2
      via ALPN, which causes ReadError when httpx defaults to h2)
    - Uses a split timeout: short connect phase, generous read phase
    """
    t = httpx.Timeout(timeout, connect=15.0)
    return httpx.AsyncClient(http2=False, timeout=t)


async def post_requests(url, headers, cookies, payload, timeout=90, max_retries=5, base_delay=2):
    for attempt in range(max_retries):
        try:
            async with _make_client(timeout) as client:
                response = await client.post(url, headers=headers, cookies=cookies, json=payload)
                if response.status_code == 405 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⏳ 405 received, retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()
                return response
        except _RETRYABLE_ERRORS as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️  Network error ({type(e).__name__}), retrying in {delay:.1f}s "
                      f"(attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Network error after {max_retries} attempts: {e}")
                raise


async def get_requests(url, headers, cookies, params=None, timeout=90, max_retries=5, base_delay=2):
    for attempt in range(max_retries):
        try:
            async with _make_client(timeout) as client:
                response = await client.get(url, headers=headers, cookies=cookies, params=params)
                if response.status_code == 405 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⏳ 405 received, retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()
                return response
        except _RETRYABLE_ERRORS as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️  Network error ({type(e).__name__}), retrying in {delay:.1f}s "
                      f"(attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Network error after {max_retries} attempts: {e}")
                raise