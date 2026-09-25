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

function render() {
  if (modo === "feed") renderFeed(); else renderGestoras();
}

document.querySelectorAll(".aba").forEach(aba => {
  aba.addEventListener("click", () => {
    document.querySelectorAll(".aba").forEach(a => a.classList.remove("ativa"));
    aba.classList.add("ativa");
    modo = aba.getAttribute("data-modo");
    render();
  });
});

render();
