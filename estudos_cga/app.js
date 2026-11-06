// ============================================================
//  Central de Estudos CGA - lógica da interface
// ============================================================
const FORMULAS = window.FORMULAS || [];
const QUESTOES = window.QUESTOES || [];
const CONCEITOS = window.CONCEITOS || [];
const conteudo = document.getElementById("conteudo");

// tópicos únicos (ordenados)
const topicos = [...new Set([...FORMULAS.map(f => f.topico), ...QUESTOES.map(q => q.topico)])].sort();

// progresso persistente (localStorage)
const PROG_KEY = "cga_progresso_v1";
function lerProg(){ try{ return JSON.parse(localStorage.getItem(PROG_KEY)) || {}; }catch(e){ return {}; } }
function salvarProg(p){ localStorage.setItem(PROG_KEY, JSON.stringify(p)); }
function registrar(topico, acertou){
  const p = lerProg();
  p[topico] = p[topico] || { total:0, acertos:0 };
  p[topico].total++;
  if(acertou) p[topico].acertos++;
  salvarProg(p);
}

// caderno de erros (questões que o usuário errou) - persistente
const ERROS_KEY = "cga_erros_v1";
function chaveQ(q){ // id estável a partir do enunciado (sem depender de índice)
  const s = q.enunciado || "";
  let h = 0;
  for(let i=0;i<s.length;i++){ h = (h*31 + s.charCodeAt(i)) | 0; }
  return "q" + (h >>> 0).toString(36);
}
function lerErros(){ try{ return JSON.parse(localStorage.getItem(ERROS_KEY)) || {}; }catch(e){ return {}; } }
function salvarErros(m){ localStorage.setItem(ERROS_KEY, JSON.stringify(m)); }
// marca (errou=true adiciona) ou remove (acertou => tira da lista) uma questão do caderno de erros
function marcarErro(q, errou){
  const m = lerErros();
  const k = chaveQ(q);
  if(errou) m[k] = { t: q.topico };
  else delete m[k];
  salvarErros(m);
}
function poolErros(){ const m = lerErros(); return QUESTOES.filter(q => m[chaveQ(q)]); }
function contarErros(){ return Object.keys(lerErros()).length; }

// ============================================================
//  BLOCOS OFICIAIS DA PROVA CGA (espelho da prova real)
//  Mapeia os tópicos internos para os 5 blocos oficiais e seus
//  pesos reais (nº de questões na prova de 45).
// ============================================================
const BLOCOS = {
  "Gestão de Investimentos e de Risco": ["Estatística e Risco", "Risco de Crédito", "Derivativos", "Finanças", "Economia"],
  "Avaliação de Desempenho":            ["Performance e Risco"],
  "Gestão de Carteiras - Renda Fixa":   ["Renda Fixa"],
  "Gestão de Carteiras - Renda Variável":["Renda Variável"],
  "Investimentos no Exterior, Legislação e Tributação": ["Regulação e Fundos", "Ética e Regulação", "ESG", "Tributação", "Investimentos no Exterior"],
};
const PESO_BLOCO = { // nº de questões de cada bloco na prova real (total 45)
  "Gestão de Investimentos e de Risco": 6,
  "Avaliação de Desempenho": 6,
  "Gestão de Carteiras - Renda Fixa": 10,
  "Gestão de Carteiras - Renda Variável": 8,
  "Investimentos no Exterior, Legislação e Tributação": 15,
};
const ORDEM_BLOCO = Object.keys(PESO_BLOCO);
function blocoDe(topico){
  for(const [b, ts] of Object.entries(BLOCOS)) if(ts.includes(topico)) return b;
  return "Outros";
}
// desempenho acumulado por bloco (a partir do progresso por tópico)
function progressoPorBloco(){
  const p = lerProg();
  const porBloco = {};
  ORDEM_BLOCO.forEach(b => porBloco[b] = { total:0, acertos:0 });
  Object.entries(p).forEach(([t, d]) => {
    const b = blocoDe(t);
    if(!porBloco[b]) porBloco[b] = { total:0, acertos:0 };
    porBloco[b].total += d.total; porBloco[b].acertos += d.acertos;
  });
  return porBloco;
}
// blocos onde o aproveitamento está abaixo da meta (default 70%); sem histórico = considerado fraco
function blocosFracos(meta=70){
  const pb = progressoPorBloco();
  return ORDEM_BLOCO.filter(b => {
    const d = pb[b]; if(!d || d.total < 3) return true; // pouco dado = ainda precisa treinar
    return (d.acertos/d.total*100) < meta;
  });
}

// histórico de simulados concluídos (para evolução e ritmo)
const HIST_KEY = "cga_simulados_v1";
function lerHist(){ try{ return JSON.parse(localStorage.getItem(HIST_KEY)) || []; }catch(e){ return []; } }
function salvarSimuladoHist(reg){
  const h = lerHist(); h.push(reg);
  try{ localStorage.setItem(HIST_KEY, JSON.stringify(h.slice(-100))); }catch(e){}
}

// sessão em andamento (retomar de onde parou)
const SESS_KEY = "cga_sessao_v1"; // { tipo:'quiz'|'sim', estado:{...} }
function salvarSessao(tipo, estado){
  try{ localStorage.setItem(SESS_KEY, JSON.stringify({ tipo, estado })); }catch(e){}
}
function lerSessao(tipo){
  try{ const s = JSON.parse(localStorage.getItem(SESS_KEY)); return (s && s.tipo===tipo) ? s.estado : null; }catch(e){ return null; }
}
function limparSessao(){ localStorage.removeItem(SESS_KEY); }
function avisoRetomar(tipo, estado){
  const total = estado.pool.length;
  const respondidas = estado.respostas.filter(r => r!==null && r!==undefined).length;
  const label = tipo==="sim" ? "simulado" : "quiz";
  return `<div class="card" style="border-color:var(--ciano);border-width:2px">
    <span class="tag-topico">↩ Sessão salva</span>
    <h3 style="margin:10px 0 6px">Você tem um ${label} em andamento</h3>
    <p class="desc">Questão ${estado.i+1} de ${total} · ${respondidas} respondida(s)${tipo==="sim"?` · ${fmtTempo(estado.restante)} restantes`:""}.</p>
    <div style="margin-top:12px;display:flex;gap:10px">
      <button class="btn ciano" id="retomar">↩ Continuar de onde parei</button>
      <button class="btn" id="descartar">Recomeçar do zero</button>
    </div>
  </div>`;
}

// navegação por abas
document.querySelectorAll(".aba").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".aba").forEach(b => b.classList.remove("ativa"));
    btn.classList.add("ativa");
    render(btn.dataset.modo);
  });
});

function opcoesTopico(sel){
  return `<option value="">Todos os tópicos</option>` +
    topicos.map(t => `<option value="${t}" ${t===sel?"selected":""}>${t}</option>`).join("");
}

function render(modo){
  clearInterval(simTimer); // para o cronômetro do simulado ao trocar de tela (a sessão fica salva)
  if(modo === "formulas") return renderFormulas();
  if(modo === "conceitos") return renderConceitos();
  if(modo === "quiz") return renderQuiz();
  if(modo === "simulado") return renderSimulado();
  if(modo === "progresso") return renderProgresso();
}

// ---------------- FÓRMULAS ----------------
function renderFormulas(){
  conteudo.innerHTML = `
    <div class="controles">
      <input class="busca" id="busca" placeholder="🔎 Buscar fórmula, conceito ou palavra-chave...">
      <select id="filtro">${opcoesTopico("")}</select>
    </div>
    <div class="grid" id="lista"></div>`;
  const busca = document.getElementById("busca");
  const filtro = document.getElementById("filtro");
  function atualizar(){
    const q = busca.value.toLowerCase().trim();
    const t = filtro.value;
    const res = FORMULAS.filter(f => {
      const okT = !t || f.topico === t;
      const texto = (f.titulo+" "+f.formula+" "+f.descricao+" "+(f.tags||[]).join(" ")).toLowerCase();
      const okQ = !q || texto.includes(q);
      return okT && okQ;
    });
    document.getElementById("lista").innerHTML = res.length ? res.map(cardFormula).join("") :
      `<div class="vazio">Nenhum resultado. Adicione mais conteúdo em <code>dados/formulas.js</code>.</div>`;
  }
  busca.addEventListener("input", atualizar);
  filtro.addEventListener("change", atualizar);
  atualizar();
  busca.focus();
}
function cardFormula(f){
  return `<div class="card">
    <span class="tag-topico">${f.topico}</span>
    <h3>${f.titulo}</h3>
    <div class="formula">${f.formula}</div>
    <p class="desc">${f.descricao}</p>
    <div class="tags">${(f.tags||[]).map(t=>`<span>${t}</span>`).join("")}</div>
  </div>`;
}

// ---------------- CONCEITOS (destrinchados) ----------------
function renderConceitos(){
  const topsC = [...new Set(CONCEITOS.map(c => c.topico))].sort();
  conteudo.innerHTML = `
    <div class="controles">
      <input class="busca" id="buscaC" placeholder="🔎 Buscar conceito, tema ou palavra-chave...">
      <select id="filtroC">
        <option value="">Todos os tópicos</option>
        ${topsC.map(t => `<option value="${t}">${t}</option>`).join("")}
      </select>
    </div>
    <div class="grid" id="listaC"></div>`;
  const busca = document.getElementById("buscaC");
  const filtro = document.getElementById("filtroC");
  function atualizar(){
    const q = busca.value.toLowerCase().trim();
    const t = filtro.value;
    const res = CONCEITOS.filter(c => {
      const okT = !t || c.topico === t;
      const texto = (c.titulo+" "+(c.resumo||"")+" "+(c.tags||[]).join(" ")).toLowerCase();
      const okQ = !q || texto.includes(q);
      return okT && okQ;
    });
    document.getElementById("listaC").innerHTML = res.length ? res.map(cardConceito).join("") :
      `<div class="vazio">Nenhum conceito. Adicione mais em <code>dados/conceitos.js</code>.</div>`;
    document.querySelectorAll(".conc-card .conc-topo").forEach(h => {
      h.addEventListener("click", () => h.parentElement.classList.toggle("aberto"));
    });
  }
  busca.addEventListener("input", atualizar);
  filtro.addEventListener("change", atualizar);
  atualizar();
  busca.focus();
}
function cardConceito(c){
  return `<div class="conc-card aberto">
    <div class="conc-topo">
      <div>
        <span class="tag-topico">${c.topico}</span>
        <h3>${c.titulo}</h3>
        <p class="desc">${c.resumo||""}</p>
      </div>
      <span class="conc-seta">▾</span>
    </div>
    <div class="conc-corpo">${c.html||""}</div>
  </div>`;
}

// ---------------- QUIZ ----------------
let quizEstado = null;
function renderQuiz(){
  const nErros = contarErros();
  conteudo.innerHTML = `
    <div class="controles">
      <select id="filtroQuiz">${opcoesTopico("")}</select>
      <label class="check-erros" title="${nErros ? "Refaz apenas as questões que você errou. Acertar aqui remove a questão do caderno de erros." : "Você ainda não tem erros registrados. Faça um quiz ou simulado primeiro."}">
        <input type="checkbox" id="soErros" ${nErros ? "" : "disabled"}>
        <span>📕 Só questões que errei (<b id="cErros">${nErros}</b>)</span>
      </label>
      <button class="btn ciano" id="iniciar">Iniciar quiz ▶</button>
      ${nErros ? `<button class="btn" id="limparErros" title="Esvazia o caderno de erros">Limpar erros</button>` : ""}
    </div>
    <div id="areaQuiz"></div>`;
  document.getElementById("iniciar").addEventListener("click", () => {
    const t = document.getElementById("filtroQuiz").value;
    const soErros = document.getElementById("soErros").checked;
    let base = soErros ? poolErros() : QUESTOES;
    let pool = base.filter(q => !t || q.topico === t);
    if(!pool.length){
      alert(soErros
        ? "Nenhuma questão errada" + (t ? " nesse tópico." : " registrada. Faça um quiz ou simulado primeiro.")
        : "Sem questões para esse tópico ainda.");
      return;
    }
    pool = embaralhar(pool);
    quizEstado = { pool, i:0, acertos:0, respondida:false, respostas:new Array(pool.length).fill(null) };
    limparSessao();
    mostrarQuestao();
  });
  const btnLimpar = document.getElementById("limparErros");
  if(btnLimpar) btnLimpar.addEventListener("click", () => {
    if(confirm("Esvaziar o caderno de erros? Isso apaga a lista de questões que você errou.")){
      localStorage.removeItem(ERROS_KEY); renderQuiz();
    }
  });

  // sessão salva de um quiz anterior?
  const salva = lerSessao("quiz");
  const area = document.getElementById("areaQuiz");
  if(salva){
    area.innerHTML = avisoRetomar("quiz", salva);
    document.getElementById("retomar").onclick = () => {
      quizEstado = salva; quizEstado.respondida = false; mostrarQuestao();
    };
    document.getElementById("descartar").onclick = () => { limparSessao(); area.innerHTML = `<div class="vazio">Escolha um tópico (ou todos) e clique em iniciar.</div>`; };
  } else {
    area.innerHTML = `<div class="vazio">Escolha um tópico (ou todos) e clique em iniciar.</div>`;
  }
}
function mostrarQuestao(){
  const e = quizEstado;
  salvarSessao("quiz", e);
  const q = e.pool[e.i];
  const pct = Math.round((e.i / e.pool.length) * 100);
  document.getElementById("areaQuiz").innerHTML = `
    <div class="barra"><i style="width:${pct}%"></i></div>
    <div class="q-card">
      <div class="q-topo"><span>Questão ${e.i+1} de ${e.pool.length}</span><span class="tag-topico">${q.topico}</span></div>
      <div class="q-enunciado">${q.enunciado}</div>
      <div class="alts" id="alts">
        ${q.alternativas.map((a,idx)=>`<button class="alt" data-idx="${idx}"><span class="letra">${"ABCDE"[idx]}</span><span>${a}</span></button>`).join("")}
      </div>
      <div id="feedback"></div>
      <div class="q-nav">
        <span></span>
        <button class="btn" id="prox" style="display:none">Próxima ▶</button>
      </div>
    </div>`;
  document.querySelectorAll("#alts .alt").forEach(btn => {
    btn.addEventListener("click", () => responder(parseInt(btn.dataset.idx)));
  });
}
function responder(idx){
  const e = quizEstado;
  if(e.respondida) return;
  e.respondida = true;
  const q = e.pool[e.i];
  const acertou = idx === q.correta;
  if(acertou) e.acertos++;
  e.respostas[e.i] = idx;
  registrar(q.topico, acertou);
  marcarErro(q, !acertou); // acertou remove do caderno; errou adiciona
  salvarSessao("quiz", e);
  document.querySelectorAll("#alts .alt").forEach(btn => {
    const i = parseInt(btn.dataset.idx);
    btn.disabled = true;
    if(i === q.correta) btn.classList.add("certa");
    else if(i === idx) btn.classList.add("errada");
  });
  document.getElementById("feedback").innerHTML =
    `<div class="explicacao ${acertou?"ok":"no"}">
      <b>${acertou?"✓ Correto!":"✗ Incorreto."}</b> ${q.explicacao}
    </div>${htmlMacete(q)}`;
  const prox = document.getElementById("prox");
  prox.style.display = "inline-block";
  prox.textContent = e.i < e.pool.length-1 ? "Próxima ▶" : "Ver resultado ▶";
  prox.onclick = () => {
    e.i++;
    if(e.i < e.pool.length){ e.respondida = false; mostrarQuestao(); }
    else resultadoQuiz();
  };
}
function resultadoQuiz(){
  const e = quizEstado;
  limparSessao();
  const pct = Math.round((e.acertos / e.pool.length) * 100);
  document.getElementById("areaQuiz").innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${e.pool.length}</b><span>Questões</span></div>
      <div class="stat verde"><b>${e.acertos}</b><span>Acertos</span></div>
      <div class="stat vermelho"><b>${e.pool.length-e.acertos}</b><span>Erros</span></div>
      <div class="stat"><b>${pct}%</b><span>Aproveitamento</span></div>
    </div>
    <div class="centro" id="acoesResultado">
      <button class="btn" onclick="revisar(quizEstado,'erros')">📝 Revisar erros</button>
      <button class="btn" onclick="revisar(quizEstado,'todas')">Ver gabarito completo</button>
      <button class="btn ciano" onclick="render('quiz')">Novo quiz ▶</button>
    </div>
    <div id="areaRevisao"></div>`;
}

// ---------------- REVISÃO (gabarito comentado) ----------------
// Reutilizada por quiz e simulado. estado = { pool, respostas }
function revisar(estado, modo){
  const alvo = document.getElementById("areaRevisao");
  const itens = estado.pool.map((q,idx) => ({q, dada:estado.respostas[idx], acertou:estado.respostas[idx]===q.correta}));
  const lista = modo === "erros" ? itens.filter(x => !x.acertou) : itens;
  if(!lista.length){
    alvo.innerHTML = `<div class="vazio">🎉 Você não errou nenhuma! Nada para revisar.</div>`;
    return;
  }
  const titulo = modo === "erros" ? `Revisão dos erros (${lista.length})` : `Gabarito comentado (${lista.length} questões)`;
  alvo.innerHTML = `<h3 style="margin:22px 0 12px">${titulo}</h3>` + lista.map(x => cardRevisao(x)).join("");
  alvo.scrollIntoView({behavior:"smooth", block:"start"});
}
function cardRevisao({q, dada, acertou}){
  const alts = q.alternativas.map((a,idx) => {
    let cls = "alt";
    if(idx === q.correta) cls += " certa";
    else if(idx === dada) cls += " errada";
    const marca = idx === dada ? " ← sua resposta" : "";
    return `<div class="${cls}" style="cursor:default">
      <span class="letra">${"ABCDE"[idx]}</span><span>${a}<em style="color:var(--texto2);font-style:normal">${marca}</em></span></div>`;
  }).join("");
  const semResposta = dada === null || dada === undefined;
  return `<div class="q-card" style="margin-bottom:14px">
    <div class="q-topo">
      <span>${acertou ? "✓ Você acertou" : (semResposta ? "— Não respondida" : "✗ Você errou")}</span>
      <span class="tag-topico">${q.topico}</span>
    </div>
    <div class="q-enunciado">${q.enunciado}</div>
    <div class="alts">${alts}</div>
    <div class="explicacao ${acertou?"ok":"no"}"><b>Explicação:</b> ${q.explicacao}</div>${htmlMacete(q)}
  </div>`;
}
function htmlMacete(q){
  return q.macete ? `<div class="macete">💡 <b>Macete:</b> ${q.macete}</div>` : "";
}

// ---------------- SIMULADO ----------------
let simEstado = null, simTimer = null;
function renderSimulado(){
  const nFracos = poolFracos().length;
  conteudo.innerHTML = `
    <div class="card">
      <h3>⏱ Simulado cronometrado</h3>
      <p class="desc" style="margin:8px 0 16px">Monte o simulado do jeito que quiser. O <b>Espelho da prova</b> reproduz os 5 blocos oficiais nos pesos reais (6/6/10/8/15).</p>
      <div class="controles">
        <label>Nº de questões:
          <select id="numQ">
            <option value="45" selected>45 (prova cheia)</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="0">Todas</option>
          </select>
        </label>
        <label>Minutos:
          <select id="min"><option>15</option><option>30</option><option selected>45</option><option>60</option><option>90</option></select>
        </label>
        <label>Sorteio:
          <select id="modoSorteio">
            <option value="espelho" selected>🎯 Espelho da prova (pesos reais)</option>
            <option value="adaptativo">🧠 Adaptativo (foca onde erro)</option>
            <option value="peso">Proporcional (tópicos)</option>
            <option value="uniforme">Uniforme</option>
          </select>
        </label>
      </div>
      <div class="controles" style="margin-top:4px">
        <label class="check-erros" title="${nFracos ? "Sorteia apenas dos blocos em que você está abaixo de 70%." : "Sem dados suficientes ainda — faça alguns simulados."}">
          <input type="checkbox" id="soFracos"> <span>🎯 Só blocos fracos (&lt;70%) — ${nFracos} questões</span>
        </label>
        <label class="check-erros" title="Marque se consultou material. Fica separado no histórico para não inflar sua média real.">
          <input type="checkbox" id="comConsulta"> <span>📖 Fiz com consulta</span>
        </label>
        <button class="btn ciano" id="iniciarSim">Começar ▶</button>
      </div>
    </div>
    <div id="avisoSim"></div>`;
  document.getElementById("iniciarSim").addEventListener("click", () => {
    let n = parseInt(document.getElementById("numQ").value);
    const min = parseInt(document.getElementById("min").value);
    const modo = document.getElementById("modoSorteio").value;
    const soFracos = document.getElementById("soFracos").checked;
    const consulta = document.getElementById("comConsulta").checked;
    const base = soFracos ? poolFracos() : QUESTOES;
    if(!base.length){ alert("Sem questões para esse filtro ainda."); return; }
    const alvo = n > 0 ? n : base.length;
    let pool;
    if(modo === "espelho") pool = amostrarEspelho(base, alvo);
    else if(modo === "adaptativo") pool = amostrarAdaptativo(base, alvo);
    else if(modo === "peso") pool = amostrarPonderado(base, alvo);
    else pool = embaralhar(base).slice(0, alvo);
    simEstado = { pool, i:0, respostas:new Array(pool.length).fill(null), restante:min*60, totalSeg:min*60, consulta };
    limparSessao();
    iniciarCronometro();
    mostrarSim();
  });

  // simulado em andamento?
  const salva = lerSessao("sim");
  if(salva && salva.restante > 0){
    const av = document.getElementById("avisoSim");
    av.innerHTML = avisoRetomar("sim", salva);
    document.getElementById("retomar").onclick = () => {
      simEstado = salva; iniciarCronometro(); mostrarSim();
    };
    document.getElementById("descartar").onclick = () => { limparSessao(); av.innerHTML = ""; };
  }
}
function iniciarCronometro(){
  clearInterval(simTimer);
  simTimer = setInterval(() => {
    simEstado.restante--;
    const el = document.getElementById("crono");
    if(el) el.textContent = fmtTempo(simEstado.restante);
    if(simEstado.restante % 5 === 0) salvarSessao("sim", simEstado); // salva periodicamente
    if(simEstado.restante <= 0) finalizarSim();
  }, 1000);
}
function mostrarSim(){
  const e = simEstado;
  salvarSessao("sim", e);
  const q = e.pool[e.i];
  const jaResp = e.respostas[e.i];
  const pct = Math.round((e.i / e.pool.length) * 100);
  conteudo.innerHTML = `
    <div class="controles" style="justify-content:space-between">
      <span class="cronometro" id="crono">${fmtTempo(e.restante)}</span>
      <button class="btn" id="encerrar">Encerrar e ver nota</button>
    </div>
    <div class="barra"><i style="width:${pct}%"></i></div>
    <div class="q-card">
      <div class="q-topo"><span>Questão ${e.i+1} de ${e.pool.length}</span><span class="tag-topico">${q.topico}</span></div>
      <div class="q-enunciado">${q.enunciado}</div>
      <div class="alts" id="alts">
        ${q.alternativas.map((a,idx)=>`<button class="alt ${jaResp===idx?"":""}" data-idx="${idx}" style="${jaResp===idx?"border-color:var(--ciano);background:#f7fcfe":""}"><span class="letra">${"ABCDE"[idx]}</span><span>${a}</span></button>`).join("")}
      </div>
      <div class="q-nav">
        <button class="btn" id="ant" ${e.i===0?"disabled":""}>◀ Anterior</button>
        <button class="btn ciano" id="prox">${e.i<e.pool.length-1?"Próxima ▶":"Finalizar ▶"}</button>
      </div>
    </div>`;
  document.querySelectorAll("#alts .alt").forEach(btn => {
    btn.addEventListener("click", () => { e.respostas[e.i] = parseInt(btn.dataset.idx); mostrarSim(); });
  });
  document.getElementById("ant").onclick = () => { if(e.i>0){e.i--;mostrarSim();} };
  document.getElementById("prox").onclick = () => { if(e.i<e.pool.length-1){e.i++;mostrarSim();} else finalizarSim(); };
  document.getElementById("encerrar").onclick = finalizarSim;
}
function finalizarSim(){
  clearInterval(simTimer);
  limparSessao();
  const e = simEstado;
  let acertos = 0, respondidas = 0;
  const porBloco = {};
  e.pool.forEach((q,idx) => {
    const acertou = e.respostas[idx] === q.correta;
    if(acertou) acertos++;
    const b = blocoDe(q.topico);
    porBloco[b] = porBloco[b] || {total:0,acertos:0};
    porBloco[b].total++;
    if(acertou) porBloco[b].acertos++;
    registrar(q.topico, acertou);
    const respondeu = e.respostas[idx] !== null && e.respostas[idx] !== undefined;
    if(respondeu){ respondidas++; marcarErro(q, !acertou); }
  });
  const pct = Math.round((acertos/e.pool.length)*100);
  const aprovado = pct >= 70;
  const segUsados = (e.totalSeg || 0) - Math.max(0, e.restante);
  const ritmo = respondidas ? Math.round(segUsados/respondidas) : 0;

  // salva no histórico (para evolução e ritmo)
  salvarSimuladoHist({
    ts: Date.now(), pct, acertos, total:e.pool.length,
    segundos: segUsados, ritmo, consulta: !!e.consulta,
    porBloco: Object.fromEntries(ORDEM_BLOCO.filter(b=>porBloco[b]).map(b=>[b,[porBloco[b].acertos,porBloco[b].total]]))
  });

  const linhas = ORDEM_BLOCO.filter(b=>porBloco[b]).map(b => {
    const d = porBloco[b]; const p = Math.round((d.acertos/d.total)*100);
    return `<tr><td>${b}</td><td>${d.acertos}/${d.total}</td>
      <td><div class="mini-barra"><i style="width:${p}%;background:${p>=70?'var(--verde)':p>=50?'#e0a300':'var(--vermelho)'}"></i></div></td>
      <td>${p}%</td></tr>`;
  }).join("");
  conteudo.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${pct}%</b><span>Nota final${e.consulta?' 📖':''}</span></div>
      <div class="stat verde"><b>${acertos}</b><span>Acertos</span></div>
      <div class="stat vermelho"><b>${e.pool.length-acertos}</b><span>Erros</span></div>
      <div class="stat ${aprovado?'verde':'vermelho'}"><b>${aprovado?'✓':'✗'}</b><span>${aprovado?'Aprovado (≥70%)':'Abaixo de 70%'}</span></div>
    </div>
    ${e.consulta?`<div class="macete" style="margin:0 0 12px">📖 <b>Com consulta:</b> esta nota fica separada no histórico e não entra na sua média "real" (sem consulta).</div>`:''}
    <div class="stat-grid" style="margin-bottom:14px">
      <div class="stat"><b>${fmtTempo(segUsados)}</b><span>Tempo usado</span></div>
      <div class="stat"><b>${ritmo}s</b><span>Ritmo / questão</span></div>
    </div>
    <h3 style="margin:6px 0 12px">Desempenho por bloco oficial</h3>
    <table class="tabela-topicos">
      <tr><th>Bloco</th><th>Acertos</th><th>Aproveitamento</th><th>%</th></tr>
      ${linhas}
    </table>
    <div class="centro" id="acoesResultado">
      <button class="btn" onclick="revisar(simEstado,'erros')">📝 Revisar erros</button>
      <button class="btn" onclick="revisar(simEstado,'todas')">Ver gabarito completo</button>
      <button class="btn" onclick="render('progresso')">📊 Ver evolução</button>
      <button class="btn ciano" onclick="render('simulado')">Novo simulado ▶</button>
    </div>
    <div id="areaRevisao"></div>`;
}

// ---------------- PROGRESSO ----------------
function corPct(p){ return p>=70?'var(--verde)':p>=50?'#e0a300':'var(--vermelho)'; }

function renderProgresso(){
  const p = lerProg();
  const ent = Object.entries(p).sort();
  let totalT=0, totalA=0;
  ent.forEach(([_,d])=>{totalT+=d.total;totalA+=d.acertos;});
  const geral = totalT ? Math.round((totalA/totalT)*100) : 0;

  // --- desempenho por bloco oficial ---
  const pb = progressoPorBloco();
  const linhasBloco = ORDEM_BLOCO.map(b => {
    const d = pb[b] || {total:0,acertos:0};
    const pc = d.total ? Math.round((d.acertos/d.total)*100) : null;
    const barra = pc===null ? `<span style="color:var(--texto2)">sem dados</span>`
      : `<div class="mini-barra"><i style="width:${pc}%;background:${corPct(pc)}"></i></div>`;
    return `<tr><td>${b} <small style="color:var(--texto2)">(${PESO_BLOCO[b]}q)</small></td>
      <td>${d.total?d.acertos+'/'+d.total:'—'}</td><td>${barra}</td><td>${pc===null?'—':pc+'%'}</td></tr>`;
  }).join("");

  // --- diagnóstico: bloco mais fraco com dados ---
  const comDados = ORDEM_BLOCO.map(b=>({b, d:pb[b]})).filter(x=>x.d && x.d.total>=3)
    .map(x=>({b:x.b, pct:x.d.acertos/x.d.total*100}));
  let diag;
  if(!comDados.length){
    diag = `Faça alguns simulados (de preferência <b>sem consulta</b>) para o diagnóstico aparecer.`;
  } else {
    comDados.sort((a,b)=>a.pct-b.pct);
    const pior = comDados[0];
    const pesoPior = PESO_BLOCO[pior.b];
    diag = `Seu ponto mais fraco é <b>${pior.b}</b> (${pior.pct.toFixed(0)}%)` +
      (pesoPior>=10?` — e vale <b>${pesoPior} questões</b> na prova, então é alta prioridade.`:`.`) +
      ` Use o <b>Simulado → Só blocos fracos</b> ou o modo <b>Adaptativo</b> para treinar isso.`;
  }

  // --- evolução dos simulados ---
  const hist = lerHist();
  const semC = hist.filter(h=>!h.consulta);
  const mediaSemC = semC.length ? Math.round(semC.reduce((s,h)=>s+h.pct,0)/semC.length) : null;
  const ultimos = hist.slice(-16);
  let grafico = `<div class="vazio">Sem simulados ainda. Faça um na aba Simulado!</div>`;
  if(ultimos.length){
    const barras = ultimos.map(h => {
      const alt = Math.max(4, Math.round(h.pct*0.9));
      const cor = h.consulta ? '#9bbccf' : corPct(h.pct);
      const borda = h.consulta ? 'border:1px dashed #5c7a8c;' : '';
      return `<div style="display:flex;flex-direction:column;align-items:center;gap:3px;flex:1">
        <div style="font-size:10px;color:var(--texto2)">${h.pct}</div>
        <div title="${h.consulta?'com consulta ':''}${new Date(h.ts).toLocaleDateString('pt-BR')}" style="width:100%;max-width:26px;height:${alt}px;background:${cor};${borda}border-radius:4px 4px 0 0"></div>
      </div>`;
    }).join("");
    grafico = `
      <div style="display:flex;align-items:flex-end;gap:5px;height:110px;padding:8px 2px;border-bottom:2px solid var(--borda)">${barras}</div>
      <div style="display:flex;gap:16px;margin-top:8px;font-size:12px;color:var(--texto2)">
        <span><span style="display:inline-block;width:10px;height:10px;background:var(--verde);border-radius:2px"></span> sem consulta</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#9bbccf;border:1px dashed #5c7a8c;border-radius:2px"></span> com consulta</span>
        <span style="margin-left:auto">linha de corte: 70%</span>
      </div>`;
  }

  const linhasTopico = ent.length ? ent.map(([t,d])=>{
    const pc = Math.round((d.acertos/d.total)*100);
    return `<tr><td>${t}</td><td>${d.acertos}/${d.total}</td>
      <td><div class="mini-barra"><i style="width:${pc}%;background:${corPct(pc)}"></i></div></td>
      <td>${pc}%</td></tr>`;
  }).join("") : `<tr><td colspan="4" style="text-align:center;color:var(--texto2)">Ainda sem histórico.</td></tr>`;

  conteudo.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${totalT}</b><span>Questões respondidas</span></div>
      <div class="stat verde"><b>${totalA}</b><span>Acertos totais</span></div>
      <div class="stat"><b>${geral}%</b><span>Aproveitamento geral</span></div>
      <div class="stat ${mediaSemC===null?'':(mediaSemC>=70?'verde':'vermelho')}"><b>${mediaSemC===null?'—':mediaSemC+'%'}</b><span>Média simulados (sem consulta)</span></div>
    </div>

    <div class="card" style="border-left:4px solid var(--ciano)">
      <h3 style="margin:0 0 6px">🔎 Diagnóstico</h3>
      <p class="desc" style="margin:0">${diag}</p>
    </div>

    <h3 style="margin:18px 0 12px">Desempenho por bloco oficial da prova</h3>
    <table class="tabela-topicos">
      <tr><th>Bloco</th><th>Acertos</th><th>Aproveitamento</th><th>%</th></tr>
      ${linhasBloco}
    </table>

    <h3 style="margin:22px 0 10px">📈 Evolução dos simulados</h3>
    ${grafico}

    <h3 style="margin:22px 0 12px">Detalhe por tópico</h3>
    <table class="tabela-topicos">
      <tr><th>Tópico</th><th>Acertos</th><th>Aproveitamento</th><th>%</th></tr>
      ${linhasTopico}
    </table>

    <div class="centro" style="gap:10px">
      <button class="btn" onclick="if(confirm('Apagar o histórico de acertos por tópico/bloco?')){localStorage.removeItem('${PROG_KEY}');render('progresso');}">Zerar histórico de tópicos</button>
      <button class="btn" onclick="if(confirm('Apagar o histórico de simulados (evolução)?')){localStorage.removeItem('${HIST_KEY}');render('progresso');}">Zerar evolução</button>
    </div>`;
}

// ---------------- utils ----------------
function embaralhar(arr){ const a=[...arr]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function fmtTempo(s){ s=Math.max(0,s); const m=Math.floor(s/60); const seg=s%60; return `${String(m).padStart(2,"0")}:${String(seg).padStart(2,"0")}`; }

// pesos aproximados por bloco no edital da CGA (mais alto = mais questões na prova)
const PESO_TOPICO = {
  "Renda Fixa": 5, "Renda Variável": 5, "Performance e Risco": 4,
  "Estatística e Risco": 3, "Regulação e Fundos": 3, "Ética e Regulação": 3,
  "Derivativos": 2, "Economia": 2, "Finanças": 2
};
// sorteia n questões respeitando os pesos por tópico (sem repetir), com fallback quando falta questão no tópico
function amostrarPonderado(todas, n){
  const porTopico = {};
  todas.forEach(q => { (porTopico[q.topico] = porTopico[q.topico] || []).push(q); });
  Object.values(porTopico).forEach(arr => arr.sort(() => Math.random()-0.5)); // embaralha dentro do tópico
  const escolhidas = [];
  const usados = new Set();
  while(escolhidas.length < n){
    // monta lista de tópicos que ainda têm questão disponível
    const disp = Object.keys(porTopico).filter(t => porTopico[t].some(q => !usados.has(q)));
    if(!disp.length) break;
    const pesos = disp.map(t => PESO_TOPICO[t] || 1);
    const total = pesos.reduce((a,b)=>a+b,0);
    let r = Math.random()*total, t = disp[0];
    for(let i=0;i<disp.length;i++){ r -= pesos[i]; if(r<=0){ t = disp[i]; break; } }
    const q = porTopico[t].find(q => !usados.has(q));
    if(q){ usados.add(q); escolhidas.push(q); }
  }
  return escolhidas;
}

// sorteio ESPELHO DA PROVA: distribui n questões entre os 5 blocos oficiais
// na proporção real (6/6/10/8/15). Para n=45 reproduz a prova exata.
function amostrarEspelho(todas, n){
  const porBloco = {};
  todas.forEach(q => { const b = blocoDe(q.topico); (porBloco[b] = porBloco[b] || []).push(q); });
  Object.values(porBloco).forEach(arr => arr.sort(() => Math.random()-0.5));
  const totalPeso = ORDEM_BLOCO.reduce((s,b)=>s+PESO_BLOCO[b],0);
  // cota ideal por bloco (arredondada), limitada ao que existe
  let cotas = ORDEM_BLOCO.map(b => ({ b, alvo: Math.round(n * PESO_BLOCO[b] / totalPeso) }));
  const escolhidas = [], usados = new Set();
  cotas.forEach(({b, alvo}) => {
    const disp = porBloco[b] || [];
    for(let i=0; i<alvo && i<disp.length; i++){ usados.add(disp[i]); escolhidas.push(disp[i]); }
  });
  // completa/apara até n (caso arredondamento ou falta de questão em algum bloco)
  if(escolhidas.length < n){
    const resto = embaralhar(todas.filter(q => !usados.has(q)));
    for(const q of resto){ if(escolhidas.length>=n) break; escolhidas.push(q); }
  }
  return embaralhar(escolhidas.slice(0, n));
}

// sorteio ADAPTATIVO: pondera cada tópico pela FRAQUEZA (1 - aproveitamento),
// então temas onde você erra mais caem com mais frequência.
function amostrarAdaptativo(todas, n){
  const prog = lerProg();
  const porTopico = {};
  todas.forEach(q => { (porTopico[q.topico] = porTopico[q.topico] || []).push(q); });
  Object.values(porTopico).forEach(arr => arr.sort(() => Math.random()-0.5));
  const pesoTopico = t => {
    const d = prog[t];
    const aprov = (d && d.total>=3) ? d.acertos/d.total : 0.5; // sem dado = neutro
    return 0.15 + (1 - aprov); // base 0,15 + fraqueza (0 a 1)
  };
  const escolhidas = [], usados = new Set();
  while(escolhidas.length < n){
    const disp = Object.keys(porTopico).filter(t => porTopico[t].some(q => !usados.has(q)));
    if(!disp.length) break;
    const pesos = disp.map(pesoTopico);
    const total = pesos.reduce((a,b)=>a+b,0);
    let r = Math.random()*total, t = disp[0];
    for(let i=0;i<disp.length;i++){ r -= pesos[i]; if(r<=0){ t = disp[i]; break; } }
    const q = porTopico[t].find(q => !usados.has(q));
    if(q){ usados.add(q); escolhidas.push(q); }
  }
  return escolhidas;
}

// questões dos blocos em que você está abaixo da meta (para "focar nos fracos")
function poolFracos(meta=70){
  const fracos = new Set(blocosFracos(meta));
  return QUESTOES.filter(q => fracos.has(blocoDe(q.topico)));
}

// inicial
render("formulas");
