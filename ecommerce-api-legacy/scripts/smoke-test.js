const assert = require('node:assert/strict');
const { createApp } = require('../src/app');

async function main() {
  const app = await createApp({ config: { databasePath: ':memory:', paymentMode: 'simulation' } });
  const server = app.listen(0, '127.0.0.1');
  await new Promise((resolve, reject) => {
    server.once('listening', resolve);
    server.once('error', reject);
  });
  const baseUrl = `http://127.0.0.1:${server.address().port}`;

  async function request(method, path, payload) {
    const response = await fetch(`${baseUrl}${path}`, {
      method,
      headers: payload ? { 'content-type': 'application/json' } : undefined,
      body: payload ? JSON.stringify(payload) : undefined,
    });
    return { status: response.status, body: await response.text(), headers: response.headers };
  }

  try {
    const approved = await request('POST', '/api/checkout', {
      usr: 'Guilherme', eml: 'gui@fullcycle.com.br', pwd: 'senha-demo-forte',
      c_id: 2, card: '4111222233334444',
    });
    assert.equal(approved.status, 200);
    const checkoutBody = JSON.parse(approved.body);
    assert.equal(checkoutBody.msg, 'Sucesso');
    assert.ok(Number.isInteger(checkoutBody.enrollment_id));

    const declined = await request('POST', '/api/checkout', {
      usr: 'João', eml: 'joao@teste.com', pwd: 'senha-demo-forte',
      c_id: 1, card: '5111222233334444',
    });
    assert.equal(declined.status, 400);
    assert.equal(declined.body, 'Pagamento recusado');

    const arbitraryVisa = await request('POST', '/api/checkout', {
      usr: 'Outra pessoa', eml: 'outra@example.test', pwd: 'senha-demo-forte',
      c_id: 1, card: '4111111111111111',
    });
    assert.equal(arbitraryVisa.status, 400);
    assert.equal(await app.locals.repository.findUserByEmail('outra@example.test'), undefined);

    const invalid = await request('POST', '/api/checkout', {
      usr: 'Sem senha', eml: 'sem-senha@example.test', c_id: 1, card: '4111222233334444',
    });
    assert.equal(invalid.status, 400);

    const report = await request('GET', '/api/admin/financial-report');
    assert.equal(report.status, 200);
    const reportBody = JSON.parse(report.body);
    assert.equal(reportBody.length, 2);
    assert.equal(reportBody[0].revenue, 0);

    const user = await app.locals.repository.findUserByEmail('gui@fullcycle.com.br');
    assert.match(user.pass, /^scrypt\$/);
    const deleted = await request('DELETE', `/api/users/${user.id}`);
    assert.equal(deleted.status, 200);
    assert.equal(deleted.body, 'Usuário deletado e dados relacionados removidos.');
    assert.equal(await app.locals.repository.findUserByEmail('gui@fullcycle.com.br'), undefined);

    const missing = await request('DELETE', '/api/users/999999');
    assert.equal(missing.status, 404);

    console.log('smoke=PASS; checkout=approved/declined/invalid; financial-report=PASS; delete-user=cascade/404; password=scrypt');
  } finally {
    await new Promise((resolve) => server.close(resolve));
    await app.locals.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
