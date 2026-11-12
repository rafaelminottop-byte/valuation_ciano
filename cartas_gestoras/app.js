const CARTAS = (window.CARTAS || []).slice().sort((a, b) => (b.data || "").localeCompare(a.data || ""));
const GESTORAS = window.GESTORAS || [];
const conteudo = document.getElementById("conteudo");

const LIDAS_KEY = "cartas_lidas_v1";
function getLidas() {
  try { return JSON.parse(localStorage.getItem(LIDAS_KEY) || "{}"); } catch { return {}; }
}
function setLida(id, valor) {
  const l = getLidas();
  if (valor) l[id] = true; else delete l[id];
  try { localStorage.setItem(LIDAS_KEY, JSON.stringify(l)); } catch {}
}

let modo = "feed";
let filtroTexto = "";
let filtroCat = "";
let filtroLidas = "todas";

function fmtData(iso) {
  if (!iso) return "";
  const [a, m, d] = iso.split("-");
  return `${d}/${m}/${a}`;
}

function esc(s) {
  return String(s || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function renderFeed() {
  const lidas = getLidas();
  const cats = [...new Set(CARTAS.map(c => c.categoria).filter(Boolean))].sort();
  let lista = CARTAS.filter(c => {
    if (filtroCat && c.categoria !== filtroCat) return false;
    const estaLida = !!lidas[c.id];
    if (filtroLidas === "lidas" && !estaLida) return false;
    if (filtroLidas === "nao" && estaLida) return false;
    if (filtroTexto) {
      const blob = `${c.gestora} ${c.titulo} ${c.tese} ${(c.bullets || []).join(" ")} ${(c.tags || []).join(" ")} ${(c.ativos || []).join(" ")}`.toLowerCase();
      if (!blob.includes(filtroTexto.toLowerCase())) return false;
    }
    return true;
  });

  const naoLidas = CARTAS.filter(c => !lidas[c.id]).length;

  let html = `
    <div class="controles">
      <input class="busca" id="busca" placeholder="Buscar por gestora, tema, ativo…" value="${esc(filtroTexto)}">
      <select id="fcat">
        <option value="">Todas as categorias</option>
        ${cats.map(c => `<option value="${esc(c)}" ${c === filtroCat ? "selected" : ""}>${esc(c)}</option>`).join("")}
      </select>
      <select id="flidas">
        <option value="todas" ${filtroLidas === "todas" ? "selected" : ""}>Todas</option>
        <option value="nao" ${filtroLidas === "nao" ? "selected" : ""}>Não lidas</option>
        <option value="lidas" ${filtroLidas === "lidas" ? "selected" : ""}>Lidas</option>
      </select>
    </div>
    <div class="contador">${lista.length} carta(s) · ${naoLidas} não lida(s) de ${CARTAS.length}</div>
  `;

  if (!lista.length) {
    html += `<div class="vazio">Nenhuma carta encontrada com esses filtros.</div>`;
  } else {
    html += lista.map(c => {
      const estaLida = !!lidas[c.id];
      return `
        <article class="carta ${estaLida ? "lida" : ""}" data-id="${esc(c.id)}">
          <div class="carta-topo">
            <span class="carta-gestora">🏦 ${esc(c.gestora)}
              ${c.categoria ? `<span class="pill cat">${esc(c.categoria)}</span>` : ""}
            </span>
            <span class="carta-data">${fmtData(c.data)}</span>
          </div>
          <h3>${esc(c.titulo)}</h3>
          ${c.tese ? `<p class="tese">${esc(c.tese)}</p>` : ""}
          <ul>${(c.bullets || []).map(b => `<li>${esc(b)}</li>`).join("")}</ul>
          ${(c.ativos && c.ativos.length) ? `<div class="ativos"><b>Ativos citados:</b> ${c.ativos.map(esc).join(" · ")}</div>` : ""}
          ${(c.tags && c.tags.length) ? `<div class="meta-linha">${c.tags.map(t => `<span class="tag">#${esc(t)}</span>`).join("")}</div>` : ""}
          <div class="carta-acoes">
            <button class="btn btn-marcar" data-marcar="${esc(c.id)}">${estaLida ? "✓ Lida" : "Marcar como lida"}</button>
            ${c.url ? `<a class="link-pdf" href="${esc(c.url)}" target="_blank" rel="noopener">📄 Abrir carta original (PDF)</a>` : ""}
          </div>
        </article>`;
    }).join("");
  }

  conteudo.innerHTML = html;

  document.getElementById("busca").addEventListener("input", e => { filtroTexto = e.target.value; renderFeed(); });
  document.getElementById("fcat").addEventListener("change", e => { filtroCat = e.target.value; renderFeed(); });
  document.getElementById("flidas").addEventListener("change", e => { filtroLidas = e.target.value; renderFeed(); });
  conteudo.querySelectorAll("[data-marcar]").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-marcar");
      setLida(id, !getLidas()[id]);
      renderFeed();
    });
  });
  // reposiciona cursor no fim da busca
  const b = document.getElementById("busca");
  if (b && document.activeElement !== b && filtroTexto) { b.focus(); b.setSelectionRange(b.value.length, b.value.length); }
}

function renderGestoras() {
  const porGestora = {};
  CARTAS.forEach(c => { porGestora[c.gestora] = (porGestora[c.gestora] || 0) + 1; });
  const html = `
    <div class="contador">${GESTORAS.length} gestoras no catálogo</div>
    <div class="grid-gestoras">
      ${GESTORAS.map(g => `
        <div class="gestora-card">
          <h3>${esc(g.nome)}</h3>
          <div class="info">${esc(g.categoria)} · ${esc(g.freq)}</div>
          ${porGestora[g.nome] ? `<div class="n-cartas">📬 ${porGestora[g.nome]} carta(s) no feed</div>` : `<div class="info">— sem cartas ainda</div>`}
          <div style="margin-top:8px"><a href="${esc(g.pagina)}" target="_blank" rel="noopener">Ver cartas no site →</a></div>
        </div>
      `).join("")}
    </div>`;
  conteudo.innerHTML = html;
}

// Cartas citadas por um tema (ids em t.fontes -> CARTAS)
function panoCartas(t) {
  return (t.fontes || []).map(id => (window.CARTAS || []).find(c => c.id === id)).filter(Boolean);
}
// Selo de força: quantas gestoras diferentes falaram do tema
function panoForca(t) {
  const n = new Set(panoCartas(t).map(c => c.gestora)).size;
  if (!n) return "";
  const [cls, txt] = n >= 3 ? ["forte", "Consenso forte"] : n === 2 ? ["medio", "Duas casas"] : ["fraco", "Uma casa só"];
  return `<div class="pano-forca ${cls}">${txt} · ${n} gestora${n > 1 ? "s" : ""}</div>`;
}
function panoFontes(t) {
  const cs = panoCartas(t);
  if (!cs.length) return "";
  return `<details class="pano-fontes"><summary>Ler nas cartas (${cs.length})</summary>${cs.map(c =>
    `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.gestora)} · ${esc(c.data.split("-").reverse().join("/"))} — ${esc(c.titulo)}</a>`).join("")}</details>`;
}
function panoTexto(p) {
  return [p.periodo, "", p.destaque, ""].concat(p.temas.map((t, i) => `${i + 1}. ${t.titulo}\n${t.resumo}\nQuem falou: ${(t.gestoras || []).join(", ")}\n`))
    .concat(["Síntese das visões dos gestores nas últimas cartas — não é recomendação de investimento."]).join("\n");
}

function renderPanorama() {
  const p = window.PANORAMA;
  if (!p) { conteudo.innerHTML = `<div class="vazio">Panorama ainda não gerado.</div>`; return; }
  conteudo.innerHTML = `
    <div class="pano-destaque">
      <div class="pano-periodo">📊 ${esc(p.periodo || "Panorama")}</div>
      <p>${esc(p.destaque)}</p>
    </div>
    ${(p.consenso && p.consenso.length) ? `
    <h3 class="pano-sec">📐 Consenso das gestoras</h3>
    <div class="consenso">
      ${p.consenso.map(c => {
        const d = c.dir === "alta" ? { s: "▲", cls: "up", t: "Alta" }
               : c.dir === "queda" ? { s: "▼", cls: "down", t: "Queda" }
               : { s: "▬", cls: "flat", t: "Lateral" };
        return `<div class="cons-row">
          <div class="cons-ind">${esc(c.indicador)}</div>
          <div class="cons-dir ${d.cls}" title="${d.t}">${d.s}</div>
          <div class="cons-vis">${esc(c.visao)}<span class="cons-ges">${c.gestoras.map(esc).join(" · ")}</span></div>
        </div>`;
      }).join("")}
    </div>
    <p class="pano-aviso">Direção da visão predominante nas cartas (não são previsões numéricas nossas).</p>
    <h3 class="pano-sec">🧩 Principais temas</h3>` : ""}
    <div class="pano-grid">
      ${p.temas.map((t, i) => `
        <article class="pano-card">
          <div class="pano-topo"><span class="pano-emoji">${esc(t.emoji || "•")}</span>
            <h3>${esc(t.titulo)}</h3><span class="pano-num">${i + 1}</span></div>
          <p class="pano-resumo">${esc(t.resumo)}</p>
          ${panoForca(t)}
          ${t.nota ? `<p class="pano-nota">${esc(t.nota)}</p>` : ""}
          ${(t.gestoras && t.gestoras.length) ? `<div class="meta-linha">${t.gestoras.map(g => `<span class="tag">${esc(g)}</span>`).join("")}</div>` : ""}
          ${panoFontes(t)}
        </article>`).join("")}
    </div>
    <div class="pano-acoes"><button class="aba" id="btn-copiar-pano">📋 Copiar resumo em texto</button><span id="pano-copiado" class="pano-copiado" hidden>Copiado!</span></div>
    <p class="pano-rodape">Síntese das visões dos gestores nas últimas cartas — não é recomendação de investimento. Atualizado em ${esc((p.atualizadoEm||"").split("-").reverse().join("/"))}.</p>`;
}

document.addEventListener("click", e => {
  if (e.target.id !== "btn-copiar-pano" || !window.PANORAMA) return;
  const ok = () => { const m = document.getElementById("pano-copiado"); m.hidden = false; setTimeout(() => m.hidden = true, 1800); };
  navigator.clipboard.writeText(panoTexto(window.PANORAMA)).then(ok).catch(() => {});
});

function render() {
  if (modo === "feed") renderFeed();
  else if (modo === "panorama") renderPanorama();
  else renderGestoras();
}

document.querySelectorAll(".aba[data-modo]").forEach(aba => {
  aba.addEventListener("click", () => {
    document.querySelectorAll(".aba[data-modo]").forEach(a => a.classList.remove("ativa"));
    aba.classList.add("ativa");
    modo = aba.getAttribute("data-modo");
    render();
  });
});

// Botão "Atualizar cartas": copia o comando e mostra um aviso rápido (sem tela cheia)
let toastTimer = null;
function mostrarToast(html) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.innerHTML = html;
  t.hidden = false;
  t.classList.add("ver");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.classList.remove("ver"); setTimeout(() => t.hidden = true, 300); }, 6000);
}
document.getElementById("btn-atualizar")?.addEventListener("click", () => {
  const cmd = "py atualizar.py";
  const feito = () => mostrarToast(`✅ <b>Comando copiado!</b> Cole no terminal e aperte Enter — ou dê 2 cliques em <code>Atualizar_Cartas.bat</code>. Depois é só recarregar (F5).`);
  if (navigator.clipboard) {
    navigator.clipboard.writeText(cmd).then(feito).catch(() => mostrarToast(`Para atualizar, rode <code>${cmd}</code> ou o <code>Atualizar_Cartas.bat</code>.`));
  } else {
    mostrarToast(`Para atualizar, rode <code>${cmd}</code> ou o <code>Atualizar_Cartas.bat</code>.`);
  }
});

render();
