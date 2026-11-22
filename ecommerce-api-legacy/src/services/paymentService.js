// Explicit demo-only adapter. It never calls a gateway and never records a real payment.
const APPROVED_TEST_CARD = '4111222233334444';
const DECLINED_TEST_CARD = '5111222233334444';

function authorizeSimulation(card) {
  if (card === APPROVED_TEST_CARD) return { approved: true, status: 'SIMULATED' };
  if (card === DECLINED_TEST_CARD) return { approved: false, status: 'DENIED' };
  return { approved: false, status: 'DENIED' };
}

module.exports = { authorizeSimulation };
