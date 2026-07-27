/* =========================================================================
   Jamal Cart — frontend logic
   Vanilla JS, no build step. Talks to the FastAPI backend via fetch().
   ========================================================================= */

const API = ""; // same-origin

const state = {
  userId: localStorage.getItem("jamal_user_id") || null,
  userName: localStorage.getItem("jamal_user_name") || null,
  category: "",
  keyword: "",
  cartCount: 0,
};

// ---------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = body.detail || "Something went wrong.";
    throw new Error(message);
  }
  return body;
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.remove("is-visible"), 2600);
}

function money(n) {
  return `${Number(n).toLocaleString()} PKR`;
}

// ---------------------------------------------------------------------
// Product catalog
// ---------------------------------------------------------------------

function renderProducts(products) {
  const grid = $("#product-grid");
  const empty = $("#catalog-empty");
  grid.innerHTML = "";

  if (!products || products.length === 0) {
    empty.hidden = false;
    $("#catalog-count").textContent = "";
    return;
  }
  empty.hidden = true;
  $("#catalog-count").textContent = `${products.length} item${products.length === 1 ? "" : "s"}`;

  for (const p of products) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-thumb">${(p.name || "?").charAt(0)}</div>
      <div class="product-card-top">
        <p class="product-name">${p.name}</p>
        ${p.discount_percent ? `<span class="discount-tag">-${p.discount_percent}%</span>` : ""}
      </div>
      <div class="product-meta">${p.brand || "Jamal Cart"} · Stock: ${p.stock ?? "N/A"}</div>
      <div class="product-price">${money(p.price)}</div>
      <div class="product-actions">
        <button class="add-cart-btn" data-id="${p.id}">Add to cart</button>
        <button class="wish-btn" data-id="${p.id}" aria-label="Add to wishlist">
          <svg viewBox="0 0 24 24" width="16" height="16"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M12 20.5s-8-5-8-11.2C4 5.8 6.2 4 8.7 4c1.6 0 3 .8 3.3 2 .3-1.2 1.7-2 3.3-2C17.8 4 20 5.8 20 9.3c0 6.2-8 11.2-8 11.2Z"/></svg>
        </button>
      </div>
    `;
    grid.appendChild(card);
  }

  grid.querySelectorAll(".add-cart-btn").forEach((btn) => {
    btn.addEventListener("click", () => addToCart(btn.dataset.id));
  });
  grid.querySelectorAll(".wish-btn").forEach((btn) => {
    btn.addEventListener("click", () => addToWishlist(btn.dataset.id, btn));
  });
}

async function loadProducts() {
  try {
    let result;
    if (state.keyword) {
      result = await api(`/products/search?keyword=${encodeURIComponent(state.keyword)}`);
    } else if (state.category) {
      result = await api(`/products/category/${encodeURIComponent(state.category)}`);
    } else {
      result = await api("/products");
    }
    renderProducts(result.data);
  } catch (err) {
    showToast(err.message);
  }
}

$$(".cat-pill").forEach((pill) => {
  pill.addEventListener("click", () => {
    $$(".cat-pill").forEach((p) => p.classList.remove("is-active"));
    pill.classList.add("is-active");
    state.category = pill.dataset.category;
    state.keyword = "";
    $("#search-input").value = "";
    $("#catalog-title").textContent = state.category ? `${state.category}` : "All products";
    loadProducts();
  });
});

let searchDebounce;
$("#search-input").addEventListener("input", (e) => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    state.keyword = e.target.value.trim();
    $("#catalog-title").textContent = state.keyword ? `Results for "${state.keyword}"` : "All products";
    loadProducts();
  }, 350);
});

// ---------------------------------------------------------------------
// Cart
// ---------------------------------------------------------------------

function requireLogin() {
  if (!state.userId) {
    showToast("Please log in first.");
    openAuth("login");
    return false;
  }
  return true;
}

async function addToCart(productId) {
  if (!requireLogin()) return;
  try {
    await api("/cart/add", {
      method: "POST",
      body: JSON.stringify({ user_id: state.userId, product_id: productId, quantity: 1 }),
    });
    showToast("Added to cart.");
    refreshCartCount();
  } catch (err) {
    showToast(err.message);
  }
}

async function addToWishlist(productId, btn) {
  if (!requireLogin()) return;
  try {
    await api("/wishlist/add", {
      method: "POST",
      body: JSON.stringify({ user_id: state.userId, product_id: productId }),
    });
    btn.classList.add("is-active");
    showToast("Added to wishlist.");
  } catch (err) {
    showToast(err.message);
  }
}

async function refreshCartCount() {
  if (!state.userId) {
    $("#cart-count").textContent = "0";
    return;
  }
  try {
    const result = await api(`/cart/${state.userId}`);
    const items = result.data || [];
    state.cartCount = items.reduce((sum, i) => sum + i.quantity, 0);
    $("#cart-count").textContent = state.cartCount;
  } catch {
    /* silent - cart badge just stays stale */
  }
}

async function renderCartDrawer() {
  const body = $("#cart-body");
  const footer = $("#cart-footer");

  if (!state.userId) {
    body.innerHTML = `<p class="empty-state">Log in to view your cart.</p>`;
    footer.hidden = true;
    return;
  }

  try {
    const result = await api(`/cart/${state.userId}`);
    const items = result.data || [];

    if (items.length === 0) {
      body.innerHTML = `<p class="empty-state">Your cart is empty.</p>`;
      footer.hidden = true;
      return;
    }

    body.innerHTML = "";
    let total = 0;
    for (const item of items) {
      const p = item.products;
      if (!p) continue;
      const lineTotal = p.price * item.quantity;
      total += lineTotal;
      const row = document.createElement("div");
      row.className = "cart-line";
      row.innerHTML = `
        <div>
          <p class="cart-line-name">${p.name}</p>
          <p class="cart-line-qty">Qty ${item.quantity}</p>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <span class="cart-line-price">${money(lineTotal)}</span>
          <button class="cart-line-remove" data-id="${item.product_id}" aria-label="Remove">✕</button>
        </div>
      `;
      body.appendChild(row);
    }

    body.querySelectorAll(".cart-line-remove").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await api("/cart/remove", {
          method: "DELETE",
          body: JSON.stringify({ user_id: state.userId, product_id: btn.dataset.id }),
        });
        renderCartDrawer();
        refreshCartCount();
      });
    });

    $("#cart-total-value").textContent = money(total);
    footer.hidden = false;
  } catch (err) {
    body.innerHTML = `<p class="empty-state">${err.message}</p>`;
    footer.hidden = true;
  }
}

$("#cart-btn").addEventListener("click", () => {
  renderCartDrawer();
  toggleDrawer("cart-drawer", "cart-overlay", true);
});
$("#cart-close").addEventListener("click", () => toggleDrawer("cart-drawer", "cart-overlay", false));
$("#cart-overlay").addEventListener("click", () => {
  toggleDrawer("cart-drawer", "cart-overlay", false);
  toggleAuth(false);
});

$("#checkout-btn").addEventListener("click", async () => {
  const address = $("#checkout-address").value.trim();
  if (!address) {
    showToast("Please enter a shipping address.");
    return;
  }
  try {
    const result = await api("/checkout", {
      method: "POST",
      body: JSON.stringify({ user_id: state.userId, shipping_address: address }),
    });
    showToast(`Order placed! ID: ${result.data.id}`);
    toggleDrawer("cart-drawer", "cart-overlay", false);
    refreshCartCount();
  } catch (err) {
    showToast(err.message);
  }
});

function toggleDrawer(drawerId, overlayId, open) {
  $(`#${drawerId}`).classList.toggle("is-open", open);
  $(`#${overlayId}`).classList.toggle("is-open", open);
}

// ---------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------

function openAuth(tab) {
  $("#auth-modal").classList.add("is-open");
  $("#auth-overlay").classList.add("is-open");
  setAuthTab(tab);
}
function toggleAuth(open) {
  $("#auth-modal").classList.toggle("is-open", open);
  $("#auth-overlay").classList.toggle("is-open", open);
}
function setAuthTab(tab) {
  $$(".auth-tab").forEach((t) => t.classList.toggle("is-active", t.dataset.tab === tab));
  $("#login-form").hidden = tab !== "login";
  $("#register-form").hidden = tab !== "register";
}

$$(".auth-tab").forEach((t) => t.addEventListener("click", () => setAuthTab(t.dataset.tab)));
$("#auth-close").addEventListener("click", () => toggleAuth(false));

$("#account-btn").addEventListener("click", () => {
  if (state.userId) {
    // simple logout
    localStorage.removeItem("jamal_user_id");
    localStorage.removeItem("jamal_user_name");
    state.userId = null;
    state.userName = null;
    $("#account-btn").textContent = "Log in";
    refreshCartCount();
    showToast("Logged out.");
  } else {
    openAuth("login");
  }
});

$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msgEl = $("#login-msg");
  msgEl.className = "auth-msg";
  try {
    const result = await api("/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("#login-email").value,
        password: $("#login-password").value,
      }),
    });
    onAuthSuccess(result.data);
  } catch (err) {
    msgEl.textContent = err.message;
  }
});

$("#register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msgEl = $("#register-msg");
  msgEl.className = "auth-msg";
  try {
    const result = await api("/register", {
      method: "POST",
      body: JSON.stringify({
        full_name: $("#register-name").value,
        email: $("#register-email").value,
        phone: $("#register-phone").value || null,
        password: $("#register-password").value,
      }),
    });
    onAuthSuccess(result.data);
  } catch (err) {
    msgEl.textContent = err.message;
  }
});

function onAuthSuccess(user) {
  state.userId = user.id;
  state.userName = user.full_name;
  localStorage.setItem("jamal_user_id", user.id);
  localStorage.setItem("jamal_user_name", user.full_name);
  $("#account-btn").textContent = user.full_name.split(" ")[0];
  toggleAuth(false);
  showToast(`Welcome, ${user.full_name.split(" ")[0]}!`);
  refreshCartCount();
}

// ---------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------

function appendMessage(role, text, data) {
  const container = $("#chat-messages");
  const wrap = document.createElement("div");
  wrap.className = `msg msg--${role}`;

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  container.appendChild(wrap);

  // If the bot returned a product list, render mini chips beneath the bubble.
  if (role === "bot" && Array.isArray(data) && data.length && data[0]?.price !== undefined) {
    const list = document.createElement("div");
    list.className = "msg-products";
    for (const p of data.slice(0, 5)) {
      const chip = document.createElement("div");
      chip.className = "msg-product-chip";
      chip.innerHTML = `<span class="chip-name">${p.name}</span><span class="chip-price">${money(p.price)}</span>`;
      list.appendChild(chip);
    }
    container.appendChild(list);
  }

  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage(text) {
  appendMessage("user", text);
  $("#chat-typing").hidden = false;

  try {
    const result = await api("/chat", {
      method: "POST",
      body: JSON.stringify({ message: text, user_id: state.userId }),
    });
    $("#chat-typing").hidden = true;
    appendMessage("bot", result.message, result.data);

    // Cart/order actions from chat should refresh the header badge.
    if (["add_to_cart", "remove_from_cart", "checkout"].includes(result.intent)) {
      refreshCartCount();
    }
  } catch (err) {
    $("#chat-typing").hidden = true;
    appendMessage("bot", "Sorry, I couldn't reach the assistant. Please try again.");
  }
}

$("#chat-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("#chat-input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendChatMessage(text);
});

function openChat() {
  $("#chat-panel").classList.add("is-open");
}
$("#chat-fab").addEventListener("click", openChat);
$("#chat-close").addEventListener("click", () => $("#chat-panel").classList.remove("is-open"));
$("#hero-chat-cta").addEventListener("click", () => {
  openChat();
  $("#chat-input").focus();
  $("#chat-panel").scrollIntoView({ behavior: "smooth", block: "center" });
});

// ---------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------

(function init() {
  if (state.userId && state.userName) {
    $("#account-btn").textContent = state.userName.split(" ")[0];
  }
  loadProducts();
  refreshCartCount();
})();