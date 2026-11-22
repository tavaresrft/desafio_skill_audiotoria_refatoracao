const { hashPassword, verifyPassword } = require('./passwordService');
const { authorizeSimulation } = require('./paymentService');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function badRequest(message = 'Bad Request') {
  return { status: 400, body: message };
}

async function checkout(repository, body = {}) {
  const { usr, eml, pwd, c_id: courseId, card } = body;
  if (![usr, eml, pwd, courseId, card].every((value) => value !== undefined && value !== null && value !== '')) {
    return badRequest();
  }
  if (typeof usr !== 'string' || usr.trim().length < 2 || usr.length > 200) return badRequest('Dados inválidos');
  if (typeof eml !== 'string' || eml.length > 254 || !EMAIL_PATTERN.test(eml)) return badRequest('Dados inválidos');
  if (typeof pwd !== 'string' || pwd.length === 0 || pwd.length > 256) return badRequest('Senha inválida');
  if (!Number.isInteger(Number(courseId)) || Number(courseId) <= 0) return badRequest('Dados inválidos');
  if (typeof card !== 'string' || !CARD_PATTERN.test(card)) return badRequest('Dados inválidos');

  const course = await repository.findActiveCourse(Number(courseId));
  if (!course) return { status: 404, body: 'Curso não encontrado' };

  const user = await repository.findUserByEmail(eml);
  if (user) {
    if (!(await verifyPassword(pwd, user.pass))) return { status: 401, body: 'Credenciais inválidas' };
  } else if (pwd.length < 8) {
    return badRequest('Senha deve ter ao menos 8 caracteres');
  }

  const payment = authorizeSimulation(card);
  if (!payment.approved) return { status: 400, body: 'Pagamento recusado' };

  const newUser = user ? null : { name: usr.trim(), email: eml, passwordHash: await hashPassword(pwd) };
  const enrollmentId = await repository.createCheckout({ user, newUser, course, paymentStatus: payment.status });
  return { status: 200, body: { msg: 'Sucesso', enrollment_id: enrollmentId } };
}

module.exports = { checkout };
