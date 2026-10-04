"use strict";
const menuButton = document.querySelector(".menu-button");
const mobileMenu = document.querySelector("#mobile-menu");
function closeMenu() {
  if (!menuButton || !mobileMenu) return;
  mobileMenu.hidden = true;
  menuButton.setAttribute("aria-expanded", "false");
  menuButton.setAttribute("aria-label", "Open navigation");
}
if (menuButton && mobileMenu) {
  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    mobileMenu.hidden = !open;
  });
  mobileMenu.addEventListener("click", event => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !mobileMenu.hidden) {
      closeMenu();
      menuButton.focus();
    }
  });
  window.matchMedia("(min-width: 961px)").addEventListener("change", closeMenu);
}

const search = document.querySelector("#actor-search");
const groupSelect = document.querySelector("#actor-group");
const cards = [...document.querySelectorAll("[data-actor-card]")];
if (search && groupSelect && cards.length) {
  document.querySelector("[data-catalog-controls]").hidden = false;
  const count = document.querySelector("#catalog-count");
  const empty = document.querySelector("#catalog-empty");
  const update = () => {
    const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let total = 0;
    cards.forEach(card => {
      const matches = words.every(word => card.dataset.search.includes(word)) &&
        (!groupSelect.value || card.dataset.group === groupSelect.value);
      card.hidden = !matches;
      if (matches) total += 1;
    });
    count.textContent = `${total} of ${cards.length} Actors`;
    empty.hidden = total !== 0;
  };
  search.addEventListener("input", update);
  groupSelect.addEventListener("change", update);
  document.querySelector("#clear-filters").addEventListener("click", () => {
    search.value = "";
    groupSelect.value = "";
    update();
    search.focus();
  });
}

document.querySelectorAll("[data-copy]").forEach(button => {
  button.addEventListener("click", async () => {
    const content = document.getElementById(button.dataset.copy);
    if (!content) return;
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(content.textContent);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Select the text to copy";
    }
    setTimeout(() => { button.textContent = original; }, 2000);
  });
});
