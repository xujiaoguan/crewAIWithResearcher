(function () {
  const $ = (sel) => document.querySelector(sel);

  function formatDetail(d) {
    if (typeof d === "string") return d;
    if (Array.isArray(d))
      return d.map((x) => (x && x.msg) || JSON.stringify(x)).join("；");
    if (d && typeof d === "object") return JSON.stringify(d);
    return String(d);
  }

  const topicEl = $("#topic");
  const btn = $("#run");
  const statusEl = $("#status");
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");
  const mdEl = $("#md-preview");
  const rawEl = $("#raw-out");
  const notesEl = $("#notes-preview");
  const linksEl = $("#links");

  function setStatus(kind, text) {
    statusEl.className = "status visible " + (kind || "info");
    statusEl.textContent = text;
  }

  function hideStatus() {
    statusEl.className = "status";
    statusEl.textContent = "";
  }

  function activateTab(name) {
    tabs.forEach((t) => {
      t.classList.toggle("active", t.dataset.tab === name);
    });
    panels.forEach((p) => {
      p.classList.toggle("active", p.dataset.panel === name);
    });
  }

  tabs.forEach((t) => {
    t.addEventListener("click", () => activateTab(t.dataset.tab));
  });

  async function loadMarkdown(name, el, useMarked) {
    const r = await fetch("/api/output/" + encodeURIComponent(name));
    if (!r.ok) {
      el.innerHTML =
        '<p class="muted">暂无文件（请先生成一次）或文件读取失败：' +
        r.status +
        "</p>";
      return;
    }
    const txt = await r.text();
    if (useMarked && window.marked && typeof marked.parse === "function") {
      el.innerHTML = '<div class="markdown">' + marked.parse(txt) + "</div>";
    } else {
      el.innerHTML = "<pre class=\"raw\"></pre>";
      el.querySelector("pre").textContent = txt;
    }
  }

  async function refreshOutputs() {
    await loadMarkdown("report.md", mdEl, true);
    await loadMarkdown("research_notes.md", notesEl, true);
  }

  btn.addEventListener("click", async () => {
    const topic = (topicEl.value || "").trim();
    if (!topic) {
      setStatus("err", "请先填写研究主题或论文选题。");
      return;
    }
    btn.disabled = true;
    hideStatus();
    setStatus("info", "正在运行 Crew（可能需要数分钟），请耐心等待…");
    rawEl.textContent = "";
    mdEl.innerHTML = "";
    notesEl.innerHTML = "";
    linksEl.innerHTML = "";

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const rawText = await res.text();
      let data = {};
      try {
        data = rawText ? JSON.parse(rawText) : {};
      } catch (_) {
        data = { detail: rawText.slice(0, 800) };
      }
      if (!res.ok) {
        setStatus(
          "err",
          formatDetail(data.detail) || data.message || "请求失败 " + res.status
        );
        return;
      }
      setStatus("ok", data.message || "生成完成。");
      rawEl.textContent = data.result || "";
      await refreshOutputs();
      linksEl.innerHTML =
        '<a href="/api/output/report.pdf" target="_blank" rel="noopener">下载 report.pdf</a>' +
        '<a href="/api/output/report.md" target="_blank" rel="noopener">打开 report.md</a>' +
        '<a href="/api/output/research_notes.md" target="_blank" rel="noopener">打开 research_notes.md</a>';
      activateTab("report");
    } catch (e) {
      setStatus("err", String(e.message || e));
    } finally {
      btn.disabled = false;
    }
  });

  $("#refresh-files").addEventListener("click", () => {
    refreshOutputs();
    setStatus("ok", "已从磁盘重新加载 Markdown。");
  });

  // 初次进入尝试加载已有产物
  refreshOutputs().catch(() => {});
})();
