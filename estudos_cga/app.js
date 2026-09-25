// ============================================================
//  Central de Estudos CGA - lógica da interface
// ============================================================
const FORMULAS = window.FORMULAS || [];
const QUESTOES = window.QUESTOES || [];
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
  conteudo.innerHTML = `
    <div class="card">
      <h3>⏱ Simulado cronometrado</h3>
      <p class="desc" style="margin:8px 0 16px">Questões embaralhadas de todos os tópicos, com tempo. Ao final, veja o desempenho por tópico.</p>
      <div class="controles">
        <label>Nº de questões:
          <select id="numQ">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="0">Todas</option>
          </select>
        </label>
        <label>Minutos:
          <select id="min"><option>15</option><option>30</option><option>45</option><option>60</option></select>
        </label>
        <label>Sorteio:
          <select id="modoSorteio">
            <option value="peso">Proporcional à prova</option>
            <option value="uniforme">Uniforme</option>
          </select>
        </label>
        <button class="btn ciano" id="iniciarSim">Começar ▶</button>
      </div>
    </div>
    <div id="avisoSim"></div>`;
  document.getElementById("iniciarSim").addEventListener("click", () => {
    let n = parseInt(document.getElementById("numQ").value);
    const min = parseInt(document.getElementById("min").value);
    const modo = document.getElementById("modoSorteio").value;
    let pool = (modo === "peso" && n > 0) ? amostrarPonderado(QUESTOES, n) : embaralhar(QUESTOES);
    if(n > 0) pool = pool.slice(0, n);
    simEstado = { pool, i:0, respostas:new Array(pool.length).fill(null), restante:min*60 };
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
  let acertos = 0;
  const porTopico = {};
  e.pool.forEach((q,idx) => {
    const acertou = e.respostas[idx] === q.correta;
    if(acertou) acertos++;
    porTopico[q.topico] = porTopico[q.topico] || {total:0,acertos:0};
    porTopico[q.topico].total++;
    if(acertou) porTopico[q.topico].acertos++;
    registrar(q.topico, acertou);
    const respondeu = e.respostas[idx] !== null && e.respostas[idx] !== undefined;
    if(respondeu) marcarErro(q, !acertou); // só conta erro em questão de fato respondida
  });
  const pct = Math.round((acertos/e.pool.length)*100);
  const aprovado = pct >= 70;
  const linhas = Object.entries(porTopico).sort().map(([t,d]) => {
    const p = Math.round((d.acertos/d.total)*100);
    return `<tr><td>${t}</td><td>${d.acertos}/${d.total}</td>
      <td><div class="mini-barra"><i style="width:${p}%;background:${p>=70?'var(--verde)':p>=50?'#e0a300':'var(--vermelho)'}"></i></div></td>
      <td>${p}%</td></tr>`;
  }).join("");
  conteudo.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${pct}%</b><span>Nota final</span></div>
      <div class="stat verde"><b>${acertos}</b><span>Acertos</span></div>
      <div class="stat vermelho"><b>${e.pool.length-acertos}</b><span>Erros</span></div>
      <div class="stat ${aprovado?'verde':'vermelho'}"><b>${aprovado?'✓':'✗'}</b><span>${aprovado?'Aprovado (≥70%)':'Abaixo de 70%'}</span></div>
    </div>
    <h3 style="margin:6px 0 12px">Desempenho por tópico</h3>
    <table class="tabela-topicos">
      <tr><th>Tópico</th><th>Acertos</th><th>Aproveitamento</th><th>%</th></tr>
      ${linhas}
    </table>
    <div class="centro" id="acoesResultado">
      <button class="btn" onclick="revisar(simEstado,'erros')">📝 Revisar erros</button>
      <button class="btn" onclick="revisar(simEstado,'todas')">Ver gabarito completo</button>
      <button class="btn ciano" onclick="render('simulado')">Novo simulado ▶</button>
    </div>
    <div id="areaRevisao"></div>`;
}

// ---------------- PROGRESSO ----------------
function renderProgresso(){
  const p = lerProg();
  const ent = Object.entries(p).sort();
  let totalT=0, totalA=0;
  ent.forEach(([_,d])=>{totalT+=d.total;totalA+=d.acertos;});
  const geral = totalT ? Math.round((totalA/totalT)*100) : 0;
  const linhas = ent.length ? ent.map(([t,d])=>{
    const pc = Math.round((d.acertos/d.total)*100);
    return `<tr><td>${t}</td><td>${d.acertos}/${d.total}</td>
      <td><div class="mini-barra"><i style="width:${pc}%;background:${pc>=70?'var(--verde)':pc>=50?'#e0a300':'var(--vermelho)'}"></i></div></td>
      <td>${pc}%</td></tr>`;
  }).join("") : `<tr><td colspan="4" style="text-align:center;color:var(--texto2)">Ainda sem histórico. Responda alguns quizzes!</td></tr>`;
  conteudo.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${totalT}</b><span>Questões respondidas</span></div>
      <div class="stat verde"><b>${totalA}</b><span>Acertos totais</span></div>
      <div class="stat"><b>${geral}%</b><span>Aproveitamento geral</span></div>
    </div>
    <h3 style="margin:6px 0 12px">Histórico por tópico</h3>
    <table class="tabela-topicos">
      <tr><th>Tópico</th><th>Acertos</th><th>Aproveitamento</th><th>%</th></tr>
      ${linhas}
    </table>
    <div class="centro"><button class="btn" onclick="if(confirm('Apagar todo o histórico?')){localStorage.removeItem('${PROG_KEY}');render('progresso');}">Zerar histórico</button></div>`;
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

// inicial
render("formulas");
