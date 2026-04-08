# api_client.py
import httpx
import asyncio

async def post_requests(url, headers, cookies, payload, timeout=60, max_retries=5, base_delay=2):
    for attempt in range(max_retries):
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, cookies=cookies, json=payload)
            if response.status_code == 405 and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"⏳ 405 received, retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(delay)
                continue
            response.raise_for_status()
            return response

async def get_requests(url, headers, cookies, params=None, timeout=60, max_retries=5, base_delay=2):
    for attempt in range(max_retries):
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, cookies=cookies, params=params)
            if response.status_code == 405 and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"⏳ 405 received, retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(delay)
                continue
            response.raise_for_status()
            return response