# 🛒 Day 7 – Food & Grocery Ordering Voice Agent  
### Murf AI Voice Agents Challenge (10 Days of AI Voice Agents)

This project is my **Day 7 submission** for the  
🔥 **Murf AI Voice Agents Challenge**  
Built using **LiveKit Agents + Murf Falcon TTS + Deepgram STT + Gemini LLM**.

The goal:  
Create a **fully conversational grocery ordering assistant** that can understand items, manage a cart, add recipe ingredients automatically, and save final orders to JSON.

---

## 🚀 Features Implemented

### 🛍️ 1. Grocery Catalog (JSON-Based)
A custom `catalog.json` file containing grocery, snacks, and prepared food items:
- Bread  
- Eggs  
- Milk  
- Snacks  
- Pasta + Sauce  
- Sandwiches  
…and more.

### 🛠️ 2. AI Voice Ordering System
The agent can understand natural speech like:
- “Add 2 breads”
- “Remove eggs”
- “I need ingredients for pasta”
- “What’s in my cart?”
- “Place my order”

### 🧠 3. Intelligent Recipe Mapping
A hardcoded recipe engine lets users say:
- “Ingredients for tea”
- “Ingredients for peanut butter sandwich”
- “Ingredients for pasta”

The agent automatically adds all required items to cart.

### 🛒 4. Cart Management
Implemented with `Userdata`:
- Add items  
- Update quantities  
- Remove items  
- List all cart contents  

### 💾 5. Order Creation (orders.json)
When the user says “Place my order”, the agent:
- Calculates total cost  
- Generates unique order ID  
- Saves the order to `orders.json`  
- Clears the cart  
- Responds with confirmation

### 🎤 6. Voice Interface
Built with:
- **Deepgram Nova-3** (STT)
- **Gemini 2.5 Flash** (LLM)
- **Murf Falcon TTS** for ultra-fast responses
- **Silero VAD + LiveKit Turn Detection**

---

## 📁 Project Structure

```
/backend  
  ├── src/  
  │    ├── agent.py          # Main voice agent logic  
  │    ├── catalog.json      # Product database  
  │    ├── orders.json       # Saved orders  
  │    └── ...  
  ├── .env.local  
  └── README.md  
```

---

## 🔧 Tools Used

- **LiveKit Agents Framework**
- **Deepgram STT**
- **Google Gemini Flash**
- **Murf AI Falcon TTS**
- **Python Dataclasses**
- **JSON Storage**
- **Function Tools & Agent Instructions**

---

## 🗣️ Agent Capabilities

### The agent can:
✔ Understand grocery item requests  
✔ Understand quantities  
✔ Map meals → ingredients  
✔ Maintain cart state  
✔ Save orders with timestamps  
✔ Talk naturally using Murf Falcon  
✔ Auto-handle multi-step ordering flows  

---

## ▶️ How to Run

```bash
uv run python src/agent.py dev
```

Make sure you have:
- `.env.local` configured with your Murf/Deepgram keys
- `catalog.json` and `orders.json` present in your project folder

---

## 🏁 Challenge Goal Completed

This project fulfills the **complete Day-7 primary requirement**:
- Catalog  
- Cart  
- Ingredient intelligence  
- Order placement  
- JSON persistence  

Next step → **Advanced Goals** (Order Tracking, History, Concurrent Orders).

---

## ⭐ Author
Built by **Rudra**  
Part of the **Murf AI Voice Agents Challenge – #10DaysofAIVoiceAgents**

