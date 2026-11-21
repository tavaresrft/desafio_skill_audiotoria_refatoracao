"""HTTP route declarations (Views) for the public API."""

from flask import Blueprint, jsonify

import controllers


api = Blueprint("api", __name__)

api.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])
api.add_url_rule("/produtos/busca", "buscar_produtos", controllers.buscar_produtos, methods=["GET"])
api.add_url_rule("/produtos/<int:id>", "buscar_produto", controllers.buscar_produto, methods=["GET"])
api.add_url_rule("/produtos", "criar_produto", controllers.criar_produto, methods=["POST"])
api.add_url_rule("/produtos/<int:id>", "atualizar_produto", controllers.atualizar_produto, methods=["PUT"])
api.add_url_rule("/produtos/<int:id>", "deletar_produto", controllers.deletar_produto, methods=["DELETE"])
api.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
api.add_url_rule("/usuarios/<int:id>", "buscar_usuario", controllers.buscar_usuario, methods=["GET"])
api.add_url_rule("/usuarios", "criar_usuario", controllers.criar_usuario, methods=["POST"])
api.add_url_rule("/login", "login", controllers.login, methods=["POST"])
api.add_url_rule("/pedidos", "criar_pedido", controllers.criar_pedido, methods=["POST"])
api.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
api.add_url_rule(
    "/pedidos/usuario/<int:usuario_id>",
    "listar_pedidos_usuario",
    controllers.listar_pedidos_usuario,
    methods=["GET"],
)
api.add_url_rule(
    "/pedidos/<int:pedido_id>/status",
    "atualizar_status_pedido",
    controllers.atualizar_status_pedido,
    methods=["PUT"],
)
api.add_url_rule("/relatorios/vendas", "relatorio_vendas", controllers.relatorio_vendas, methods=["GET"])
api.add_url_rule("/health", "health_check", controllers.health_check, methods=["GET"])


@api.get("/")
def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


@api.post("/admin/reset-db")
def reset_database():
    return jsonify({"erro": "Operação administrativa desativada", "sucesso": False}), 410


@api.post("/admin/query")
def disable_arbitrary_query():
    return jsonify({"erro": "Execução arbitrária de SQL desativada", "sucesso": False}), 410
