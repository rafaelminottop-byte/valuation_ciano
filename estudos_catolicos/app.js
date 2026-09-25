// ============================================================
//  Estudos Católicos — lógica da interface
// ============================================================
const TEMAS   = window.TEMAS   || [];
const SANTOS  = window.SANTOS  || [];
const QUESTOES = window.QUESTOES || [];

const conteudo = document.getElementById("conteudo");
let modo = "temas";

// --- Navegação por abas ---
document.querySelectorAll(".aba").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".aba").forEach(b => b.classList.remove("ativa"));
    btn.classList.add("ativa");
    modo = btn.dataset.modo;
    render();
  });
});

function esc(s){ return String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

// ---------------------------------------------------------
//  TEMAS
// ---------------------------------------------------------
function renderTemas(){
  const cats = [...new Set(TEMAS.map(t => t.categoria))].sort();
  conteudo.innerHTML = `
    <div class="controles">
      <input class="busca" id="busca" placeholder="Buscar tema, palavra-chave...">
      <select id="filtro">
        <option value="">Todas as categorias</option>
        ${cats.map(c => `<option>${esc(c)}</option>`).join("")}
      </select>
    </div>
    <div class="grid" id="lista"></div>`;
  const busca = document.getElementById("busca");
  const filtro = document.getElementById("filtro");
  const atualiza = () => {
    const q = busca.value.toLowerCase().trim();
    const cat = filtro.value;
    const itens = TEMAS.filter(t => {
      if (cat && t.categoria !== cat) return false;
      if (!q) return true;
      const alvo = (t.titulo + " " + t.resumo + " " + t.corpo.join(" ") + " " + (t.tags||[]).join(" ")).toLowerCase();
      return alvo.includes(q);
    });
    document.getElementById("lista").innerHTML = itens.length ? itens.map(t => `
      <article class="card">
        <span class="tag-topico">${esc(t.categoria)}</span>
        <h3>${esc(t.titulo)}</h3>
        <p class="resumo">${esc(t.resumo)}</p>
        ${t.corpo.map(p => `<p>${esc(p)}</p>`).join("")}
        ${(t.tags&&t.tags.length) ? `<div class="tags">${t.tags.map(x=>`<span>${esc(x)}</span>`).join("")}</div>` : ""}
      </article>`).join("") : `<p class="vazio">Nenhum tema encontrado.</p>`;
  };
  busca.addEventListener("input", atualiza);
  filtro.addEventListener("change", atualiza);
  atualiza();
}

// ---------------------------------------------------------
//  SANTOS
// ---------------------------------------------------------
function renderSantos(){
  conteudo.innerHTML = `
    <div class="controles">
      <input class="busca" id="busca" placeholder="Buscar santo, padroado, palavra-chave...">
    </div>
    <div class="grid" id="lista"></div>`;
  const busca = document.getElementById("busca");
  const atualiza = () => {
    const q = busca.value.toLowerCase().trim();
    const itens = SANTOS.filter(s => {
      if (!q) return true;
      const alvo = (s.nome+" "+s.resumo+" "+s.padroado+" "+s.epoca+" "+s.historia.join(" ")+" "+(s.tags||[]).join(" ")).toLowerCase();
      return alvo.includes(q);
    });
    document.getElementById("lista").innerHTML = itens.length ? itens.map(s => `
      <article class="card">
        <h3>${esc(s.nome)}</h3>
        <p class="resumo">${esc(s.resumo)}</p>
        <div class="meta">
          <span>📅 <b>Festa:</b> ${esc(s.festa)}</span>
          <span>🕰 <b>Época:</b> ${esc(s.epoca)}</span>
          <span>🛡 <b>Padroado:</b> ${esc(s.padroado)}</span>
        </div>
        ${s.historia.map(p => `<p>${esc(p)}</p>`).join("")}
        ${(s.tags&&s.tags.length) ? `<div class="tags">${s.tags.map(x=>`<span>${esc(x)}</span>`).join("")}</div>` : ""}
      </article>`).join("") : `<p class="vazio">Nenhum santo encontrado.</p>`;
  };
  busca.addEventListener("input", atualiza);
  atualiza();
}

// ---------------------------------------------------------
//  QUIZ
// ---------------------------------------------------------
let quiz = null;
function embaralhar(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }

function iniciarQuiz(){
  quiz = { ordem: embaralhar([...Array(QUESTOES.length).keys()]), i: 0, acertos: 0, respondida: false };
  renderQuiz();
}

function renderQuiz(){
  if (!QUESTOES.length){ conteudo.innerHTML = `<p class="vazio">Ainda não há questões cadastradas.</p>`; return; }
  if (!quiz){
    conteudo.innerHTML = `
      <div class="q-card centro">
        <h3>Quiz da Fé Católica</h3>
        <p style="margin:12px 0;color:var(--texto2)">${QUESTOES.length} questões · ordem aleatória</p>
        <button class="btn dourado" id="start">Começar</button>
      </div>`;
    document.getElementById("start").addEventListener("click", iniciarQuiz);
    return;
  }
  if (quiz.i >= quiz.ordem.length){ renderResultado(); return; }

  const q = QUESTOES[quiz.ordem[quiz.i]];
  const prog = Math.round((quiz.i / quiz.ordem.length) * 100);
  conteudo.innerHTML = `
    <div class="barra"><i style="width:${prog}%"></i></div>
    <div class="q-card">
      <div class="q-topo"><span>Questão ${quiz.i+1} de ${quiz.ordem.length}</span><span class="tag-topico">${esc(q.categoria)}</span></div>
      <p class="q-enunciado">${esc(q.enunciado)}</p>
      <div class="alts" id="alts">
        ${q.alternativas.map((a,idx)=>`
          <button class="alt" data-idx="${idx}"><span class="letra">${String.fromCharCode(65+idx)}</span><span>${esc(a)}</span></button>`).join("")}
      </div>
      <div id="feedback"></div>
      <div class="q-nav"><span></span><button class="btn dourado" id="prox" style="display:none">Próxima →</button></div>
    </div>`;

  document.querySelectorAll(".alt").forEach(btn => {
    btn.addEventListener("click", () => {
      if (quiz.respondida) return;
      quiz.respondida = true;
      const idx = +btn.dataset.idx;
      const certo = idx === q.correta;
      if (certo) quiz.acertos++;
      document.querySelectorAll(".alt").forEach(b => {
        b.disabled = true;
        const bi = +b.dataset.idx;
        if (bi === q.correta) b.classList.add("certa");
        else if (bi === idx) b.classList.add("errada");
      });
      document.getElementById("feedback").innerHTML =
        `<div class="explicacao ${certo?"ok":"no"}"><b>${certo?"Correto!":"Ops!"}</b> ${esc(q.explicacao)}</div>`;
      document.getElementById("prox").style.display = "block";
    });
  });
  document.getElementById("prox").addEventListener("click", () => {
    quiz.i++; quiz.respondida = false; renderQuiz();
  });
}

function renderResultado(){
  const total = quiz.ordem.length, ac = quiz.acertos, err = total - ac;
  const pct = Math.round((ac/total)*100);
  conteudo.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${pct}%</b><span>aproveitamento</span></div>
      <div class="stat verde"><b>${ac}</b><span>acertos</span></div>
      <div class="stat vermelho"><b>${err}</b><span>erros</span></div>
    </div>
    <div class="centro"><button class="btn dourado" id="rein">Refazer</button></div>`;
  document.getElementById("rein").addEventListener("click", iniciarQuiz);
}

// ---------------------------------------------------------
function render(){
  if (modo === "temas") renderTemas();
  else if (modo === "santos") renderSantos();
  else if (modo === "quiz"){ quiz = null; renderQuiz(); }
}
render();
