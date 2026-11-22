const path = require('node:path');

function loadConfig(env = process.env) {
  const paymentMode = env.PAYMENT_MODE || 'simulation';
  if (paymentMode !== 'simulation') {
    throw new Error('PAYMENT_MODE must be explicitly configured with a supported provider');
  }
  return {
    port: Number(env.PORT || 3000),
    host: env.HOST || '0.0.0.0',
    databasePath: env.DATABASE_PATH || ':memory:',
    paymentMode,
    baseDir: path.resolve(__dirname, '..'),
  };
}

module.exports = { loadConfig };
