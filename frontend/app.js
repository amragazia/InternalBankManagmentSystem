const API_BASE = '/api';

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

function setResult(elementId, message, isError = false) {
  const element = document.getElementById(elementId);
  element.textContent = message;
  element.style.color = isError ? '#fda4af' : '#bfdbfe';
}

function resetForm(event) {
  const form = event.currentTarget || event.target;
  if (form && typeof form.reset === 'function') {
    form.reset();
  }
}

async function loadAccounts() {
  const container = document.getElementById('accounts-list');
  try {
    const data = await requestJson('/accounts');
    const accounts = data.accounts || [];
    if (!accounts.length) {
      container.innerHTML = '<div class="card">No accounts yet.</div>';
      return;
    }

    container.innerHTML = accounts.map((account) => `
      <div class="card">
        <strong>#${account.account_number}</strong> — ${account.holder}<br />
        Balance: ${account.balance}
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = `<div class="card">${error.message}</div>`;
  }
}

async function loadTransactions() {
  const container = document.getElementById('transactions-list');
  try {
    const data = await requestJson('/transactions');
    const transactions = data.transactions || [];
    if (!transactions.length) {
      container.innerHTML = '<div class="card">No transactions yet.</div>';
      return;
    }

    container.innerHTML = transactions.map((transaction) => `
      <div class="card">
        <strong>${transaction.type}</strong><br />
        Amount: ${transaction.amount}<br />
        Source: ${transaction.source ?? '—'}
        Destination: ${transaction.destination ?? '—'}<br />
        Timestamp: ${transaction.timestamp}
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = `<div class="card">${error.message}</div>`;
  }
}

document.getElementById('create-account-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  try {
    const payload = { name: formData.get('name'), balance: Number(formData.get('balance')) };
    const result = await requestJson('/accounts', { method: 'POST', body: JSON.stringify(payload) });
    setResult('create-account-result', `Created account #${result.account_number}`);
    resetForm(event);
    await loadAccounts();
    await loadTransactions();
  } catch (error) {
    setResult('create-account-result', error.message, true);
  }
});

document.getElementById('deposit-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const accountId = formData.get('accountId');
  const amount = formData.get('amount');
  try {
    const result = await requestJson(`/accounts/${accountId}/deposit`, {
      method: 'POST',
      body: JSON.stringify({ amount: Number(amount) })
    });
    setResult('deposit-result', result.Message || `Deposit successful. New balance: ${result.new_balance}`);
    resetForm(event);
    await loadAccounts();
    await loadTransactions();
  } catch (error) {
    setResult('deposit-result', error.message, true);
  }
});

document.getElementById('withdraw-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const accountId = formData.get('accountId');
  const amount = formData.get('amount');
  try {
    const result = await requestJson(`/accounts/${accountId}/withdraw`, {
      method: 'POST',
      body: JSON.stringify({ amount: Number(amount) })
    });
    setResult('withdraw-result', result.Message || `Withdrawal successful. New balance: ${result.new_balance}`);
    resetForm(event);
    await loadAccounts();
    await loadTransactions();
  } catch (error) {
    setResult('withdraw-result', error.message, true);
  }
});

document.getElementById('transfer-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  try {
    const result = await requestJson(`/accounts/${formData.get('fromAccount')}/transfer`, {
      method: 'POST',
      body: JSON.stringify({ dest: Number(formData.get('toAccount')), amount: Number(formData.get('amount')) })
    });
    setResult('transfer-result', `Transfer successful. New balance: ${result.new_balance}`);
    resetForm(event);
    await loadAccounts();
    await loadTransactions();
  } catch (error) {
    setResult('transfer-result', error.message, true);
  }
});

document.getElementById('refresh-accounts').addEventListener('click', async () => {
  await loadAccounts();
  await loadTransactions();
});

window.addEventListener('load', async () => {
  await loadAccounts();
  await loadTransactions();
});
