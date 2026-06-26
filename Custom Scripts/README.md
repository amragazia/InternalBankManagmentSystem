# Custom Scripts

This folder contains examples for stressing the bank API with concurrent POST requests.

## Scripts
- `threading_burst.py`: launches 50 threads and synchronizes them with a barrier so they start at nearly the same moment.
- `async_burst.py`: uses `asyncio` and `aiohttp` to run 50 concurrent requests together.

## Examples
```bash
/home/peter/amr/BackEnd/InternalBankManagmentSystem/.venv/bin/pip install -r requirements.txt
/home/peter/amr/BackEnd/InternalBankManagmentSystem/.venv/bin/python "Custom Scripts/threading_burst.py" --url http://127.0.0.1:8000 --account-id 1 --action deposit --amount 10
/home/peter/amr/BackEnd/InternalBankManagmentSystem/.venv/bin/python "Custom Scripts/async_burst.py" --url http://127.0.0.1:8000 --account-id 1 --action withdraw --amount 5
```

> Use an existing account ID for the target endpoint. For withdraw requests, the account must have enough balance.