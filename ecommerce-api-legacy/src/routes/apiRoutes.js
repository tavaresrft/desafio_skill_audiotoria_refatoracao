const express = require('express');
const { createCheckoutController } = require('../controllers/checkoutController');
const { createAdminController } = require('../controllers/adminController');
const { createUserController } = require('../controllers/userController');

function createApiRouter(repository) {
  const router = express.Router();
  const checkout = createCheckoutController(repository);
  const admin = createAdminController(repository);
  const users = createUserController(repository);
  router.post('/checkout', checkout.checkout);
  router.get('/admin/financial-report', admin.financialReport);
  router.delete('/users/:id', users.deleteUser);
  return router;
}

module.exports = { createApiRouter };
