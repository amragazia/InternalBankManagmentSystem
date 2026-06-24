import argparse
import asyncio
from typing import Any

import aiohttp


def build_url(base_url: str, account_id: int, action: str) -> str:
    return f"{base_url.rstrip('/')}/accounts/{account_id}/{action}"


async def send_post_request(
    session: aiohttp.ClientSession,
    index: int,
    url: str,
    payload: dict[str, Any],
    timeout: int,
    barrier: asyncio.Barrier,
) -> dict[str, Any]:
    await barrier.wait()
    start = asyncio.get_running_loop().time()
    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as response:
            body = await response.text()
            elapsed_ms = (asyncio.get_running_loop().time() - start) * 1000
            return {
                "index": index,
                "status": response.status,
                "elapsed_ms": round(elapsed_ms, 2),
                "response": body,
            }
    except Exception as error:  # pragma: no cover - defensive logging
        elapsed_ms = (asyncio.get_running_loop().time() - start) * 1000
        return {
            "index": index,
            "status": "error",
            "elapsed_ms": round(elapsed_ms, 2),
            "response": str(error),
        }


async def run_burst(base_url: str, count: int, account_id: int, action: str, amount: float, timeout: int) -> None:
    url = build_url(base_url, account_id, action)
    barrier = asyncio.Barrier(count)
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(
                send_post_request(
                    session,
                    index,
                    url,
                    {"amount": amount},
                    timeout,
                    barrier,
                )
            )
            for index in range(count)
        ]
        results = await asyncio.gather(*tasks)

    success_count = sum(1 for item in results if item.get("status") == 200)
    print(f"Completed {len(results)} requests to {url}")
    print(f"Successful: {success_count} | Failed: {len(results) - success_count}")
    for item in results[:5]:
        print(item)
    if len(results) > 5:
        print("...")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send concurrent POST requests to deposit/withdraw endpoints using asyncio and aiohttp")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument("--count", type=int, default=50, help="Number of concurrent requests")
    parser.add_argument("--account-id", type=int, default=1, help="Account ID to target")
    parser.add_argument("--action", choices=["deposit", "withdraw"], default="deposit", help="Endpoint action")
    parser.add_argument("--amount", type=float, default=10.0, help="Amount to send in the request body")
    parser.add_argument("--timeout", type=int, default=10, help="Per-request timeout in seconds")
    args = parser.parse_args()
    asyncio.run(run_burst(args.url, args.count, args.account_id, args.action, args.amount, args.timeout))


if __name__ == "__main__":
    main()
