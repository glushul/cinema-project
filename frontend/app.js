class CinemaApiProxy {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.cache = new Map();
  }

  async request(path, options = {}) {
    const method = options.method || "GET";
    const cacheKey = `${method}:${path}`;
    if (method === "GET" && this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    if (!response.ok) {
      throw new Error(`Ошибка API: ${response.status}`);
    }

    const data = await response.json();
    if (method === "GET") {
      this.cache.set(cacheKey, data);
    }
    return data;
  }

  clearCache() {
    this.cache.clear();
  }

  getStatus() {
    return this.request("/api/status");
  }

  getCatalog(sortBy) {
    return this.request(`/catalog/?sort_by=${encodeURIComponent(sortBy)}`);
  }

  getFilteredCatalog(filters) {
    const params = new URLSearchParams();
    if (filters.genre) params.set("genre", filters.genre);
    if (filters.minRating) params.set("min_rating", filters.minRating);
    if (filters.minYear) params.set("min_year", filters.minYear);
    return this.request(`/catalog/filtered?${params.toString()}`);
  }

  register(payload) {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  login(payload) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  getMe(userId) {
    return this.request(`/auth/me/${userId}`);
  }

  getSubscription(userId) {
    return this.request(`/subscription/user/${userId}`);
  }

  activateSubscription(userId, plan, paymentMethod) {
    this.clearCache();
    return this.request(`/subscription/activate/${userId}?plan=${plan}&payment_method=${paymentMethod}`, {
      method: "POST",
    });
  }

  cancelSubscription(userId) {
    this.clearCache();
    return this.request(`/subscription/cancel/${userId}`, { method: "POST" });
  }

  seedDatabase() {
    this.clearCache();
    return this.request("/seed/");
  }
}

class CatalogComponent {
  render() {
    throw new Error("Метод render должен быть реализован");
  }
}

class CatalogItem extends CatalogComponent {
  constructor(movie) {
    super();
    this.movie = movie;
  }

  render(template) {
    const node = template.content.firstElementChild.cloneNode(true);
    const poster = node.querySelector(".poster");
    const posterLabel = node.querySelector(".poster-label");

    node.tabIndex = 0;
    node.querySelector("h3").textContent = this.movie.title;
    node.querySelector("p").textContent = this.movie.year
      ? `Год выпуска: ${this.movie.year}`
      : "Год выпуска не указан";
    poster.style.setProperty("--poster", createPosterBackground(this.movie.title));
    posterLabel.textContent = this.movie.year || "HD";
    node.addEventListener("click", () => openMovieModal(this.movie));
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        openMovieModal(this.movie);
      }
    });

    return node;
  }
}

class CatalogGroup extends CatalogComponent {
  constructor(name) {
    super();
    this.name = name;
    this.children = [];
  }

  add(component) {
    this.children.push(component);
  }

  [Symbol.iterator]() {
    return new CatalogIterator(this.children);
  }

  render(root, template) {
    root.replaceChildren();
    for (const component of this) {
      root.append(component.render(template));
    }
  }
}

class CatalogIterator {
  constructor(items) {
    this.items = items;
    this.index = 0;
  }

  next() {
    if (this.index < this.items.length) {
      return { value: this.items[this.index++], done: false };
    }
    return { value: undefined, done: true };
  }
}

const api = new CinemaApiProxy();
const catalogRoot = document.querySelector("#catalogRoot");
const movieTemplate = document.querySelector("#movieTemplate");
const sortSelect = document.querySelector("#sortSelect");
const searchForm = document.querySelector("#searchForm");
const searchInput = document.querySelector("#searchInput");
const genreInput = document.querySelector("#genreInput");
const ratingInput = document.querySelector("#ratingInput");
const yearInput = document.querySelector("#yearInput");
const countText = document.querySelector("#countText");
const statusText = document.querySelector("#statusText");
const movieModal = document.querySelector("#movieModal");
const modalPoster = document.querySelector("#modalPoster");
const modalMeta = document.querySelector("#modalMeta");
const modalTitle = document.querySelector("#modalTitle");
const modalDescription = document.querySelector("#modalDescription");
const modalFacts = document.querySelector("#modalFacts");
const modalGenres = document.querySelector("#modalGenres");
const authModal = document.querySelector("#authModal");
const authButton = document.querySelector("#authButton");
const authForm = document.querySelector("#authForm");
const authModeButton = document.querySelector("#authModeButton");
const authSubmitButton = document.querySelector("#authSubmitButton");
const authTitle = document.querySelector("#authTitle");
const authMessage = document.querySelector("#authMessage");
const authName = document.querySelector("#authName");
const authEmail = document.querySelector("#authEmail");
const authPassword = document.querySelector("#authPassword");
const nameField = document.querySelector("#nameField");
const accountTitle = document.querySelector("#accountTitle");
const logoutButton = document.querySelector("#logoutButton");
const subscriptionTitle = document.querySelector("#subscriptionTitle");
const subscriptionDetails = document.querySelector("#subscriptionDetails");
const cancelSubscriptionButton = document.querySelector("#cancelSubscriptionButton");

let currentMovies = [];
let currentUser = JSON.parse(localStorage.getItem("cinema_user") || "null");
let isRegisterMode = false;

const posterImages = {
  // "Начало": "/static/posters/inception.jpg",
  // "Аватар": "/static/posters/avatar.jpg",
  "Крёстный отец": "/static/фотокарточки/godfather.jpg",
};

const posterPalettes = [
  ["#ff4d5a", "#191d2b", "#f8c14a"],
  ["#45b7ff", "#101a2b", "#e7f2ff"],
  ["#8a5cff", "#171124", "#ffd166"],
  ["#00b894", "#0d1d19", "#dffcf4"],
  ["#ff8a3d", "#211209", "#fff0df"],
  ["#c44569", "#171019", "#f7d794"],
];

function createPosterBackground(title) {
  if (posterImages[title]) {
    return `url("${posterImages[title]}")`;
  }

  const index = [...title].reduce((sum, char) => sum + char.charCodeAt(0), 0) % posterPalettes.length;
  const [primary, dark, light] = posterPalettes[index];
  return `
    radial-gradient(circle at 30% 22%, ${primary} 0 9%, transparent 10% 100%),
    radial-gradient(circle at 76% 18%, ${light} 0 4%, transparent 5% 100%),
    linear-gradient(145deg, ${primary}, ${dark} 54%, #05070b)
  `;
}

const TICKET_PRICE = 350;
let ticketQuantity = 1;

function updateTicketUI() {
  document.getElementById("qtyValue").textContent = ticketQuantity;
  document.getElementById("totalPrice").textContent = (TICKET_PRICE * ticketQuantity).toLocaleString("ru-RU");
}

document.getElementById("qtyMinus").onclick = () => {
  if (ticketQuantity > 1) { ticketQuantity--; updateTicketUI(); }
};

document.getElementById("qtyPlus").onclick = () => {
  if (ticketQuantity < 10) { ticketQuantity++; updateTicketUI(); }
};

function openMovieModal(movie) {
  modalPoster.style.setProperty("--poster", createPosterBackground(movie.title));
  modalMeta.textContent = [movie.year, movie.type].filter(Boolean).join(" • ") || "Фильм";
  modalTitle.textContent = movie.title;
  modalDescription.textContent = movie.description || "Описание пока не добавлено.";

  modalFacts.replaceChildren(
    createFact("Рейтинг", movie.rating ? movie.rating.toFixed(1) : "—"),
    createFact("Длительность", movie.duration ? `${movie.duration} мин` : "—"),
    createFact("Просмотры", movie.views ? movie.views.toLocaleString("ru-RU") : "—"),
  );

  modalGenres.replaceChildren();
  (movie.genres || []).forEach((genre) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = genre;
    modalGenres.append(chip);
  });

  movieModal.classList.add("is-open");
  movieModal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";

  ticketQuantity = 1;
  updateTicketUI();
  document.getElementById("ticketSection").style.display = "block";

  document.getElementById("buyTicketBtn").onclick = async () => {
    if (!currentUser) {
      openAuthModal();
      return;
    }
    
    const paymentMethod = document.querySelector("input[name='payment']:checked").value;

    const cinemaType = Math.random() < 0.4 ? "premium" : "standard";

    const response = await fetch("/tickets/buy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        movie_id: movie.id,
        movie_title: movie.title,
        user_id: currentUser.id,
        quantity: ticketQuantity,
        payment_method: paymentMethod,
        cinema_type: cinemaType,
      })
    });

    const data = await response.json();
    if (!response.ok) {
      document.getElementById("ticketResult").textContent = data.detail || "Ошибка";
      return;
    }
    document.getElementById("ticketResult").textContent = data.message;
  };
}

function createFact(label, value) {
  const fact = document.createElement("div");
  const labelNode = document.createElement("span");
  const valueNode = document.createElement("strong");
  fact.className = "fact";
  labelNode.textContent = label;
  valueNode.textContent = value;
  fact.append(labelNode, valueNode);
  return fact;
}

function closeMovieModal() {
  movieModal.classList.remove("is-open");
  movieModal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function openAuthModal() {
  authModal.classList.add("is-open");
  authModal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function closeAuthModal() {
  authModal.classList.remove("is-open");
  authModal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  authMessage.textContent = "";
}

function setAuthMode(registerMode) {
  isRegisterMode = registerMode;
  nameField.hidden = !registerMode;
  authTitle.textContent = registerMode ? "Регистрация" : "Вход в систему";
  authSubmitButton.textContent = registerMode ? "Создать аккаунт" : "Войти";
  authModeButton.textContent = registerMode ? "У меня уже есть аккаунт" : "Создать новый аккаунт";
}

function saveUser(user) {
  currentUser = user;
  localStorage.setItem("cinema_user", JSON.stringify(user));
  renderAccount();
  refreshSubscription();
}

function logout() {
  currentUser = null;
  localStorage.removeItem("cinema_user");
  renderAccount();
}

function renderAccount() {
  if (!currentUser) {
    authButton.textContent = "Войти";
    authButton.hidden = false;
    logoutButton.hidden = true;
    accountTitle.textContent = "Войдите, чтобы оформить подписку";
    subscriptionTitle.textContent = "Нет активной подписки";
    subscriptionDetails.textContent = "Авторизуйтесь для проверки статуса";
    cancelSubscriptionButton.hidden = true;
    return;
  }

  authButton.textContent = currentUser.name;
  logoutButton.hidden = false;
  accountTitle.textContent = `${currentUser.name}, выберите подходящий тариф`;
}

async function refreshCurrentUser() {
  if (!currentUser) return;
  const result = await api.getMe(currentUser.id);
  if (result.status === "success") {
    saveUser(result.user);
  }
}

async function refreshSubscription() {
  if (!currentUser) return;
  const result = await api.getSubscription(currentUser.id);
  if (result.status !== "success" || !result.subscription) {
    subscriptionTitle.textContent = "Нет активной подписки";
    subscriptionDetails.textContent = "Можно оформить Base или Premium";
    cancelSubscriptionButton.hidden = true;
    return;
  }

  const endDate = result.subscription.end_date
    ? new Date(result.subscription.end_date).toLocaleDateString("ru-RU")
    : "дата не указана";
  subscriptionTitle.textContent = result.subscription.plan;
  subscriptionDetails.textContent = `Действует до ${endDate}, стоимость ${result.subscription.price} ₽`;
  cancelSubscriptionButton.hidden = false;
}

function showEmpty(message) {
  catalogRoot.replaceChildren();
  const empty = document.createElement("div");
  empty.className = "empty";
  empty.textContent = message;
  catalogRoot.append(empty);
  countText.textContent = "0 фильмов";
}

function normalizeMovies(data) {
  if (Array.isArray(data)) {
    return data;
  }
  return (data.movies || []).map((movie) => (
    typeof movie === "string" ? { title: movie, year: null } : movie
  ));
}

function renderMovies(data) {
  const movies = normalizeMovies(data);
  if (!movies.length) {
    showEmpty("Ничего не найдено. Если каталог пустой, обновите его.");
    return;
  }

  const group = new CatalogGroup("Каталог фильмов");
  movies.forEach((movie) => group.add(new CatalogItem(movie)));
  group.render(catalogRoot, movieTemplate);
  countText.textContent = `${movies.length} фильмов`;
}

function applySearch() {
  const query = searchInput.value.trim().toLowerCase();
  if (!query) {
    renderMovies(currentMovies);
    return;
  }

  renderMovies(currentMovies.filter((movie) => movie.title.toLowerCase().includes(query)));
}

async function loadCatalog() {
  try {
    currentMovies = normalizeMovies(await api.getCatalog(sortSelect.value));
    statusText.textContent = "Подборка обновлена";
    applySearch();
  } catch (error) {
    showEmpty(error.message);
  }
}

async function loadFilteredCatalog() {
  try {
    const data = await api.getFilteredCatalog({
      genre: genreInput.value.trim(),
      minRating: ratingInput.value,
      minYear: yearInput.value,
    });
    currentMovies = normalizeMovies(data);
    statusText.textContent = "Фильтры применены";
    applySearch();
  } catch (error) {
    showEmpty(error.message);
  }
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authMessage.textContent = "";

  try {
    const payload = {
      email: authEmail.value,
      password: authPassword.value,
    };
    if (isRegisterMode) {
      payload.name = authName.value;
    }

    const result = isRegisterMode
      ? await api.register(payload)
      : await api.login(payload);

    if (result.status !== "success") {
      authMessage.textContent = result.message || "Не удалось выполнить действие";
      return;
    }

    saveUser(result.user);
    closeAuthModal();
    authForm.reset();
  } catch (error) {
    authMessage.textContent = "Сервер запущен без модуля авторизации. Перезапустите uvicorn.";
  }
});

authButton.addEventListener("click", openAuthModal);
authModeButton.addEventListener("click", () => setAuthMode(!isRegisterMode));
logoutButton.addEventListener("click", logout);

document.querySelectorAll(".subscribeButton").forEach((button) => {
  button.addEventListener("click", async () => {
    if (!currentUser) {
      openAuthModal();
      return;
    }

    const result = await api.activateSubscription(
      currentUser.id,
      button.dataset.plan,
      button.dataset.payment,
    );

    if (result.error) {
      subscriptionDetails.textContent = result.error;
      return;
    }

    await refreshCurrentUser();
    await refreshSubscription();
  });
});

cancelSubscriptionButton.addEventListener("click", async () => {
  if (!currentUser) return;
  await api.cancelSubscription(currentUser.id);
  await refreshCurrentUser();
  await refreshSubscription();
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  applySearch();
});
movieModal.querySelectorAll("[data-close-modal]").forEach((element) => {
  element.addEventListener("click", closeMovieModal);
});
authModal.querySelectorAll("[data-close-auth]").forEach((element) => {
  element.addEventListener("click", closeAuthModal);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && movieModal.classList.contains("is-open")) {
    closeMovieModal();
  }
  if (event.key === "Escape" && authModal.classList.contains("is-open")) {
    closeAuthModal();
  }
});
searchInput.addEventListener("input", applySearch);
document.querySelector("#filterButton").addEventListener("click", loadFilteredCatalog);
document.querySelector("#resetButton").addEventListener("click", () => {
  searchInput.value = "";
  genreInput.value = "";
  ratingInput.value = "";
  yearInput.value = "";
  loadCatalog();
});
document.querySelector("#seedButton").addEventListener("click", async () => {
  try {
    await api.seedDatabase();
    await loadCatalog();
  } catch (error) {
    statusText.textContent = "Каталог уже актуален";
  }
});
sortSelect.addEventListener("change", loadCatalog);

api.getStatus()
  .then(() => {
    statusText.textContent = "Сервис доступен";
  })
  .catch(() => {
    statusText.textContent = "Сервис недоступен";
  });

setAuthMode(false);
renderAccount();
refreshSubscription();
loadCatalog();
