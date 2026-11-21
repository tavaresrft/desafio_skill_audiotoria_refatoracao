# Playbook de transformações

Exemplos esquemáticos. Adapte nomes, biblioteca e resposta ao código encontrado; preserve contratos e não trate snippet como instrução para reescrever toda a aplicação.

## 1. SQL concatenado → parâmetros (Python/Flask)

**Antes**
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```
**Depois**
```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

## 2. SQL interpolado → bindings (Node/Express)

**Antes**
```js
db.get(`SELECT * FROM users WHERE id = ${req.params.id}`, callback);
```
**Depois**
```js
db.get('SELECT * FROM users WHERE id = ?', [req.params.id], callback);
```

## 3. Segredo literal → configuração de ambiente (ambas as stacks)

**Antes**
```python
app.secret_key = "literal-secret"
```
**Depois**
```python
app.secret_key = os.environ["APP_SECRET_KEY"]
```
Em Node, usar `process.env.APP_SECRET_KEY` e validação de configuração no boot. Não incluir fallback secreto versionado; documentar a variável sem revelar seu valor.

## 4. Rota com consulta e regra → handler fino + caso de uso

**Antes (Flask)**
```python
@app.get("/orders/<int:order_id>")
def get_order(order_id):
    row = db.execute("SELECT ...", (order_id,)).fetchone()
    # regra, joins e montagem HTTP misturados
    return jsonify(build_response(row))
```
**Depois (esquemático)**
```python
@app.get("/orders/<int:order_id>")
def get_order(order_id):
    return jsonify(order_service.fetch(order_id))
```
O service/repository só deve ser extraído se houver regra ou persistência que justifique a fronteira.

## 5. Express AppManager monolítico → router e handler separados

**Antes**
```js
class AppManager {
  constructor(app, db) { app.post('/items', (req, res) => { /* regra + SQL */ }); }
}
```
**Depois (esquemático)**
```js
router.post('/items', asyncHandler(itemController.create));
// itemController valida/adapta HTTP e delega itemService.create(input)
```
Não é necessário usar classes; mantenha estilo funcional se for o padrão local.

## 6. N+1 → consulta em lote/agregação

**Antes**
```python
for order in orders:
    order.items = query_items(order.id)
```
**Depois**
```python
items_by_order = query_items_for_orders([order.id for order in orders])
for order in orders:
    order.items = items_by_order.get(order.id, [])
```
Em SQL/ORM, considerar join, agregação ou eager loading suportado. Preservar ordenação, cardinalidade e tratamento de ausência.

## 7. Erro ignorado → falha propagada e mapeada

**Antes (Express callback)**
```js
db.run(sql, params, () => res.json({ ok: true }));
```
**Depois**
```js
db.run(sql, params, function (err) {
  if (err) return next(err);
  res.json({ ok: true });
});
```
Mapeie erro no middleware existente sem vazar detalhes internos; não responder sucesso se a persistência falhar.

## 8. `except` amplo → exceções esperadas e resposta coerente

**Antes (Flask)**
```python
try:
    result = service.run(value)
except:
    return jsonify({"error": "failed"}), 500
```
**Depois**
```python
try:
    result = service.run(value)
except ExpectedInputError as exc:
    return jsonify({"error": str(exc)}), 400
```
Erros inesperados seguem o handler central, com logging seguro. Não capturar `BaseException`/equivalente como fluxo normal.

## 9. Dados sensíveis em serializer → allowlist de campos

**Antes**
```python
return jsonify(user.to_dict())  # inclui todos os atributos
```
**Depois**
```python
return jsonify({"id": user.id, "name": user.name, "email": user.email})
```
Em ambos os runtimes, construir resposta por allowlist e testar ausência de senha/hash/token sem mudar campos públicos necessários.

## 10. Configuração dispersa → ponto de configuração explícito

**Antes**
```js
const port = 3000; // repetido em diferentes módulos
```
**Depois**
```js
const port = Number(process.env.PORT ?? 3000); // resolvido no composition root
```
Centralize apenas configuração realmente compartilhada; validar tipos/limites e manter defaults compatíveis com o projeto.
