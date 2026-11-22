const { randomBytes, scrypt: scryptCallback, timingSafeEqual } = require('node:crypto');
const { promisify } = require('node:util');

const scrypt = promisify(scryptCallback);
const KEY_LENGTH = 64;

async function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const derivedKey = await scrypt(String(password), salt, KEY_LENGTH);
  return `scrypt$${salt}$${derivedKey.toString('hex')}`;
}

function isPasswordHash(value) {
  return typeof value === 'string' && value.startsWith('scrypt$');
}

async function verifyPassword(password, encoded) {
  if (!isPasswordHash(encoded)) return false;
  const [, salt, expectedHex] = encoded.split('$');
  if (!salt || !expectedHex || !/^[a-f0-9]{128}$/i.test(expectedHex)) return false;
  const actual = await scrypt(String(password), salt, KEY_LENGTH);
  return timingSafeEqual(actual, Buffer.from(expectedHex, 'hex'));
}

module.exports = { hashPassword, isPasswordHash, verifyPassword };
