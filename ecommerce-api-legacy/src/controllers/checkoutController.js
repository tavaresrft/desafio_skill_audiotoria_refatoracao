const checkoutService = require('../services/checkoutService');

function asyncHandler(handler) {
  return (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);
}

function createCheckoutController(repository) {
  return {
    checkout: asyncHandler(async (req, res) => {
      const result = await checkoutService.checkout(repository, req.body);
      res.status(result.status).send(result.body);
    }),
  };
}

module.exports = { createCheckoutController, asyncHandler };
