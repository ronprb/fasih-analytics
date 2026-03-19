# api_client.py
import httpx

async def post_requests(url, headers, cookies, payload, timeout=10):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, cookies=cookies, json=payload)
        response.raise_for_status()
        return response

async def get_requests(url, headers, cookies, params=None, timeout=10):
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()
        return response