"""Odoo MCP server - read-only tools for AI agents."""
import os

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from odoo_client import OdooClient

load_dotenv()

mcp = MCPServer("odoo-mcp")

_client: OdooClient | None = None


def client() -> OdooClient:
    global _client
    if _client is None:
        _client = OdooClient(
            url=os.environ["ODOO_URL"],
            db=os.environ["ODOO_DB"],
            username=os.environ["ODOO_USER"],
            api_key=os.environ["ODOO_API_KEY"],
        )
    return _client


@mcp.tool()
def list_odoo_models(limit: int = 200) -> list[str]:
    """List available Odoo business models, e.g. sale.order, stock.quant, res.partner."""
    rows = client().search_read("ir.model", [], ["model"], limit=limit)
    return [r["model"] for r in rows]


@mcp.tool()
def search_partners(name: str = "", email: str = "", limit: int = 20) -> list[dict]:
    """Search customers and suppliers by name or email."""
    domain = [("is_company", "=", True)]
    if name:
        domain.append(("name", "ilike", name))
    if email:
        domain.append(("email", "ilike", email))
    fields = ["name", "email", "phone", "create_date"]
    return client().search_read("res.partner", domain, fields, limit=limit)


@mcp.tool()
def search_sales_orders(
    state: str = "", customer: str = "", limit: int = 20
) -> list[dict]:
    """Search sales orders by state (draft, sent, sale, done) or customer name."""
    domain: list = []
    if state:
        domain.append(("state", "=", state))
    if customer:
        domain.append(("partner_id.name", "ilike", customer))
    fields = ["name", "partner_id", "amount_total", "state", "date_order"]
    return client().search_read("sale.order", domain, fields, limit=limit)


@mcp.tool()
def search_products(name: str = "", sku: str = "", limit: int = 20) -> list[dict]:
    """Search sellable products by name or internal reference (SKU)."""
    domain = [("sale_ok", "=", True)]
    if name:
        domain.append(("name", "ilike", name))
    if sku:
        domain.append(("default_code", "=", sku))
    fields = ["name", "default_code", "list_price"]
    return client().search_read("product.product", domain, fields, limit=limit)


@mcp.tool()
def get_stock_quant(sku: str = "", name: str = "", limit: int = 20) -> list[dict]:
    """Query real-time on-hand stock by product SKU or name."""
    product_domain: list = []
    if sku:
        product_domain.append(("default_code", "=", sku))
    if name:
        product_domain.append(("name", "ilike", name))

    products = client().search_read(
        "product.product", product_domain, ["id", "name", "default_code"], limit=limit
    )
    if not products:
        return []

    ids = [p["id"] for p in products]
    quants = client().search_read(
        "stock.quant",
        [("product_id", "in", ids), ("location_id.usage", "=", "internal")],
        ["product_id", "location_id", "quantity", "reserved_quantity"],
        limit=limit,
    )
    for q in quants:
        q["product_name"] = next(
            (p["name"] for p in products if p["id"] == q["product_id"][0]), ""
        )
    return quants


@mcp.tool()
def get_sale_order_detail(order_name: str) -> dict:
    """Get a full sales order by its name, including line items and totals."""
    orders = client().search_read(
        "sale.order",
        [("name", "=", order_name)],
        ["id", "name", "amount_total", "state"],
        limit=1,
    )
    if not orders:
        return {"error": f"Order {order_name} not found"}

    order_id = orders[0]["id"]
    order = client().search_read(
        "sale.order",
        [("id", "=", order_id)],
        ["name", "partner_id", "amount_total", "state", "date_order"],
        limit=1,
    )[0]

    lines = client().search_read(
        "sale.order.line",
        [("order_id", "=", order_id)],
        ["product_id", "product_uom_qty", "price_unit", "price_subtotal"],
        limit=200,
    )
    order["lines"] = lines
    return order


if __name__ == "__main__":
    mcp.run()
