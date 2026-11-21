"""Data access and persistence operations for the commerce domain."""

from database import get_db
from security import hash_password, verify_password


def _rows_as_dicts(rows):
    return [dict(row) for row in rows]


def get_todos_produtos():
    return _rows_as_dicts(get_db().execute("SELECT * FROM produtos ORDER BY id").fetchall())


def get_produto_por_id(id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    return dict(row) if row else None


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, id),
    )
    db.commit()
    return cursor.rowcount > 0


def deletar_produto(id):
    db = get_db()
    cursor = db.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()
    return cursor.rowcount > 0


def get_todos_usuarios():
    rows = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios ORDER BY id"
    ).fetchall()
    return _rows_as_dicts(rows)


def get_usuario_por_id(id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (id,)
    ).fetchone()
    return dict(row) if row else None


def login_usuario(email, senha):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return None

    stored_password = row["senha"]
    if not verify_password(senha, stored_password):
        # Legacy accounts can still authenticate during gradual migration.
        if stored_password != senha:
            return None
        db.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?", (hash_password(senha), row["id"])
        )
        db.commit()

    return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hash_password(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def criar_pedido(usuario_id, itens):
    db = get_db()
    produtos = {}
    total = 0

    for item in itens:
        produto_id = item["produto_id"]
        quantidade = item["quantidade"]
        produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        if produto is None:
            return {"erro": f"Produto {produto_id} não encontrado"}
        if produto["estoque"] < quantidade:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        produtos[produto_id] = produto
        total += produto["preco"] * quantidade

    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            produto = produtos[item["produto_id"]]
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"pedido_id": pedido_id, "total": total}


def _pedidos_por_usuario(usuario_id=None):
    db = get_db()
    if usuario_id is None:
        orders = db.execute("SELECT * FROM pedidos ORDER BY id").fetchall()
    else:
        orders = db.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id", (usuario_id,)
        ).fetchall()
    if not orders:
        return []

    order_ids = [row["id"] for row in orders]
    placeholders = ",".join("?" for _ in order_ids)
    item_rows = db.execute(
        f"SELECT i.pedido_id, i.produto_id, p.nome AS produto_nome, i.quantidade, i.preco_unitario "
        f"FROM itens_pedido AS i LEFT JOIN produtos AS p ON p.id = i.produto_id "
        f"WHERE i.pedido_id IN ({placeholders}) ORDER BY i.id",
        order_ids,
    ).fetchall()
    items_by_order = {}
    for item in item_rows:
        items_by_order.setdefault(item["pedido_id"], []).append(
            {
                "produto_id": item["produto_id"],
                "produto_nome": item["produto_nome"] or "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            }
        )
    result = []
    for row in orders:
        order = {key: row[key] for key in ("id", "usuario_id", "status", "total", "criado_em")}
        order["itens"] = items_by_order.get(row["id"], [])
        result.append(order)
    return result


def get_pedidos_usuario(usuario_id):
    return _pedidos_por_usuario(usuario_id)


def get_todos_pedidos():
    return _pedidos_por_usuario()


def relatorio_vendas():
    db = get_db()
    summary = db.execute(
        "SELECT COUNT(*) AS total_pedidos, COALESCE(SUM(total), 0) AS faturamento, "
        "SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes, "
        "SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados, "
        "SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados FROM pedidos"
    ).fetchone()
    total_pedidos = summary["total_pedidos"]
    faturamento = summary["faturamento"]
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
    else:
        desconto = 0
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": summary["pendentes"] or 0,
        "pedidos_aprovados": summary["aprovados"] or 0,
        "pedidos_cancelados": summary["cancelados"] or 0,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
    }


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return cursor.rowcount > 0


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    clauses = []
    values = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        pattern = f"%{termo}%"
        values.extend((pattern, pattern))
    if categoria:
        clauses.append("categoria = ?")
        values.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        values.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        values.append(preco_max)
    query = "SELECT * FROM produtos"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"
    return _rows_as_dicts(get_db().execute(query, values).fetchall())
