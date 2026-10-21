// ============================================================
//  CONCEITOS DESTRINCHADOS - CGA
//  Resumos aprofundados de temas que a banca gosta de misturar.
//  Como adicionar: copie um bloco { ... } e edite.
//    topico  -> mesmo nome usado nas questões (para filtrar)
//    titulo  -> nome do tema
//    resumo  -> uma linha de chamada (aparece na busca e no card)
//    tags    -> palavras-chave para a busca
//    html    -> conteúdo rico (HTML) exibido ao abrir o card
// ============================================================

window.CONCEITOS = [

  {
    topico: "Regulação e Fundos",
    titulo: "FI-Infra e o sufixo \"Crédito Privado\"",
    resumo: "Três regras que a banca mistura: classificação de fundo, sufixo de crédito privado e o regime especial de infraestrutura.",
    tags: ["fi-infra","crédito privado","infraestrutura","debêntures incentivadas","lei 12.431","cvm 175","renda fixa","sufixo","concentração","iliquidez","isenção","denominação","fidc","cri"],
    html: `
      <p><b>Esse tema junta três camadas de regra</b> que a banca adora sobrepor: classificação do fundo, sufixo de crédito privado e o regime especial de infraestrutura. Separe-as.</p>

      <h4>1. A base: o que faz um fundo ser "Renda Fixa"</h4>
      <p>Sob a <b>Resolução CVM 175</b> (que substituiu a ICVM 555), uma classe é <b>Renda Fixa</b> quando tem <b>no mínimo 80% da carteira</b> associada ao fator de risco <b>taxa de juros e/ou índice de preços</b>. Debêntures, CRI e cotas de FIDC são ativos de dívida → batem com esse fator. Na origem, portanto, a classe <b>é Renda Fixa</b>. Sem polêmica aqui.</p>

      <h4>2. O sufixo "Crédito Privado" — a regra geral</h4>
      <p>Se o fundo aplicar <b>mais de 50% do patrimônio líquido</b> em ativos de <b>responsabilidade de emissores privados</b> (risco de crédito privado), a regra geral exige duas coisas:</p>
      <ul>
        <li>incluir o <b>sufixo "Crédito Privado"</b> na denominação;</li>
        <li>trazer <b>alerta destacado</b> sobre o risco de perda de parcela substancial do patrimônio.</li>
      </ul>
      <p>É isso que uma carteira com "+50% em emissores privados" normalmente <b>aciona</b>.</p>

      <h4>3. O regime especial: FI-Infra (Lei 12.431)</h4>
      <p>Quando a política é voltada a <b>debêntures incentivadas, CRI e FIDC ligados a projetos de infraestrutura</b>, não se trata de um fundo de crédito privado "comum": é um <b>Fundo Incentivado de Investimento em Infraestrutura (FI-Infra)</b>, com regime próprio da <b>Lei 12.431</b> e <b>denominação própria vinculada à infraestrutura</b> ("Investimento em Infraestrutura").</p>
      <p class="destaque-conc">A denominação de infraestrutura <b>substitui</b> o sufixo "Crédito Privado". O FI-Infra é <b>dispensado</b> do sufixo — o regime especial <b>desloca</b> a regra geral. O risco de crédito não sumiu; muda só a forma de <b>denominar</b> a classe.</p>

      <h4>4. Dispensa do sufixo ≠ dispensa de transparência</h4>
      <p>Esse é o erro que derruba as alternativas "quase certas". O material tinha dois defeitos:</p>
      <ul>
        <li><b>Omitiu riscos de concentração e iliquidez</b> → precisam ser <b>evidenciados ao investidor</b>, não "reservados ao regulamento". Guardar risco só no regulamento é tirar do material justamente o que o investidor precisa ver.</li>
        <li><b>Destacou a isenção de IR para PF sem as condições</b> → o benefício (Lei 12.431) depende de <b>condições de manutenção</b> (prazo, características do ativo, elegibilidade do projeto). Destacar o benefício sem condições e sem riscos é propaganda incompleta.</li>
      </ul>
      <p><b>Providência correta:</b> manter o nome de infraestrutura <b>+</b> dispensar o "Crédito Privado" <b>+</b> revisar o material de divulgação (incluindo riscos e condicionantes do benefício).</p>

      <h4>Por que cada alternativa cai</h4>
      <table class="tab-conc">
        <tr><th>Alternativa</th><th></th><th>Motivo</th></tr>
        <tr><td>Acrescentar "Crédito Privado" + manter o destaque tributário como está</td><td class="x">✗</td><td>Aplica a regra geral a um fundo com regime especial; e mantém o material tributário defeituoso</td></tr>
        <tr><td><b>Manter infra + dispensar sufixo + revisar material</b></td><td class="v">✓</td><td>Respeita o regime do FI-Infra e corrige a divulgação</td></tr>
        <tr><td>"Renda Fixa – Crédito Privado" e dispensar o regime de infra na denominação</td><td class="x">✗</td><td>Joga fora o regime de infraestrutura, que é o que define a classe</td></tr>
        <tr><td>Manter infra e revisar, mas <b>reservando ao regulamento</b> os riscos</td><td class="x">✗</td><td>A "quase certa" sedutora: acerta o enquadramento, mas <b>esconde</b> risco que precisa ser <b>evidenciado</b></td></tr>
      </table>

      <p class="chave-conc">🔑 <b>Chave mental:</b> regime especial de infraestrutura vence o sufixo genérico de crédito privado <b>na denominação</b> — mas nenhum regime te dispensa de evidenciar risco e as condições do benefício fiscal <b>no material de divulgação</b>.</p>
    `
  },

  {
    topico: "Renda Fixa",
    titulo: "Duration, DV01 e Convexidade",
    resumo: "Macaulay × Modificada × Effective, o valor monetário do DV01 e por que a convexidade corrige a estimativa da duration.",
    tags: ["duration","macaulay","modificada","effective duration","dv01","dollar duration","convexidade","renda fixa","sensibilidade","taxa de juros","imunização"],
    html: `
      <p>Duration mede a <b>sensibilidade do preço</b> de um título a mudanças na taxa de juros. A banca cobra a diferença entre os tipos e a correção pela convexidade.</p>

      <h4>Os três tipos de duration</h4>
      <ul>
        <li><b>Macaulay</b>: prazo médio ponderado dos fluxos de caixa (em anos), usando o valor presente de cada fluxo como peso. É "tempo", não sensibilidade direta.</li>
        <li><b>Modificada (DM)</b>: deriva da Macaulay → DM = Macaulay / (1 + y/k). Dá a <b>variação % aproximada do preço</b> para +1 p.p. na taxa: <b>ΔP% ≈ −DM × Δy</b>. Pressupõe fluxos fixos.</li>
        <li><b>Effective (efetiva)</b>: mede a sensibilidade quando os <b>fluxos mudam</b> com a taxa (títulos com opção embutida — callable, puttable, MBS). Calculada por reprecificação (+Δy e −Δy). É a correta para bonds com opcionalidade.</li>
      </ul>

      <h4>DV01 / Dollar Duration (sensibilidade em $)</h4>
      <p>A duration modificada é em %. O <b>DV01</b> (ou PV01 / Dollar Duration) traduz isso em <b>valor monetário</b>: quanto o preço muda em reais/dólares para <b>1 ponto-base</b> (0,01%) de variação na taxa.</p>
      <p class="destaque-conc"><b>Dollar Duration ≈ DM × Preço</b> (por 1% de taxa). <b>DV01 ≈ Dollar Duration × 0,0001</b> (por 1 bp). É o que o gestor usa para dimensionar hedge: iguala o DV01 das pontas para neutralizar o risco de taxa.</p>

      <h4>Convexidade — por que a duration "erra"</h4>
      <p>A duration é uma aproximação <b>linear</b>, mas a relação preço × taxa é uma <b>curva</b> (convexa). Para variações grandes de taxa, a duration sozinha superestima a queda e subestima a alta do preço.</p>
      <p>A <b>convexidade</b> é o termo de segunda ordem que corrige isso:</p>
      <p class="destaque-conc"><b>ΔP% ≈ −DM × Δy + ½ × Convexidade × (Δy)²</b></p>
      <ul>
        <li>Convexidade <b>positiva</b> (bond comum) é "boa" para o investidor: o preço cai menos quando o juro sobe e sobe mais quando o juro cai.</li>
        <li>Títulos <b>callable</b> podem ter convexidade <b>negativa</b> em taxas baixas (o emissor exerce a recompra) — o upside de preço fica limitado.</li>
      </ul>

      <p class="chave-conc">🔑 <b>Chave mental:</b> Macaulay = tempo; Modificada = %; Effective = % com fluxo variável (opção embutida); DV01 = $ por 1 bp. A <b>convexidade</b> entra sempre que a variação de taxa é grande — e é o que faz a duration sozinha "errar".</p>
    `
  },

  {
    topico: "Renda Fixa",
    titulo: "Spread, Spread Duration e Key Rate Duration",
    resumo: "Em choque de crédito, o que domina o resultado: duration da taxa livre de risco × spread duration × key rate (deslocamentos não-paralelos).",
    tags: ["spread","spread duration","key rate duration","crédito","high yield","treasury","curva de juros","não-paralelo","risco de crédito","oas","duration efetiva"],
    html: `
      <p>Um título de crédito corporativo tem <b>dois fatores de risco de taxa</b> que se movem de forma independente: a <b>taxa livre de risco</b> (curva do Tesouro) e o <b>spread de crédito</b> (prêmio pelo risco do emissor). A banca monta cenários em que eles andam em <b>direções opostas</b>.</p>

      <h4>Duration (taxa livre de risco) × Spread Duration</h4>
      <ul>
        <li><b>Duration modificada</b>: sensibilidade do preço a mudanças na <b>curva livre de risco</b> (Treasury). ΔP% ≈ −DM × Δtaxa_livre.</li>
        <li><b>Spread duration</b>: sensibilidade do preço a mudanças no <b>spread de crédito</b>. ΔP% ≈ −SpreadDur × Δspread. Para bond a taxa prefixada, numericamente ≈ a duration, mas o <b>fator de risco é outro</b>.</li>
      </ul>
      <p class="destaque-conc"><b>O efeito líquido soma os dois:</b> ΔP% ≈ −DM × Δtaxa_livre − SpreadDur × Δspread. Num high-yield, o spread é largo e volátil → <b>a abertura de spread costuma dominar</b> o resultado, mesmo que a curva livre caia.</p>

      <h4>Exemplo típico de prova</h4>
      <p>HY com duration 4,0 e spread duration 5,0. Curva livre cai 50 bp (<b>ganho</b> ≈ 4,0 × 0,50% = +2,00%); spread abre 120 bp (<b>perda</b> ≈ 5,0 × 1,20% = −6,00%). Efeito líquido do HY ≈ <b>−4,00%</b>. Numa carteira 40% Treasury / 60% HY, com a Treasury ganhando ~3,00%: 0,40×3,00% + 0,60×(−4,00%) = <b>−1,20%</b>. Conclusão: apesar da queda da taxa livre e do <i>yield</i> alto, <b>o spread domina</b> e o resultado é de perda.</p>

      <h4>Key Rate Duration (deslocamentos não-paralelos)</h4>
      <p>Duration e spread duration supõem deslocamento <b>paralelo</b> da curva. Quando a curva muda de <b>formato</b> (steepening, flattening, butterfly), usa-se a <b>Key Rate Duration</b>: a sensibilidade do preço a um choque em <b>cada vértice</b> específico (2a, 5a, 10a...), mantendo os demais fixos.</p>
      <ul>
        <li>A soma das key rate durations ≈ a duration efetiva total.</li>
        <li>Permite medir o risco de uma carteira <b>barbell</b> vs. <b>bullet</b> com a mesma duration total, mas exposições diferentes por vértice.</li>
      </ul>

      <p class="chave-conc">🔑 <b>Chave mental:</b> em cenário de estresse de crédito, meça o efeito da <b>taxa livre</b> (duration) e do <b>spread</b> (spread duration) <b>separadamente</b> e some — não leia o resultado só pelo <i>current yield</i> ou pela queda da taxa de referência. Curva mudando de formato → <b>key rate duration</b>.</p>
    `
  },

  {
    topico: "Performance e Risco",
    titulo: "Medidas ajustadas ao risco: Sharpe × Treynor × IR × Jensen × M²",
    resumo: "Qual risco cada índice usa (total × sistemático × tracking error) e quando cada um é o correto.",
    tags: ["sharpe","treynor","information ratio","jensen","alfa","m²","m-quadrado","modigliani","beta","desvio padrão","tracking error","risco sistemático","medidas ajustadas"],
    html: `
      <p>Todas comparam <b>retorno excedente ÷ risco</b> — a diferença está em <b>qual risco</b> vai no denominador. Errar o denominador é a pegadinha clássica.</p>

      <h4>As cinco medidas</h4>
      <table class="tab-conc">
        <tr><th>Medida</th><th>Fórmula</th><th>Risco usado</th><th>Quando usar</th></tr>
        <tr><td><b>Sharpe</b></td><td>(Rp − Rf) / σp</td><td>Total (desvio padrão)</td><td>Carteira é o <b>portfólio inteiro</b> do investidor (risco não diversificado)</td></tr>
        <tr><td><b>Treynor</b></td><td>(Rp − Rf) / βp</td><td>Sistemático (beta)</td><td>Carteira é <b>uma parte</b> de um conjunto já diversificado</td></tr>
        <tr><td><b>Information Ratio</b></td><td>(Rp − Rb) / TE</td><td>Tracking error (risco ativo)</td><td>Avaliar a <b>gestão ativa</b> vs. o benchmark</td></tr>
        <tr><td><b>Jensen (α)</b></td><td>Rp − [Rf + βp(Rm − Rf)]</td><td>Sistemático (CAPM)</td><td>Retorno <b>acima do previsto pelo CAPM</b> (habilidade)</td></tr>
        <tr><td><b>M² (Modigliani)</b></td><td>deriva do Sharpe</td><td>Total (desvio padrão)</td><td>Mesmo ranking do Sharpe, mas expresso em <b>% de retorno</b> comparável</td></tr>
      </table>

      <h4>Os pares que confundem</h4>
      <ul>
        <li><b>Sharpe × Treynor</b>: mesmo numerador (prêmio sobre o livre de risco). Sharpe usa <b>risco total</b> (σ); Treynor usa <b>só o sistemático</b> (β). Se a carteira é tudo que o investidor tem → Sharpe. Se é um sleeve de um todo diversificado → Treynor.</li>
        <li><b>IR × Jensen</b>: ambos olham para o benchmark/modelo. IR divide o retorno ativo pelo <b>tracking error</b>; Jensen é o <b>alfa</b> em pontos, sem dividir por risco.</li>
        <li><b>M² × Sharpe</b>: M² dá o <b>mesmo ordenamento</b> do Sharpe (é o Sharpe "alavancado/desalavancado" até a volatilidade do mercado), só que num número em % mais fácil de interpretar.</li>
      </ul>

      <p class="chave-conc">🔑 <b>Chave mental:</b> a pergunta é sempre "qual risco no denominador?". Portfólio inteiro → <b>total/σ</b> (Sharpe, M²). Parte de um todo diversificado → <b>sistemático/β</b> (Treynor, Jensen). Gestão ativa vs. índice → <b>tracking error</b> (IR).</p>
    `
  },

  {
    topico: "Renda Fixa",
    titulo: "Imunização × Cash-flow matching × Estratégias passivas",
    resumo: "Como casar ativos a passivos: imunização por duration, casamento de fluxo e as combinações (contingent e combination matching).",
    tags: ["imunização","cash-flow matching","dedicação","contingent immunization","combination matching","duration","passivo","alm","renda fixa","risco de reinvestimento"],
    html: `
      <p>O objetivo é garantir recursos para honrar <b>passivos futuros</b>. As estratégias variam no grau de precisão × flexibilidade × custo.</p>

      <h4>Imunização clássica (por duration)</h4>
      <p>Iguala a <b>duration</b> dos ativos à do passivo (e o valor presente). Assim, o <b>risco de preço</b> e o <b>risco de reinvestimento</b> se compensam diante de um deslocamento de taxa: o que se perde num, ganha-se no outro. Exige <b>rebalanceamento</b> (a duration muda com o tempo e com as taxas) e protege bem só contra deslocamentos <b>paralelos</b>.</p>

      <h4>Cash-flow matching (dedicação)</h4>
      <p>Monta uma carteira cujos <b>fluxos de caixa coincidem</b> exatamente com os desembolsos do passivo, data a data. <b>Máxima precisão</b> e sem necessidade de rebalanceamento — mas é <b>mais cara</b> e rígida (precisa de títulos com os vencimentos certos).</p>

      <h4>As combinações</h4>
      <ul>
        <li><b>Contingent immunization</b>: gestão <b>ativa</b> enquanto o valor da carteira estiver acima de um piso (<i>safety net</i>). Se cair até o gatilho, converte-se em <b>imunização pura</b> para travar o resultado mínimo. Ativo com rede de segurança.</li>
        <li><b>Combination matching (horizon matching)</b>: faz <b>cash-flow matching nos primeiros anos</b> (passivos de curto prazo, onde deslocamentos não-paralelos doem mais) e <b>imunização por duration</b> para o restante. Equilíbrio entre custo e proteção.</li>
      </ul>

      <table class="tab-conc">
        <tr><th>Estratégia</th><th>Precisão</th><th>Custo / flexibilidade</th></tr>
        <tr><td>Cash-flow matching</td><td>Máxima</td><td>Mais cara e rígida; sem rebalanceamento</td></tr>
        <tr><td>Imunização por duration</td><td>Boa (choques paralelos)</td><td>Mais barata; exige rebalancear</td></tr>
        <tr><td>Combination matching</td><td>Alta no curto prazo</td><td>Meio-termo</td></tr>
        <tr><td>Contingent immunization</td><td>Piso garantido</td><td>Ativa até o gatilho</td></tr>
      </table>

      <p class="chave-conc">🔑 <b>Chave mental:</b> casar <b>fluxo</b> = preciso e caro; casar <b>duration</b> = barato mas só contra choque paralelo e com rebalanceamento. "Ativo com rede" = contingent; "fluxo no curto + duration no longo" = combination.</p>
    `
  },

  {
    topico: "Estatística e Risco",
    titulo: "VaR, suas limitações e stress test",
    resumo: "O que o VaR diz (e o que NÃO diz), os três métodos de cálculo e por que stress test e análise de cenário o complementam.",
    tags: ["var","value at risk","paramétrico","histórico","monte carlo","cauda","cvar","expected shortfall","stress test","análise de cenário","risco de cauda","nível de confiança"],
    html: `
      <p>O <b>VaR (Value at Risk)</b> estima a <b>perda máxima esperada</b> de uma carteira, num <b>horizonte</b> e <b>nível de confiança</b> dados, em condições normais de mercado.</p>
      <p class="destaque-conc">Leitura correta: "VaR de R$ 1 mi a 95% em 1 dia" = em <b>95% dos dias</b> a perda não passa de R$ 1 mi; nos outros <b>5%</b>, espera-se perder <b>mais</b> — mas o VaR <b>não diz quanto</b>.</p>

      <h4>Os três métodos de cálculo</h4>
      <ul>
        <li><b>Paramétrico (variância-covariância)</b>: supõe retornos <b>normais</b>; rápido, mas subestima o risco de <b>cauda</b> e trata mal opções (não-linearidade).</li>
        <li><b>Simulação histórica</b>: reaplica a distribuição <b>observada</b> no passado; não assume normalidade, mas é "refém" da janela histórica (se não houve crise na amostra, não a captura).</li>
        <li><b>Monte Carlo</b>: simula milhares de cenários a partir de um modelo; flexível (capta não-linearidade), porém <b>pesado</b> e dependente das premissas do modelo.</li>
      </ul>

      <h4>O que o VaR NÃO captura</h4>
      <ul>
        <li>A <b>magnitude</b> das perdas na cauda (além do nível de confiança) → por isso existe o <b>CVaR / Expected Shortfall</b>, que mede a perda <b>média</b> quando o VaR é rompido.</li>
        <li>Eventos <b>extremos/raros</b> e quebras de correlação em crises.</li>
        <li>Risco de <b>liquidez</b> (pode não conseguir desmontar a posição ao preço do modelo).</li>
      </ul>

      <h4>Stress test e análise de cenário (complementos)</h4>
      <p>Justamente onde o VaR é fraco, entram o <b>stress test</b> (choques severos e hipotéticos/históricos — ex.: 2008) e a <b>análise de cenário</b> (efeito de combinações específicas de fatores). Não têm "probabilidade" como o VaR; servem para <b>dimensionar a cauda</b> e testar a resiliência.</p>

      <p class="chave-conc">🔑 <b>Chave mental:</b> VaR = perda máxima <b>em condições normais</b>, dado confiança + horizonte; <b>não</b> diz o tamanho da perda além dele (isso é CVaR) nem cobre eventos extremos (isso é stress test). Se a questão fala em "pior caso" ou "além do nível de confiança", não é VaR puro.</p>
    `
  },

  {
    topico: "Performance e Risco",
    titulo: "Alocação dinâmica: Buy-and-hold × Constant Mix × CPPI",
    resumo: "Como cada estratégia reage ao mercado e qual se dá melhor em tendência, lateralidade ou queda forte.",
    tags: ["buy-and-hold","constant mix","cppi","rebalanceamento","alocação dinâmica","convexa","côncava","piso","multiplicador","mercado lateral","tendência","seguro de portfólio"],
    html: `
      <p>Três formas de administrar o peso em risco (ações) ao longo do tempo. O que muda é <b>como cada uma compra/vende conforme o mercado sobe ou cai</b>.</p>

      <h4>As três estratégias</h4>
      <ul>
        <li><b>Buy-and-hold</b>: compra e segura; <b>não rebalanceia</b>. O peso em ações sobe quando elas sobem e cai quando caem (segue o mercado). Payoff <b>linear</b>. Piso = valor do componente sem risco.</li>
        <li><b>Constant Mix</b>: mantém <b>proporção fixa</b> (ex.: 60/40) rebalanceando. Isso obriga a <b>comprar na baixa e vender na alta</b> (contrária). Payoff <b>côncavo</b>.</li>
        <li><b>CPPI (Constant Proportion Portfolio Insurance)</b>: Exposição = <b>Multiplicador × (Carteira − Piso)</b>. <b>Compra na alta e vende na baixa</b> (segue tendência); protege um piso. Payoff <b>convexo</b>.</li>
      </ul>

      <h4>Qual ganha em cada mercado</h4>
      <table class="tab-conc">
        <tr><th>Mercado</th><th>Melhor</th><th>Pior</th></tr>
        <tr><td><b>Tendência forte</b> (sobe ou cai direcionado)</td><td><b>CPPI</b> (segue a tendência; protege no tombo)</td><td>Constant Mix</td></tr>
        <tr><td><b>Lateral / oscilante</b> (vai e volta)</td><td><b>Constant Mix</b> (lucra comprando barato / vendendo caro)</td><td>CPPI (compra caro / vende barato nas idas e voltas)</td></tr>
        <tr><td><b>Estável / levemente altista</b></td><td>Buy-and-hold (sem custo de giro)</td><td>—</td></tr>
      </table>

      <p class="chave-conc">🔑 <b>Chave mental:</b> Constant Mix é <b>contrária</b> e <b>côncava</b> → ama mercado <b>lateral</b>. CPPI <b>segue tendência</b> e é <b>convexa</b> com piso → ama mercado <b>direcional</b> e protege em queda forte. Buy-and-hold é o neutro linear.</p>
    `
  }

];
