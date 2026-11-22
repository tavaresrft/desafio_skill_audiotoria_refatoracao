const { asyncHandler } = require('./checkoutController');

function createAdminController(repository) {
  return {
    financialReport: asyncHandler(async (_req, res) => {
      res.json(await repository.getFinancialReport());
    }),
  };
}

module.exports = { createAdminController };
