import argparse
import json
import threading
import time
import urllib.error
import urllib.request
from typing import Any


def build_url(base_url: str, account_id: int, action: str) -> str:
    return f"{base_url.rstrip('/')}/accounts/{account_id}/{action}"


def send_post_request(index: int, url: str, payload: dict[str, Any], timeout: int = 10) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {
                "index": index,
                "status": response.status,
                "elapsed_ms": round(elapsed_ms, 2),
                "response": response_body,
            }
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "index": index,
            "status": error.code,
            "elapsed_ms": round(elapsed_ms, 2),
            "response": response_body,
        }
    except Exception as error:  # pragma: no cover - defensive logging
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "index": index,
            "status": "error",
            "elapsed_ms": round(elapsed_ms, 2),
            "response": str(error),
        }


def run_burst(base_url: str, count: int, account_id: int, action: str, amount: float, timeout: int = 10) -> None:
    url = build_url(base_url, account_id, action)
    start_barrier = threading.Barrier(count)
    results: list[dict[str, Any]] = []
    lock = threading.Lock()

    def worker(index: int) -> None:
        start_barrier.wait(timeout=5)
        payload = {"amount": amount}
        result = send_post_request(index=index, url=url, payload=payload, timeout=timeout)
        with lock:
            results.append(result)

    threads = [threading.Thread(target=worker, args=(index,), daemon=True) for index in range(count)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    success_count = sum(1 for item in results if item.get("status") == 200)
    print(f"Completed {len(results)} requests to {url}")
    print(f"Successful: {success_count} | Failed: {len(results) - success_count}")
    for item in results[:5]:
        print(item)
    if len(results) > 5:
        print("...")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send concurrent POST requests to deposit/withdraw endpoints using Python threading")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument("--count", type=int, default=50, help="Number of concurrent requests")
    parser.add_argument("--account-id", type=int, default=1, help="Account ID to target")
    parser.add_argument("--action", choices=["deposit", "withdraw"], default="deposit", help="Endpoint action")
    parser.add_argument("--amount", type=float, default=10.0, help="Amount to send in the request body")
    parser.add_argument("--timeout", type=int, default=10, help="Per-request timeout in seconds")
    args = parser.parse_args()
    run_burst(args.url, args.count, args.account_id, args.action, args.amount, args.timeout)


if __name__ == "__main__":
    main()
