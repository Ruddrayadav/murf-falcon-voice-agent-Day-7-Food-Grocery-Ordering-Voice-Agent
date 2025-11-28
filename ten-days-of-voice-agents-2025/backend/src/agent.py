import logging
import json
import os
from datetime import datetime
from typing import Annotated, Optional, List
from dataclasses import dataclass, asdict

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

# Plugins
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# 📁 FIXED JSON PATHS (WORKS ALWAYS)
# ======================================================

BASE_DIR = os.path.dirname(__file__)
CATALOG_FILE = os.path.join(BASE_DIR, "catalog.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Auto-create missing files
if not os.path.exists(CATALOG_FILE):
    raise FileNotFoundError(
        f"catalog.json NOT FOUND in: {CATALOG_FILE}\n"
        f"➡️ FIX: Put catalog.json inside /src next to agent.py"
    )

if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w") as f:
        json.dump([], f, indent=4)

# ======================================================
# 🛒 DATA MODELS
# ======================================================

@dataclass
class CartItem:
    name: str
    quantity: int
    price: float

@dataclass
class Order:
    order_id: str
    timestamp: str
    items: List[CartItem]
    total: float
    status: str = "received"

@dataclass
class Userdata:
    cart: List[CartItem] = None

    def __post_init__(self):
        if self.cart is None:
            self.cart = []

# ======================================================
# 🔧 JSON HELPERS
# ======================================================

def load_catalog():
    with open(CATALOG_FILE, "r") as f:
        return json.load(f)

def load_orders():
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ======================================================
# 🛠️ TOOLS
# ======================================================

@function_tool
async def add_to_cart(
    ctx: RunContext[Userdata],
    item_name: Annotated[str, Field(description="Name of item to add")],
    quantity: Annotated[int, Field(description="Number of units")],
) -> str:
    """
    Adds an item from the catalog to the cart.
    """

    catalog = load_catalog()
    name = item_name.lower()

    item = next((x for x in catalog if x["name"].lower() == name), None)

    if not item:
        return "NOT_FOUND"

    # Update if already inside cart
    for ci in ctx.userdata.cart:
        if ci.name.lower() == name:
            ci.quantity += quantity
            return f"UPDATED|{ci.name}|{ci.quantity}"

    ctx.userdata.cart.append(
        CartItem(name=item["name"], quantity=quantity, price=float(item["price"]))
    )
    return f"ADDED|{item['name']}|{quantity}"


@function_tool
async def remove_from_cart(
    ctx: RunContext[Userdata],
    item_name: Annotated[str, Field(description="Item name to remove")],
) -> str:
    """
    Remove item completely from cart.
    """
    name = item_name.lower()
    before = len(ctx.userdata.cart)

    ctx.userdata.cart = [x for x in ctx.userdata.cart if x.name.lower() != name]

    after = len(ctx.userdata.cart)

    return "REMOVED" if after < before else "NOT_FOUND"


@function_tool
async def place_order(
    ctx: RunContext[Userdata],
) -> str:
    """
    Saves the user's order to JSON + clears cart.
    """
    if not ctx.userdata.cart:
        return "EMPTY"

    total = sum(x.price * x.quantity for x in ctx.userdata.cart)

    new_order = Order(
        order_id=f"ORD-{int(datetime.now().timestamp())}",
        timestamp=datetime.now().isoformat(),
        items=ctx.userdata.cart.copy(),
        total=round(total, 2),
    )

    all_orders = load_orders()
    all_orders.append(asdict(new_order))
    save_orders(all_orders)

    ctx.userdata.cart.clear()

    return f"PLACED|{new_order.order_id}|{new_order.total}"


@function_tool
async def ingredients_for(
    ctx: RunContext[Userdata],
    dish_name: Annotated[str, Field(description="Dish like pasta / sandwich")],
) -> str:
    """
    Returns list of ingredients for a given dish.
    """

    RECIPES = {
        "peanut butter sandwich": ["bread", "peanut butter"],
        "pasta": ["pasta", "pasta sauce"],
        "tea": ["tea powder", "milk", "sugar"],
    }

    dish = dish_name.lower().strip()

    if dish not in RECIPES:
        return "NO_RECIPE"

    return "ING|" + "|".join(RECIPES[dish])

# ======================================================
# 🤖 AGENT
# ======================================================

class GroceryAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are SAM — a friendly grocery ordering assistant for FreshCart.

Capabilities:
- Add items to cart using add_to_cart
- Remove items using remove_from_cart
- Handle “ingredients for X” intelligently
- Place orders using place_order
- Never invent items not in catalog.json

Conversation Flow:
1. Greeting:
   “Hi! Welcome to FreshCart. What would you like to order today?”

2. Adding/removing items:
   - If user says “add 2 milk”, call add_to_cart
   - If user says “remove eggs”, call remove_from_cart

3. Ingredients:
   - If user says “ingredients for pasta”
     → call ingredients_for(dish_name)
     → for each returned ingredient, call add_to_cart(quantity=1)

4. Cart check:
   If user says “what’s in my cart?”, list items from userdata.cart.

5. Placing order:
   User says: “place order”
   → call place_order
   → Respond with order ID & amount

Keep replies short, friendly, helpful.
            """,
            tools=[add_to_cart, remove_from_cart, place_order, ingredients_for],
        )



def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    userdata = Userdata()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-marcus",
            style="Conversational",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    await session.start(
        agent=GroceryAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
