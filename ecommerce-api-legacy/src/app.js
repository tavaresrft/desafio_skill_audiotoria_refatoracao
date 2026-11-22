const express = require('express');
const { loadConfig } = require('./config');
const { openDatabase, initializeDatabase, close } = require('./db/database');
const { LmsRepository } = require('./repositories/lmsRepository');
const { createApiRouter } = require('./routes/apiRoutes');
const { errorHandler } = require('./middleware/errorHandler');

async function createApp(options = {}) {
  const config = options.config || loadConfig(options.env);
  const db = options.db || openDatabase(config.databasePath);
  await initializeDatabase(db);

  const app = express();
  const repository = new LmsRepository(db);
  app.use(express.json({ limit: '32kb' }));
  app.use('/api', createApiRouter(repository));
  app.use((_req, res) => res.status(404).send('Not Found'));
  app.use(errorHandler);

  app.locals.close = () => close(db);
  app.locals.repository = repository;
  return app;
}

async function startServer() {
  const config = loadConfig();
  const app = await createApp({ config });
  const server = app.listen(config.port, config.host, () => {
    console.log(`LMS API listening on ${config.host}:${config.port} (${config.paymentMode} payment mode)`);
  });
  const shutdown = async () => {
    server.close(async () => {
      await app.locals.close();
      process.exit(0);
    });
  };
  process.once('SIGINT', shutdown);
  process.once('SIGTERM', shutdown);
  return server;
}

if (require.main === module) {
  startServer().catch((error) => {
    console.error('Application startup failed:', error.message);
    process.exitCode = 1;
  });
}

module.exports = { createApp, startServer };
