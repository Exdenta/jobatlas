(() => {
  "use strict";


  // Reveal sections when motion and IntersectionObserver permit.
  const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
  let revealObserver;
  const configureMotion = () => {
    revealObserver?.disconnect();
    document.querySelectorAll(".is-revealed").forEach((node) => node.classList.remove("is-revealed"));
    if (motionPreference.matches || !("IntersectionObserver" in window)) return;
    revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".home-section .section-heading, .outcome-card, .product-card, .contract-code, .integration-grid, .proof-list, .resource-grid, .detail-hero")
      .forEach((node) => revealObserver.observe(node));
  };
  configureMotion();
  motionPreference.addEventListener("change", configureMotion);

  const menuButton = document.querySelector("[data-menu-button]");
  const mobileMenu = document.querySelector("[data-mobile-menu]");

  const setMenuOpen = (open) => {
    if (!menuButton || !mobileMenu) return;
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    mobileMenu.classList.toggle("is-open", open);
    document.body.classList.toggle("menu-open", open);
  };

  menuButton?.addEventListener("click", () => {
    setMenuOpen(menuButton.getAttribute("aria-expanded") !== "true");
  });

  mobileMenu?.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenuOpen(false);
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenuOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 960) setMenuOpen(false);
  });

  const hooks = new Set();
  const eventRules = new Map("actor_cta_click:actor asset_cta_click:actor choose_actor_click:actor contract_cta_click:actor cta_click:category,label first_run_selected:product guide_cta_click:actor history_cta_click:actor install_command_copied:category,product,format integration_click:label integration_page_click:actor methodology_cta_click:actor navigation_click:category,label outbound_click:category,label,destination page_view:category,label path_selected:label product_page_click:actor product_selected:product sample_copied:product,format sample_download:product,format sample_source_selected:product,format sample_view:product,format skill_source_selected:category,product source_cta_click:actor support_cta_click:actor".split(" ").map((rule) => { const [event, fields] = rule.split(":"); return [event, fields.split(",")]; }));
  const canonicalPages = new Set("/ /about /actors /actors/ai-job-fit-scorer /actors/euraxess /actors/linkedin /actors/ycombinator /changelog /contracts /guides /guides/ai-job-fit-scoring-api /guides/euraxess-jobs-api-export /guides/linkedin-job-alerts-n8n /guides/linkedin-jobs-api-alternatives /integrations /integrations/airtable /integrations/api /integrations/make /integrations/mcp /integrations/n8n /integrations/python /integrations/zapier /methodology /privacy".split(" "));
  const fields = "category label placement product actor destination format".split(" ");
  const campaignSources = new Set("jobatlas devto linkedin youtube github apify n8n make".split(" "));
  const campaignMedia = new Set("owned-site tutorial social video documentation template referral".split(" "));
  const campaignNames = new Set("actor-discovery linkedin-alerts euraxess-tracker yc-tracker fit-scoring".split(" "));
  const privacyEnabled = navigator.globalPrivacyControl === true ||
    navigator.doNotTrack === "1" || window.doNotTrack === "1";

  const sanitize = (properties = {}) => Object.fromEntries(fields.flatMap((key) => {
    const value = typeof properties?.[key] === "string" ? properties[key].trim() : "";
    return /^[a-z0-9][a-z0-9_-]{0,63}$/.test(value) ? [[key, value]] : [];
  }));

  const pageValue = () => {
    const robots = document.querySelector('meta[name="robots"]')?.content ?? "";
    if (/(^|,)\s*noindex\s*(,|$)/i.test(robots)) return "/404";
    const normalized = window.location.pathname.replace(/\/+$/, "") || "/";
    return canonicalPages.has(normalized) ? normalized : "/404";
  };

  const campaignData = () => {
    const query = new URLSearchParams(window.location.search);
    const [s, m, c, t] = ["source", "medium", "campaign", "content"].map((name) => query.getAll(`utm_${name}`));
    if (s.length !== 1 || m.length !== 1 || c.length !== 1 || t.length > 1) return {};
    const source = s[0] === "nomad-agent-job-scrapers" ? "jobatlas" : s[0];
    const [medium] = m, [campaign] = c, [content] = t;
    if (!campaignSources.has(source) || !campaignMedia.has(medium) || !campaignNames.has(campaign)) return {};
    if (content !== undefined && !/^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/.test(content)) return {};
    return { source, medium, campaign, ...(content ? { content } : {}) };
  };

  const track = (name, properties = {}) => {
    const required = eventRules.get(name);
    if (privacyEnabled || !required) return false;
    const props = sanitize(properties);
    if (!props.placement || required.some((key) => !props[key]) ||
      typeof window.crypto?.randomUUID !== "function") return false;

    const campaign = campaignData();
    const detail = Object.freeze({
      schemaVersion: "jobatlas-site-event-v1", eventId: window.crypto.randomUUID(),
      occurredAt: new Date().toISOString(), activityClass: "unclassified",
      event: name, page: pageValue(), ...campaign, ...props,
    });
    window.dispatchEvent(new CustomEvent("nomad-agent:analytics", { detail }));

    if (Array.isArray(window.dataLayer)) window.dataLayer.push({ ...detail });

    if (typeof window.plausible === "function")
      window.plausible(name, { props: { page: detail.page, ...campaign, ...props } });

    hooks.forEach((hook) => { try { hook(detail); } catch {} });
    return true;
  };

  const subscribe = (hook) => typeof hook !== "function" ? () => {} :
    (hooks.add(hook), () => hooks.delete(hook));

  window.nomadAgentAnalytics = Object.freeze({ track, subscribe,
    collectorConfigured: () => Array.isArray(window.dataLayer) ||
      typeof window.plausible === "function" || hooks.size > 0 });

  document.addEventListener("click", (event) => {
    const origin = event.target instanceof Element ? event.target : event.target.parentElement;
    const element = origin?.closest("[data-event]");
    if (!element) return;
    const properties = Object.fromEntries(fields.flatMap((key) =>
      element.dataset[key] ? [[key, element.dataset[key]]] : []));
    track(element.dataset.event, properties);
  });

  if (!privacyEnabled) {
    const [pageGroup = "home"] = pageValue().split("/").filter(Boolean);
    track("page_view", { category: "navigation", label: pageGroup, placement: "document" });
  }

  const copyButton = document.querySelector("[data-copy-command]");
  const command = document.querySelector("[data-command]");
  const commandStatus = document.querySelector("[data-command-status]");
  const sourceOptions = document.querySelectorAll("[data-source-option]");
  let copyResetTimer;

  const resetCopyFeedback = () => {
    window.clearTimeout(copyResetTimer);
    copyButton?.classList.remove("is-copied");
    copyButton?.setAttribute("aria-label", "Copy install command");
    if (commandStatus) commandStatus.textContent = "";
  };

  const copyText = async (value) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
      return;
    }

    const textArea = document.createElement("textarea");
    textArea.value = value;
    textArea.setAttribute("readonly", "");
    textArea.className = "clipboard-fallback";
    document.body.append(textArea);
    textArea.select();
    const copied = document.execCommand("copy");
    textArea.remove();
    if (!copied) throw new Error("Copy command failed");
  };

  sourceOptions.forEach((option) => {
    option.addEventListener("click", () => {
      sourceOptions.forEach((candidate) => {
        candidate.setAttribute("aria-pressed", String(candidate === option));
      });
      if (command) command.textContent = option.dataset.commandValue ?? "";
      resetCopyFeedback();
      track("skill_source_selected", {
        category: "agent_skill",
        product: option.dataset.sourceOption,
        placement: "skill-installer",
      });
    });
  });

  copyButton?.addEventListener("click", async () => {
    try {
      await copyText(command?.textContent?.trim() ?? "");
      copyButton.classList.add("is-copied");
      copyButton.setAttribute("aria-label", "Install command copied");
      if (commandStatus) commandStatus.textContent = "Install command copied to the clipboard.";
      const activeSource = document.querySelector('[data-source-option][aria-pressed="true"]');
      track("install_command_copied", {
        category: "agent_skill",
        product: activeSource?.dataset.sourceOption,
        placement: "skill-installer",
        format: "shell-command",
      });
      copyResetTimer = window.setTimeout(resetCopyFeedback, 3000);
    } catch {
      copyButton.setAttribute("aria-label", "Copy unavailable; select the command manually");
      if (commandStatus) commandStatus.textContent = "Copy unavailable. Select the command manually.";
    }
  });

  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });
})();
