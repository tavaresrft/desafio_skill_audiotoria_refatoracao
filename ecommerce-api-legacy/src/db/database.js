const sqlite3 = require('sqlite3').verbose();
const { randomBytes } = require('node:crypto');
const { hashPassword, isPasswordHash } = require('../services/passwordService');

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, pass TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id)
  )`,
  `CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    amount REAL NOT NULL, status TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, created_at DATETIME NOT NULL
  )`,
];

function openDatabase(filename) {
  const db = new sqlite3.Database(filename);
  db.run('PRAGMA foreign_keys = ON');
  return db;
}

function run(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(error) {
      if (error) return reject(error);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function get(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (error, row) => (error ? reject(error) : resolve(row)));
  });
}

function all(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (error, rows) => (error ? reject(error) : resolve(rows)));
  });
}

function close(db) {
  return new Promise((resolve, reject) => {
    db.close((error) => (error ? reject(error) : resolve()));
  });
}

async function initializeDatabase(db) {
  for (const statement of SCHEMA) await run(db, statement);

  const userCount = await get(db, 'SELECT COUNT(*) AS count FROM users');
  if (userCount.count === 0) {
    await run(db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
      'Leonan', 'leonan@fullcycle.com.br', await hashPassword(randomBytes(32).toString('base64url')),
    ]);
  }
  const courseCount = await get(db, 'SELECT COUNT(*) AS count FROM courses');
  if (courseCount.count === 0) {
    await run(db, 'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Clean Architecture', 997, 1]);
    await run(db, 'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Docker', 497, 1]);
  }
  const enrollmentCount = await get(db, 'SELECT COUNT(*) AS count FROM enrollments');
  if (enrollmentCount.count === 0) {
    await run(db, 'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
  }
  const paymentCount = await get(db, 'SELECT COUNT(*) AS count FROM payments');
  if (paymentCount.count === 0) {
    // This is explicitly fixture data; it is not a claim that a gateway was charged.
    await run(db, 'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997, 'SIMULATED']);
  }
  const logs = await get(db, 'SELECT COUNT(*) AS count FROM audit_logs');
  if (logs.count === 0) {
    await run(db, 'INSERT INTO audit_logs (action, created_at) VALUES (?, datetime(\'now\'))', ['Seed data initialized']);
  }

  // Historical PAID rows came from the old prefix-only demo, not a gateway.
  await run(db, "UPDATE payments SET status = 'SIMULATED' WHERE status = 'PAID'");

  // Upgrade credentials in an existing SQLite file without breaking the accounts.
  const users = await all(db, 'SELECT id, pass FROM users');
  for (const user of users) {
    if (!isPasswordHash(user.pass)) {
      await run(db, 'UPDATE users SET pass = ? WHERE id = ?', [await hashPassword(user.pass || ''), user.id]);
    }
  }
}

module.exports = { openDatabase, initializeDatabase, run, get, all, close };
