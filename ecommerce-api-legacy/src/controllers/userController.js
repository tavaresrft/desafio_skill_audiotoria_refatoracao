const { asyncHandler } = require('./checkoutController');

function createUserController(repository) {
  return {
    deleteUser: asyncHandler(async (req, res) => {
      const id = Number(req.params.id);
      if (!Number.isInteger(id) || id <= 0) return res.status(400).send('ID inválido');
      const deleted = await repository.deleteUser(id);
      if (!deleted) return res.status(404).send('Usuário não encontrado');
      res.send('Usuário deletado e dados relacionados removidos.');
    }),
  };
}

module.exports = { createUserController };
