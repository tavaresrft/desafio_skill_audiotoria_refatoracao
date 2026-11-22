const { run, get, all } = require('../db/database');

class LmsRepository {
  constructor(db) {
    this.db = db;
  }

  findActiveCourse(id) {
    return get(this.db, 'SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
  }

  findUserByEmail(email) {
    return get(this.db, 'SELECT id, name, email, pass FROM users WHERE email = ? ORDER BY id LIMIT 1', [email]);
  }

  async createCheckout({ user, newUser, course, paymentStatus }) {
    await run(this.db, 'BEGIN TRANSACTION');
    try {
      let userId = user?.id;
      if (!userId) {
        const inserted = await run(
          this.db,
          'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
          [newUser.name, newUser.email, newUser.passwordHash],
        );
        userId = inserted.lastID;
      }
      const enrollment = await run(
        this.db,
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, course.id],
      );
      await run(
        this.db,
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollment.lastID, course.price, paymentStatus],
      );
      await run(
        this.db,
        'INSERT INTO audit_logs (action, created_at) VALUES (?, datetime(\'now\'))',
        [`Checkout simulation for course ${course.id}`],
      );
      await run(this.db, 'COMMIT');
      return enrollment.lastID;
    } catch (error) {
      await run(this.db, 'ROLLBACK');
      throw error;
    }
  }

  async getFinancialReport() {
    const rows = await all(
      this.db,
      `SELECT c.id AS course_id, c.title AS course, e.id AS enrollment_id,
              u.name AS student, p.amount AS amount, p.status AS payment_status
       FROM courses AS c
       LEFT JOIN enrollments AS e ON e.course_id = c.id
       LEFT JOIN users AS u ON u.id = e.user_id
       LEFT JOIN payments AS p ON p.enrollment_id = e.id
       ORDER BY c.id, e.id`,
    );
    const courses = new Map();
    for (const row of rows) {
      if (!courses.has(row.course_id)) {
        courses.set(row.course_id, { course: row.course, revenue: 0, students: [] });
      }
      if (row.enrollment_id !== null) {
        const course = courses.get(row.course_id);
        const paid = row.payment_status === 'PAID' ? row.amount : 0;
        course.revenue += paid || 0;
        course.students.push({ student: row.student || 'Unknown', paid });
      }
    }
    return [...courses.values()];
  }

  async deleteUser(id) {
    await run(this.db, 'BEGIN TRANSACTION');
    try {
      const enrollments = await all(this.db, 'SELECT id FROM enrollments WHERE user_id = ?', [id]);
      for (const enrollment of enrollments) {
        await run(this.db, 'DELETE FROM payments WHERE enrollment_id = ?', [enrollment.id]);
      }
      await run(this.db, 'DELETE FROM enrollments WHERE user_id = ?', [id]);
      const result = await run(this.db, 'DELETE FROM users WHERE id = ?', [id]);
      await run(this.db, 'COMMIT');
      return result.changes;
    } catch (error) {
      await run(this.db, 'ROLLBACK');
      throw error;
    }
  }
}

module.exports = { LmsRepository };
