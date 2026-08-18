// ============================================================
// TVK Makkal Sevai — Kavundampalayam :: main.js
// ============================================================

(function () {
  "use strict";

  // ---------- Language toggle ----------
  const LANG_KEY = "tvk_lang";
  function getLang() { return localStorage.getItem(LANG_KEY) || "ta"; }
  function setLang(lang) {
    localStorage.setItem(LANG_KEY, lang);
    applyLang(lang);
  }
  function applyLang(lang) {
    document.querySelectorAll("[data-en][data-ta]").forEach(function (el) {
      el.textContent = lang === "ta" ? el.getAttribute("data-ta") : el.getAttribute("data-en");
    });
    document.querySelectorAll("[data-en-ph][data-ta-ph]").forEach(function (el) {
      el.setAttribute("placeholder", lang === "ta" ? el.getAttribute("data-ta-ph") : el.getAttribute("data-en-ph"));
    });
    document.documentElement.setAttribute("lang", lang === "ta" ? "ta" : "en");
    document.body.classList.toggle("lang-ta", lang === "ta");
    window.__CURRENT_LANG__ = lang;
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyLang(getLang());
    var toggleBtns = [document.getElementById("langToggle"), document.getElementById("langToggleMobile")];
    toggleBtns.forEach(function (btn) {
      if (!btn) return;
      btn.addEventListener("click", function () {
        setLang(getLang() === "ta" ? "en" : "ta");
      });
    });
  });

  // ============================================================
  // Chatbot widget
  // ============================================================
  document.addEventListener("DOMContentLoaded", function () {
    const fab = document.getElementById("chatToggleBtn");
    const panel = document.getElementById("chatPanel");
    const closeBtn = document.getElementById("chatCloseBtn");
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");
    if (!fab) return;

    function addBubble(text, who) {
      const div = document.createElement("div");
      div.className = "chat-bubble " + who;
      div.textContent = text;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    let greeted = false;
    fab.addEventListener("click", function () {
      panel.classList.toggle("d-none");
      if (!greeted && !panel.classList.contains("d-none")) {
        greeted = true;
        const lang = getLang();
        addBubble(
          lang === "ta"
            ? "வணக்கம்! நான் கவுண்டம்பாளையம் மக்கள் சேவை உதவியாளர். புகார் பதிவு, டிக்கெட் நிலை, அலுவலக விவரங்கள் பற்றி கேளுங்கள்."
            : "Vanakkam! I'm the Kavundampalayam Makkal Sevai Assistant. Ask me about filing a complaint, tracking a ticket, or office details.",
          "bot"
        );
      }
    });
    closeBtn.addEventListener("click", function () { panel.classList.add("d-none"); });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      addBubble(text, "user");
      input.value = "";

      fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, lang: getLang() }),
      })
        .then((r) => r.json())
        .then((data) => addBubble(data.reply, "bot"))
        .catch(() => addBubble("Sorry, something went wrong. Please try again or call +91 94422 11117.", "bot"));
    });
  });

  // ============================================================
  // Complaint / Needs form (only present on home page)
  // ============================================================
  document.addEventListener("DOMContentLoaded", function () {
    const formTabs = document.querySelectorAll(".form-tab-btn");
    const panels = document.querySelectorAll(".form-panel");
    if (formTabs.length) {
      formTabs.forEach(function (btn) {
        btn.addEventListener("click", function () {
          formTabs.forEach((b) => b.classList.remove("active"));
          panels.forEach((p) => p.classList.add("d-none"));
          btn.classList.add("active");
          document.getElementById(btn.dataset.target).classList.remove("d-none");
        });
      });
    }

    // Ward -> street population
    document.querySelectorAll(".ward-select").forEach(function (wardSelect) {
      wardSelect.addEventListener("change", function () {
        const form = wardSelect.closest("form");
        const streetSelect = form.querySelector(".street-select");
        const ward = wardSelect.value;
        streetSelect.innerHTML = '<option value="">' + (getLang() === "ta" ? "ஏற்றுகிறது…" : "Loading…") + "</option>";
        if (!ward) { streetSelect.disabled = true; return; }
        fetch("/api/streets/" + encodeURIComponent(ward))
          .then((r) => r.json())
          .then((data) => {
            streetSelect.innerHTML = '<option value="">' + (getLang() === "ta" ? "— தெரு தேர்ந்தெடுக்கவும் —" : "— Select street —") + "</option>";
            data.streets.forEach(function (s) {
              const opt = document.createElement("option");
              opt.value = s; opt.textContent = s;
              streetSelect.appendChild(opt);
            });
            const other = document.createElement("option");
            other.value = "__other__";
            other.textContent = getLang() === "ta" ? "என் தெரு பட்டியலில் இல்லை" : "My street isn't listed";
            streetSelect.appendChild(other);
            streetSelect.disabled = false;
          });
      });
    });

    // Geolocation "Use My Location"
    document.querySelectorAll(".btn-locate").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const form = btn.closest("form");
        const latInput = form.querySelector(".gps-lat");
        const lngInput = form.querySelector(".gps-lng");
        const statusEl = form.querySelector(".gps-status");
        if (!navigator.geolocation) {
          statusEl.textContent = getLang() === "ta" ? "இந்த உலாவி இருப்பிடத்தை ஆதரிக்கவில்லை." : "Your browser does not support location.";
          return;
        }
        statusEl.textContent = getLang() === "ta" ? "இருப்பிடம் பெறப்படுகிறது…" : "Getting location…";
        navigator.geolocation.getCurrentPosition(
          function (pos) {
            latInput.value = pos.coords.latitude;
            lngInput.value = pos.coords.longitude;
            btn.classList.add("located");
            statusEl.innerHTML = '<i class="bi bi-check-circle-fill text-success me-1"></i>' + (getLang() === "ta" ? "இருப்பிடம் பதிவு செய்யப்பட்டது" : "Location captured");
          },
          function () {
            statusEl.textContent = getLang() === "ta" ? "இருப்பிடத்தை பெற முடியவில்லை. மீண்டும் முயற்சிக்கவும்." : "Could not get location. Please try again.";
          }
        );
      });
    });

    // Submit handlers
    document.querySelectorAll(".tvk-form").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const submitBtn = form.querySelector("button[type=submit]");
        const original = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.textContent = getLang() === "ta" ? "சமர்ப்பிக்கிறது…" : "Submitting…";

        const fd = new FormData(form);
        const payload = {};
        fd.forEach((v, k) => (payload[k] = v));
        payload.mode = form.dataset.mode;

        fetch("/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })
          .then((r) => r.json())
          .then((data) => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = original;
            if (data.error) {
              alert(data.error);
              return;
            }
            const modalEl = document.getElementById("receiptModal");
            document.getElementById("receiptTicketId").textContent = data.ticket_id;
            document.getElementById("receiptPriority").textContent = data.priority;
            document.getElementById("receiptExpected").textContent = data.expected_resolution;
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
            form.reset();
          })
          .catch(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = original;
            alert("Something went wrong. Please try again.");
          });
      });
    });
  });

  // ============================================================
  // Track page
  // ============================================================
  document.addEventListener("DOMContentLoaded", function () {
    const trackForm = document.getElementById("trackForm");
    if (!trackForm) return;
    trackForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const id = document.getElementById("trackInput").value.trim();
      const resultBox = document.getElementById("trackResult");
      const notFoundBox = document.getElementById("trackNotFound");
      resultBox.classList.add("d-none");
      notFoundBox.classList.add("d-none");
      if (!id) return;

      fetch("/api/track/" + encodeURIComponent(id))
        .then((r) => {
          if (!r.ok) throw new Error("not found");
          return r.json();
        })
        .then((t) => {
          document.getElementById("resTicketId").textContent = t.ticket_id;
          document.getElementById("resName").textContent = t.name;
          document.getElementById("resSubject").textContent = t.subject || t.category || "-";
          document.getElementById("resStatus").textContent = t.status.replace("_", " ").toUpperCase();
          document.getElementById("resPriority").textContent = t.priority;
          document.getElementById("resExpected").textContent = t.expected_resolution;

          const timelineBox = document.getElementById("resTimeline");
          timelineBox.innerHTML = "";
          t.timeline.forEach(function (item, idx) {
            const isLast = idx === t.timeline.length - 1;
            const row = document.createElement("div");
            row.className = "d-flex gap-3";
            row.innerHTML =
              '<div class="d-flex flex-column align-items-center">' +
              '<div class="timeline-dot"></div>' +
              (isLast ? "" : '<div class="timeline-line"></div>') +
              "</div>" +
              '<div class="pb-3">' +
              '<div class="fw-bold">' + (getLang() === "ta" ? item.label_ta : item.label_en) + "</div>" +
              '<div class="small text-muted">' + item.at + " · " + item.by + "</div>" +
              "</div>";
            timelineBox.appendChild(row);
          });

          resultBox.classList.remove("d-none");
        })
        .catch(() => notFoundBox.classList.remove("d-none"));
    });
  });
})();
