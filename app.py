import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# App configuration
st.set_page_config(
    page_title="Jamal Cart Bot & Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .product-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #eef2f6;
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://127.0.0.1:8000"

# Initialize Session State
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Auth
st.sidebar.title("👤 User Account")
if st.session_state.user is None:
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    email = st.sidebar.text_input("Email")
    
    if auth_mode == "Sign Up":
        full_name = st.sidebar.text_input("Full Name")
        if st.sidebar.button("Register"):
            if email and full_name:
                try:
                    res = requests.post(f"{API_URL}/api/auth/register", json={"email": email, "full_name": full_name})
                    if res.status_code == 200:
                        st.session_state.user = res.json()
                        st.sidebar.success(f"Registered & Logged in as {full_name}!")
                        st.rerun()
                    else:
                        st.sidebar.error(res.json().get("detail", "Registration failed."))
                except Exception:
                    st.sidebar.error("Could not connect to API server. Please make sure the backend is running.")
            else:
                st.sidebar.warning("Please fill out all fields.")
    else:
        if st.sidebar.button("Login"):
            if email:
                try:
                    res = requests.post(f"{API_URL}/api/auth/login", json={"email": email})
                    if res.status_code == 200:
                        st.session_state.user = res.json()
                        st.sidebar.success(f"Welcome back, {st.session_state.user['full_name']}!")
                        st.rerun()
                    else:
                        st.sidebar.error("User not found or login failed.")
                except Exception:
                    st.sidebar.error("Could not connect to API server.")
            else:
                st.sidebar.warning("Please enter your email.")
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user['full_name']}**")
    st.sidebar.write(f"Email: `{st.session_state.user['email']}`")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

# Title
st.title("🛍️ Jamal Cart Bot & Store")
st.write("Welcome to the next generation shopping assistant and store experience powered by FastAPI & Streamlit.")

# Tabs
tab1, tab2, tab3 = st.tabs(["🛒 Store Catalog", "🛍️ Shopping Cart & Orders", "💬 AI Assistant Chat"])

# 1. Store Catalog Tab
with tab1:
    st.header("Browse Catalog")
    try:
        # Load products
        prod_res = requests.get(f"{API_URL}/api/products")
        if prod_res.status_code == 200:
            products = prod_res.json()
            categories = list(set(p['category'] for p in products))
            
            selected_cat = st.selectbox("Filter by Category", ["All"] + categories)
            filtered_prods = [p for p in products if selected_cat == "All" or p['category'] == selected_cat]
            
            cols = st.columns(3)
            for idx, p in enumerate(filtered_prods):
                col = cols[idx % 3]
                with col:
                    st.markdown(f"""
                    <div class="product-card">
                        <h3>{p['name']}</h3>
                        <p><strong>Category:</strong> {p['category']}</p>
                        <p>{p['description']}</p>
                        <h4 style="color: #2E7D32;">Price: {p['price']} PKR</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.user:
                        if st.button(f"Add to Cart", key=f"add_{p['id']}"):
                            cart_data = {
                                "user_id": st.session_state.user['id'],
                                "product_id": p['id'],
                                "quantity": 1
                            }
                            add_res = requests.post(f"{API_URL}/api/cart", json=cart_data)
                            if add_res.status_code == 200:
                                st.toast(f"Added {p['name']} to cart!")
                            else:
                                st.error("Failed to add item to cart.")
                    else:
                        st.info("Log in to add items to your cart")
        else:
            st.error("Failed to fetch products.")
    except Exception:
        st.warning("API server is not running. Please start the backend API first.")

# 2. Cart & Orders Tab
with tab2:
    if st.session_state.user is None:
        st.warning("Please sign in or register to access the cart and checkout.")
    else:
        st.header("Your Shopping Cart")
        try:
            cart_res = requests.get(f"{API_URL}/api/cart/{st.session_state.user['id']}")
            if cart_res.status_code == 200:
                cart_items = cart_res.json()
                if not cart_items:
                    st.info("Your cart is empty.")
                else:
                    total = 0.0
                    for item in cart_items:
                        p = item.get('products') or item.get('product')
                        if not p:
                            continue
                        subtotal = float(p['price']) * item['quantity']
                        total += subtotal
                        
                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        c1.write(f"**{p['name']}** - {p['price']} PKR")
                        c2.write(f"Quantity: {item['quantity']}")
                        c3.write(f"Subtotal: {subtotal:.2f} PKR")
                        if c4.button("Remove", key=f"remove_{p['id']}"):
                            requests.delete(f"{API_URL}/api/cart/{st.session_state.user['id']}/{p['id']}")
                            st.rerun()
                    
                    st.write("---")
                    st.markdown(f"### **Total Amount: {total:.2f} PKR**")
                    
                    # Checkout
                    shipping_addr = st.text_area("Shipping Address", "123 Main St, Karachi, Pakistan")
                    if st.button("Place Order"):
                        checkout_data = {
                            "user_id": st.session_state.user['id'],
                            "shipping_address": shipping_addr
                        }
                        order_res = requests.post(f"{API_URL}/api/checkout", json=checkout_data)
                        if order_res.status_code == 200:
                            st.success("Order placed successfully!")
                            st.rerun()
                        else:
                            st.error(order_res.json().get("detail", "Checkout failed."))
            else:
                st.error("Failed to fetch cart.")
        except Exception:
            st.warning("Could not fetch cart.")

        # Order history
        st.header("Order History")
        try:
            orders_res = requests.get(f"{API_URL}/api/orders/{st.session_state.user['id']}")
            if orders_res.status_code == 200:
                orders = orders_res.json()
                if not orders:
                    st.write("No previous orders found.")
                else:
                    for o in orders:
                        st.markdown(f"""
                        **Order ID:** `{o['id']}` | **Total:** {o['total_amount']} PKR | **Status:** `{o['status']}`
                        """)
            else:
                st.error("Failed to fetch orders.")
        except Exception:
            st.warning("Could not fetch order history.")

# 3. Chatbot Tab
with tab3:
    st.header("Chat with Jamal Cart Assistant")
    st.write("Ask about categories, products, current discounts, return/refund policies, or check your cart/order status.")

    # Show message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask me anything about Jamal Cart..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare payloads
        user_id = st.session_state.user['id'] if st.session_state.user else None
        chat_payload = {"message": prompt, "user_id": user_id}
        
        # Get AI response
        try:
            res = requests.post(f"{API_URL}/api/chat", json=chat_payload)
            if res.status_code == 200:
                bot_response = res.json()["response"]
            else:
                bot_response = "Sorry, I'm having trouble understanding you right now."
        except Exception:
            bot_response = "I cannot connect to the backend server. Please make sure the API service is running."

        # Display assistant response
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
