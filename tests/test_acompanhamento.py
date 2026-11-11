import acompanhamento as ac


def test_classificar_basico():
    c = ac.classificar
    assert c("CDB")[0] == "Renda Fixa Direta"
    assert c("TESOURO DIRETO - NTN-B") == ("Renda Fixa Direta", "Títulos públicos · NTN-B (IPCA)")
    assert c("BBASK329") == ("Opções", "Call")
    assert c("BBASW271") == ("Opções", "Put")
    assert c("B3SA3") == ("Ações Brasil", "Ação")
    assert c("TAEE11") == ("Ações Brasil", "Ação")
    assert c("HGLG11")[0] == "FIIs & Fiagro"
    assert c("ROXO34") == ("Internacional", "BDR")
    assert c("BOVA11") == ("Ações Brasil", "ETF de ações")
    assert c("CIANO GANBATTE FIM")[0] == "Multimercado"
    assert c("MAG CASH FIRF LP")[0] == "Fundos de Renda Fixa"
    assert c("BTG TOTAL INCENTIVADO INFRA FIRF")[1] == "Incentivados (isentos)"
    assert c("HASHDEX BITCOIN FICFIM")[0] == "Alternativos"
    assert c("COMPRA - HGRE11")[0] == "A receber / a liquidar"
    assert c("DIVIDENDOS - TENDA       ON      NM")[1] == "Proventos a receber"


def test_ler_posicoes_formato_us():
    df = ac.ler_posicoes("product\ttotal_gross_value\ttotal_net_value\nX\t-6,183.09\t1,000\n")
    assert df.loc[0, "bruto"] == -6183.09 and df.loc[0, "liquido"] == 1000


def test_snapshot_atual_sem_nao_classificados():
    snaps = ac.listar_snapshots()
    if snaps:
        d = ac.montar(ac.ler_snapshot(snaps[-1]))
        assert d[d["classe"] == "Outros / revisar"].empty
