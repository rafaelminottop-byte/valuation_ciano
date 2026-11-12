"""Aba Gestoras: resumos das cartas das principais gestoras do Brasil + panorama.

Os dados vêm de data/cartas_gestoras.json e data/panorama_gestoras.json (gerados
a partir do app standalone cartas_gestoras/). Visual na identidade Ciano.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit as st

_DATA = Path(__file__).parent / "data"

# Paleta Ciano
_INK = "#132244"
_INK2 = "#0B1F2A"
_CIANO = "#3FD0E0"
_TEAL = "#00586A"
_BORDA = "#E2E8F2"
_VERDE = "#16A34A"
_VERM = "#DC2626"


def _esc(s) -> str:
    return html.escape(str(s or ""))


def _fmt_data(iso: str) -> str:
    try:
        a, m, d = iso.split("-")
        return f"{d}/{m}/{a}"
    except Exception:
        return iso or ""


@st.cache_data(ttl=300)
def _carregar() -> tuple[list, dict]:
    cartas = json.loads((_DATA / "cartas_gestoras.json").read_text(encoding="utf-8"))
    pano = json.loads((_DATA / "panorama_gestoras.json").read_text(encoding="utf-8"))
    cartas.sort(key=lambda c: c.get("data", ""), reverse=True)
    return cartas, pano


# ----------------------------------------------------------------- Panorama ---
def _consenso_html(consenso: list) -> str:
    linhas = []
    for c in consenso:
        d = c.get("dir")
        seta, cor = ("▲", _VERDE) if d == "alta" else ("▼", _VERM) if d == "queda" else ("▬", "#8A94AB")
        ges = " · ".join(_esc(g) for g in c.get("gestoras", []))
        linhas.append(
            f'<div style="display:grid;grid-template-columns:210px 40px 1fr;align-items:center;'
            f'gap:8px;padding:12px 16px;border-bottom:1px solid {_BORDA};">'
            f'<div style="font-weight:800;color:{_INK};font-size:0.9rem;">{_esc(c.get("indicador"))}</div>'
            f'<div style="color:{cor};font-size:1.2rem;font-weight:800;text-align:center;">{seta}</div>'
            f'<div style="color:{_INK};font-size:0.9rem;">{_esc(c.get("visao"))}'
            f'<span style="display:block;color:{_TEAL};font-size:0.78rem;font-weight:700;margin-top:2px;">{ges}</span>'
            f'</div></div>'
        )
    return (
        f'<div style="background:#fff;border:1px solid {_BORDA};border-radius:14px;overflow:hidden;">'
        + "".join(linhas)
        + "</div>"
    )


def _tema_card_html(i: int, t: dict) -> str:
    ges = "".join(
        f'<span class="tese-tag" style="margin:2px 4px 2px 0;display:inline-block;">{_esc(g)}</span>'
        for g in t.get("gestoras", [])
    )
    nota = (
        f'<div style="color:{_TEAL};font-size:0.82rem;font-weight:700;margin:6px 0 8px;">{_esc(t.get("nota"))}</div>'
        if t.get("nota") else ""
    )
    return (
        f'<div style="background:#fff;border:1px solid {_BORDA};border-radius:16px;padding:18px 20px;height:100%;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
        f'<span style="font-size:1.4rem;">{_esc(t.get("emoji"))}</span>'
        f'<h3 style="flex:1;font-size:1.02rem;color:{_INK2};margin:0;font-weight:700;">{_esc(t.get("titulo"))}</h3>'
        f'<span style="background:#E3F1F3;color:{_TEAL};font-weight:800;font-size:0.75rem;width:24px;height:24px;'
        f'border-radius:50%;display:flex;align-items:center;justify-content:center;">{i}</span></div>'
        f'<div style="color:{_INK};font-size:0.9rem;line-height:1.55;margin-bottom:8px;">{_esc(t.get("resumo"))}</div>'
        f'{nota}<div>{ges}</div></div>'
    )


def _render_panorama(pano: dict) -> None:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{_INK2},#16324a);color:#fff;border-radius:14px;'
        f'padding:20px 22px;border-left:4px solid {_CIANO};margin-bottom:16px;">'
        f'<div style="color:{_CIANO};font-size:0.72rem;font-weight:800;letter-spacing:.06em;'
        f'text-transform:uppercase;margin-bottom:8px;">{_esc(pano.get("periodo","Panorama"))}</div>'
        f'<div style="font-size:0.98rem;line-height:1.6;">{_esc(pano.get("destaque"))}</div></div>',
        unsafe_allow_html=True,
    )

    consenso = pano.get("consenso") or []
    if consenso:
        st.markdown('<div class="ciano-label">Consenso das gestoras</div>', unsafe_allow_html=True)
        st.markdown(_consenso_html(consenso), unsafe_allow_html=True)
        st.caption("Direção da visão predominante nas cartas — não são previsões numéricas nossas.")

    st.markdown('<div class="ciano-label" style="margin-top:14px;">Principais temas</div>',
                unsafe_allow_html=True)
    temas = pano.get("temas") or []
    for linha in range(0, len(temas), 2):
        cols = st.columns(2)
        for col, t in zip(cols, temas[linha:linha + 2]):
            col.markdown(_tema_card_html(temas.index(t) + 1, t), unsafe_allow_html=True)

    atualizado = _fmt_data(pano.get("atualizadoEm", ""))
    st.caption(f"Síntese das visões dos gestores nas últimas cartas. Atualizado em {atualizado}.")


# --------------------------------------------------------------------- Feed ---
def _carta_card_html(c: dict) -> str:
    bullets = "".join(f'<li style="margin-bottom:6px;">{_esc(b)}</li>' for b in c.get("bullets", []))
    tags = "".join(
        f'<span class="tese-tag" style="margin:2px 4px 2px 0;display:inline-block;">#{_esc(t)}</span>'
        for t in c.get("tags", [])
    )
    ativos = ""
    if c.get("ativos"):
        ativos = (
            f'<div style="font-size:0.85rem;color:{_INK};margin-top:8px;">'
            f'<b>Ativos citados:</b> {" · ".join(_esc(a) for a in c["ativos"])}</div>'
        )
    link = (
        f'<a href="{_esc(c.get("url"))}" target="_blank" style="color:{_TEAL};font-weight:700;'
        f'font-size:0.85rem;text-decoration:none;">📄 Abrir carta original (PDF)</a>'
        if c.get("url") else ""
    )
    return (
        f'<div style="background:#fff;border:1px solid {_BORDA};border-radius:14px;padding:18px 20px;margin-bottom:14px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px;">'
        f'<span style="font-weight:800;color:{_INK2};font-size:0.95rem;">🏦 {_esc(c.get("gestora"))} '
        f'<span class="tese-tag" style="margin-left:4px;">{_esc(c.get("categoria"))}</span></span>'
        f'<span style="color:#6B7690;font-size:0.8rem;">{_fmt_data(c.get("data",""))}</span></div>'
        f'<h3 style="font-size:1.05rem;color:{_INK2};margin:2px 0 8px;font-weight:700;">{_esc(c.get("titulo"))}</h3>'
        f'<div style="font-style:italic;color:#44506B;border-left:3px solid {_CIANO};padding-left:12px;'
        f'margin:8px 0 12px;font-size:0.9rem;">{_esc(c.get("tese"))}</div>'
        f'<ul style="margin:6px 0 10px;padding-left:20px;color:{_INK};font-size:0.9rem;line-height:1.5;">{bullets}</ul>'
        f'{ativos}<div style="margin-top:8px;">{tags}</div>'
        f'<div style="margin-top:10px;">{link}</div></div>'
    )


def _render_feed(cartas: list) -> None:
    cats = sorted({c.get("categoria") for c in cartas if c.get("categoria")})
    col1, col2 = st.columns([2, 1])
    busca = col1.text_input("Buscar por gestora, tema ou ativo", key="gest_busca").strip().lower()
    cat = col2.selectbox("Categoria", ["Todas"] + cats, key="gest_cat")

    def _ok(c: dict) -> bool:
        if cat != "Todas" and c.get("categoria") != cat:
            return False
        if busca:
            blob = " ".join([
                c.get("gestora", ""), c.get("titulo", ""), c.get("tese", ""),
                " ".join(c.get("bullets", [])), " ".join(c.get("tags", [])),
                " ".join(c.get("ativos", [])),
            ]).lower()
            if busca not in blob:
                return False
        return True

    filtradas = [c for c in cartas if _ok(c)]
    st.markdown(f'<div class="ciano-label">{len(filtradas)} carta(s)</div>', unsafe_allow_html=True)
    if not filtradas:
        st.info("Nenhuma carta com esses filtros.")
    for c in filtradas:
        st.markdown(_carta_card_html(c), unsafe_allow_html=True)


# ------------------------------------------------------------------- render ---
def render() -> None:
    try:
        cartas, pano = _carregar()
    except Exception as e:  # pragma: no cover
        st.error(f"Não consegui carregar as cartas das gestoras: {e}")
        return

    st.caption(
        "Resumos das cartas das principais gestoras do Brasil. Síntese editorial das "
        "visões dos gestores — não é recomendação de investimento."
    )
    modo = st.radio("Ver", ["📊 Panorama", "📬 Cartas"], horizontal=True, key="gest_modo")
    if modo.startswith("📊"):
        _render_panorama(pano)
    else:
        _render_feed(cartas)
