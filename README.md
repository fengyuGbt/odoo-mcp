# odoo-mcp

Connect AI agents (Claude Desktop, Cursor, Windsurf) to your Odoo ERP via the Model Context Protocol.

A read-only MCP server that lets AI assistants query sales orders, inventory, customers and products through natural language — no custom Python scripts, no spreadsheet exports.

## Features

- `list_odoo_models` — discover available Odoo business models
- `search_partners` — find customers / suppliers by name or email
- `search_sales_orders` — search orders by state (draft / sent / sale / done) or customer
- `search_products` — search sellable products by name or SKU
- `get_stock_quant` — real-time on-hand stock by warehouse
- `get_sale_order_detail` — full order detail with line items

Read-only by design. No write tools in the MVP, safe to run against production data.

## Requirements

- Odoo 14+ (API keys; in-UI management from 17) or a dedicated user password
- Python 3.12+
- A client that supports MCP over stdio (Claude Desktop, Cursor, Windsurf, ...)

## Quick start

```bash
git clone <your-repo-url> && cd odoo-mcp
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # fill in your Odoo credentials
python server.py
```

Create the API key in Odoo: Settings → Users → your profile → API Keys.
For production, use a dedicated read-only user with access only to the models you expose.

## Docker

```bash
docker build -t odoo-mcp .
docker run --rm -i --env-file .env odoo-mcp
```

## Connect Claude Desktop

Add to `claude_desktop_config.json` (Claude → Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "odoo-mcp": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/absolute/path/to/.env", "odoo-mcp"]
    }
  }
}
```

For local development without Docker:

```json
{
  "mcpServers": {
    "odoo-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart the client and try:

- "Show all confirmed sales orders this month, grouped by customer."
- "How much stock of SKU PROD-001 is available in warehouse WH01?"
- "Find customers from Germany with unpaid orders."
- "Show me the full detail of order SO00123, including line items."

## Example prompts

```
Show me all confirmed sales orders this month
What's the on-hand stock of product PROD-001?
List my top 10 customers by total order amount
Who are the customers from Germany with unpaid orders?
```

## Security

- **Read-only by default** — no write tools exposed.
- **Least privilege** — use a dedicated Odoo user with read-only access.
- **Model whitelist** — optional `ODOO_ALLOWED_MODELS` env var to restrict queryable models.
- **Never commit `.env`** — it is git-ignored by default.

## Roadmap

- [x] Read-only queries (MVP)
- [ ] Write tools: create quotation / partner, with audit logging
- [ ] Multi-instance support
- [ ] Model whitelist configuration
- [ ] Managed hosting for non-technical teams

## License

MIT
