"""
Dashboard: Participación de Psicología en Atenciones de Salud.

Métrica central: ¿Qué proporción de las atenciones de cada Servicio de Salud
corresponde a psicología, y cómo cambia según el nivel de atención?

Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Participación Psicología", layout="wide")

# ── Data ─────────────────────────────────────────────────────────────────────

PSICO = "tabla05_psicologo.pdf"


@st.cache_data
def load_data():
    base_dir = Path(__file__).parent
    df = pd.read_csv(base_dir / "atenciones_por_tipo.csv")
    df["anio"] = df["anio"].astype(int)
    df_av = pd.read_csv(base_dir / "areas_verdes_por_servicio_salud.csv")
    return df, df_av


df_raw, df_av = load_data()

# ── Sidebar filters ─────────────────────────────────────────────────────────

st.sidebar.header("Filtros")

anios = sorted(df_raw["anio"].unique())
sel_anios = st.sidebar.multiselect("Año", anios, default=anios)

servicios = sorted(df_raw["servicio_salud"].unique())
sel_servicios = st.sidebar.multiselect(
    "Servicio de Salud", servicios, default=servicios
)

niveles_opciones = ["Todos", "Nivel Primario", "Nivel Secundario", "Urgencia"]
sel_nivel = st.sidebar.selectbox("Nivel de atención", niveles_opciones)

# Apply filters
df = df_raw[
    df_raw["anio"].isin(sel_anios) & df_raw["servicio_salud"].isin(sel_servicios)
]
if sel_nivel != "Todos":
    df = df[df["nivel"] == sel_nivel]

# ── Helpers ──────────────────────────────────────────────────────────────────


def pct_psico(frame):
    """% psicología = atenciones_psico / total_atenciones * 100."""
    total = frame["valor"].sum()
    psico = frame.loc[frame["tipo"] == PSICO, "valor"].sum()
    return (psico / total * 100) if total else 0.0


def agg_by_servicio(frame):
    """Return DataFrame with total, psico, % per servicio_salud."""
    g = frame.groupby("servicio_salud")
    total = g["valor"].sum().rename("total_atenciones")
    psico = (
        frame[frame["tipo"] == PSICO]
        .groupby("servicio_salud")["valor"]
        .sum()
        .rename("atenciones_psicologia")
    )
    out = pd.concat([total, psico], axis=1).fillna(0).astype({"atenciones_psicologia": int})
    out["pct_psicologia"] = out["atenciones_psicologia"] / out["total_atenciones"] * 100
    return out.sort_values("pct_psicologia", ascending=False).reset_index()


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_general, tab_corr = st.tabs([
    "Visión General de Atenciones",
    "Análisis de Correlación: Áreas Verdes vs. Psicología",
])

with tab_general:
    tab1, tab2, tab3 = st.tabs(
        ["Participación de Psicología", "Distribución por Nivel", "Evolución"]
    )

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 1 – Participación de Psicología
    # ══════════════════════════════════════════════════════════════════════════════

    with tab1:
        st.header("Participación de Psicología en Atenciones")

        # KPIs
        total_all = int(df["valor"].sum())
        total_psico = int(df.loc[df["tipo"] == PSICO, "valor"].sum())
        pct_global = (total_psico / total_all * 100) if total_all else 0.0

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Atenciones", f"{total_all:,.0f}")
        k2.metric("Atenciones Psicología", f"{total_psico:,.0f}")
        k3.metric("% Psicología (global)", f"{pct_global:.2f}%")

        # Toggle absolute vs %
        mostrar_abs = st.toggle("Mostrar valores absolutos", value=False)

        # Table
        tbl = agg_by_servicio(df)
        st.subheader("Por Servicio de Salud")

        if mostrar_abs:
            st.dataframe(
                tbl.rename(columns={
                    "servicio_salud": "Servicio de Salud",
                    "total_atenciones": "Total Atenciones",
                    "atenciones_psicologia": "Atenciones Psicología",
                    "pct_psicologia": "% Psicología",
                }).style.format({
                    "Total Atenciones": "{:,.0f}",
                    "Atenciones Psicología": "{:,.0f}",
                    "% Psicología": "{:.2f}%",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(
                tbl[["servicio_salud", "pct_psicologia"]].rename(columns={
                    "servicio_salud": "Servicio de Salud",
                    "pct_psicologia": "% Psicología",
                }).style.format({"% Psicología": "{:.2f}%"}),
                use_container_width=True,
                hide_index=True,
            )

        # Horizontal bar chart
        st.subheader("% Psicología por Servicio de Salud")
        bar_data = tbl.copy()
        chart = (
            alt.Chart(bar_data)
            .mark_bar()
            .encode(
                x=alt.X("pct_psicologia:Q", title="% Psicología"),
                y=alt.Y("servicio_salud:N", sort="-x", title="Servicio de Salud"),
                tooltip=[
                    alt.Tooltip("servicio_salud:N", title="Servicio"),
                    alt.Tooltip("pct_psicologia:Q", title="% Psicología", format=".2f"),
                    alt.Tooltip("atenciones_psicologia:Q", title="At. Psicología", format=",.0f"),
                    alt.Tooltip("total_atenciones:Q", title="Total At.", format=",.0f"),
                ],
                color=alt.value("#4c78a8"),
            )
            .properties(height=max(len(bar_data) * 22, 200))
        )
        st.altair_chart(chart, use_container_width=True)

        # Heatmap: servicio × nivel
        st.subheader("% Psicología por Servicio de Salud × Nivel")
        # For heatmap, always use all niveles regardless of filter
        df_heat = df_raw[
            df_raw["anio"].isin(sel_anios) & df_raw["servicio_salud"].isin(sel_servicios)
        ]
        rows = []
        for srv in df_heat["servicio_salud"].unique():
            for niv in ["Nivel Primario", "Nivel Secundario", "Urgencia"]:
                sub = df_heat[(df_heat["servicio_salud"] == srv) & (df_heat["nivel"] == niv)]
                total_n = sub["valor"].sum()
                psico_n = sub.loc[sub["tipo"] == PSICO, "valor"].sum()
                rows.append({
                    "servicio_salud": srv,
                    "nivel": niv,
                    "pct_psicologia": (psico_n / total_n * 100) if total_n else 0.0,
                })
        df_hm = pd.DataFrame(rows)

        heatmap = (
            alt.Chart(df_hm)
            .mark_rect()
            .encode(
                x=alt.X("nivel:N", title="Nivel"),
                y=alt.Y("servicio_salud:N", title="Servicio de Salud"),
                color=alt.Color(
                    "pct_psicologia:Q",
                    title="% Psicología",
                    scale=alt.Scale(scheme="blues"),
                ),
                tooltip=[
                    alt.Tooltip("servicio_salud:N", title="Servicio"),
                    alt.Tooltip("nivel:N", title="Nivel"),
                    alt.Tooltip("pct_psicologia:Q", title="% Psicología", format=".2f"),
                ],
            )
            .properties(height=max(len(df_hm["servicio_salud"].unique()) * 22, 200))
        )
        # Overlay text
        text = heatmap.mark_text(baseline="middle", fontSize=10).encode(
            text=alt.Text("pct_psicologia:Q", format=".1f"),
            color=alt.condition(
                alt.datum.pct_psicologia > df_hm["pct_psicologia"].median(),
                alt.value("white"),
                alt.value("black"),
            ),
        )
        st.altair_chart(heatmap + text, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 2 – Distribución por Nivel
    # ══════════════════════════════════════════════════════════════════════════════

    with tab2:
        st.header("Participación de Psicología por Nivel")
        st.caption(
            "Cada celda = atenciones psicológicas del nivel / total de atenciones del nivel × 100. "
            "**No confundir** con la distribución de psicología entre niveles."
        )

        # Participation table: % psico within each nivel per servicio
        df_filt = df.copy()
        rows2 = []
        for srv in sorted(df_filt["servicio_salud"].unique()):
            row = {"Servicio de Salud": srv}
            srv_data = df_filt[df_filt["servicio_salud"] == srv]
            for niv in ["Nivel Primario", "Nivel Secundario", "Urgencia"]:
                sub = srv_data[srv_data["nivel"] == niv]
                t = sub["valor"].sum()
                p = sub.loc[sub["tipo"] == PSICO, "valor"].sum()
                row[niv] = (p / t * 100) if t else None
            # Total across all niveles
            t_all = srv_data["valor"].sum()
            p_all = srv_data.loc[srv_data["tipo"] == PSICO, "valor"].sum()
            row["Total"] = (p_all / t_all * 100) if t_all else None
            rows2.append(row)

        df_tab2 = pd.DataFrame(rows2)
        st.dataframe(
            df_tab2.style.format(
                {c: "{:.2f}%" for c in ["Nivel Primario", "Nivel Secundario", "Urgencia", "Total"]},
                na_rep="—",
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.subheader("Distribución de atenciones psicológicas por nivel")
        st.caption(
            "Cada celda = psicología del nivel / total de psicología del servicio × 100. "
            "Responde: ¿en qué nivel se concentra la psicología?"
        )

        rows3 = []
        for srv in sorted(df_filt["servicio_salud"].unique()):
            row = {"Servicio de Salud": srv}
            srv_data = df_filt[df_filt["servicio_salud"] == srv]
            total_psico_srv = srv_data.loc[srv_data["tipo"] == PSICO, "valor"].sum()
            for niv in ["Nivel Primario", "Nivel Secundario", "Urgencia"]:
                sub = srv_data[(srv_data["nivel"] == niv) & (srv_data["tipo"] == PSICO)]
                p = sub["valor"].sum()
                row[niv] = (p / total_psico_srv * 100) if total_psico_srv else None
            rows3.append(row)

        df_tab3 = pd.DataFrame(rows3)
        st.dataframe(
            df_tab3.style.format(
                {c: "{:.2f}%" for c in ["Nivel Primario", "Nivel Secundario", "Urgencia"]},
                na_rep="—",
            ),
            use_container_width=True,
            hide_index=True,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 3 – Evolución
    # ══════════════════════════════════════════════════════════════════════════════

    with tab3:
        st.header("Evolución del % de Psicología por Año")

        sel_srv_evo = st.multiselect(
            "Servicios a comparar",
            sorted(df_raw["servicio_salud"].unique()),
            default=["SNSS"],
            key="evo_srv",
        )

        if sel_srv_evo:
            df_evo_base = df_raw[df_raw["servicio_salud"].isin(sel_srv_evo)]
            if sel_nivel != "Todos":
                df_evo_base = df_evo_base[df_evo_base["nivel"] == sel_nivel]

            evo_rows = []
            for srv in sel_srv_evo:
                for yr in sorted(df_evo_base["anio"].unique()):
                    sub = df_evo_base[
                        (df_evo_base["servicio_salud"] == srv)
                        & (df_evo_base["anio"] == yr)
                    ]
                    t = sub["valor"].sum()
                    p = sub.loc[sub["tipo"] == PSICO, "valor"].sum()
                    evo_rows.append({
                        "servicio_salud": srv,
                        "anio": yr,
                        "pct_psicologia": (p / t * 100) if t else 0.0,
                        "atenciones_psicologia": int(p),
                        "total_atenciones": int(t),
                    })

            df_evo = pd.DataFrame(evo_rows)

            line = (
                alt.Chart(df_evo)
                .mark_line(point=True)
                .encode(
                    x=alt.X("anio:O", title="Año"),
                    y=alt.Y("pct_psicologia:Q", title="% Psicología"),
                    color=alt.Color("servicio_salud:N", title="Servicio de Salud"),
                    tooltip=[
                        alt.Tooltip("servicio_salud:N", title="Servicio"),
                        alt.Tooltip("anio:O", title="Año"),
                        alt.Tooltip("pct_psicologia:Q", title="% Psicología", format=".2f"),
                        alt.Tooltip("atenciones_psicologia:Q", title="At. Psicología", format=",.0f"),
                        alt.Tooltip("total_atenciones:Q", title="Total At.", format=",.0f"),
                    ],
                )
                .properties(height=400)
            )
            st.altair_chart(line, use_container_width=True)

            # Table for reference
            pivot = df_evo.pivot(
                index="servicio_salud", columns="anio", values="pct_psicologia"
            ).reset_index()
            pivot.columns = [str(c) for c in pivot.columns]
            year_cols = [c for c in pivot.columns if c != "servicio_salud"]
            st.dataframe(
                pivot.rename(columns={"servicio_salud": "Servicio de Salud"}).style.format(
                    {c: "{:.2f}%" for c in year_cols}, na_rep="—"
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Seleccione al menos un Servicio de Salud para ver la evolución.")


with tab_corr:
    st.header("Análisis de Correlación: Áreas Verdes vs. Psicología")

    st.markdown(
        """
        > **Hallazgos Clave de la Investigación:**
        > * **Asociación Positiva Significativa:** Existe una correlación lineal positiva fuerte ($r = 0.716$, $p < 0.001$) y una correlación de Spearman de $\rho = 0.798$ entre la superficie total de áreas verdes de un Servicio de Salud y la demanda/cobertura de atenciones psicológicas.
        > * **Concentración Territorial:** Jurisdicciones como *Maule*, *Metropolitano Sur Oriente* y *Metropolitano Occidente* destacan por concentrar simultáneamente los mayores volúmenes de atenciones psicológicas (superando las 900.000 atenciones acumuladas en 2020-2024) y amplias coberturas de áreas verdes (330 a 480 ha).
        > * **Distribución por Nivel Asistencial:** La atención psicológica se concentra predominantemente en el Nivel Primario (64.7%), seguido del Nivel Secundario (34.3%), mientras que Urgencias representa solo el 1.0%.
        """
    )

    # Filtrar psicología y excluir SNSS
    df_psico = df[(df["tipo"] == PSICO) & (df["servicio_salud"] != "SNSS")]
    psico_ss = (
        df_psico.groupby("servicio_salud")["valor"]
        .sum()
        .rename("atenciones_psicologia")
        .reset_index()
    )
    df_corr = pd.merge(psico_ss, df_av, on="servicio_salud", how="inner")

    # Métricas de correlación dinámicas
    # ponytail: rank().corr() calcula Spearman exacto sin requerir scipy
    if len(df_corr) >= 2 and df_corr["total_area_verde_ha"].std() > 0 and df_corr["atenciones_psicologia"].std() > 0:
        r_val = float(df_corr["total_area_verde_ha"].corr(df_corr["atenciones_psicologia"]))
        rho_val = float(df_corr["total_area_verde_ha"].rank().corr(df_corr["atenciones_psicologia"].rank()))
        r_str, rho_str = f"{r_val:.3f}", f"{rho_val:.3f}"
    else:
        r_str, rho_str = "—", "—"

    total_psico_analizadas = int(df_corr["atenciones_psicologia"].sum())
    total_ha = float(df_corr["total_area_verde_ha"].sum())

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Correlación de Pearson (r)", r_str)
    k2.metric("Correlación de Spearman (ρ)", rho_str)
    k3.metric("Total Atenciones Psicológicas", f"{total_psico_analizadas:,.0f}")
    k4.metric("Superficie Total Áreas Verdes", f"{total_ha:,.1f} ha")

    # Gráficos
    st.subheader("Dispersión con Línea de Tendencia")
    scatter_base = alt.Chart(df_corr).encode(
        x=alt.X("total_area_verde_ha:Q", title="Superficie de Áreas Verdes (Hectáreas)"),
        y=alt.Y("atenciones_psicologia:Q", title="Total Atenciones Psicológicas"),
    )
    scatter_pts = scatter_base.mark_circle(size=85, color="#1f77b4").encode(
        tooltip=[
            alt.Tooltip("servicio_salud:N", title="Servicio de Salud"),
            alt.Tooltip("total_area_verde_ha:Q", title="Áreas Verdes (ha)", format=",.1f"),
            alt.Tooltip("atenciones_psicologia:Q", title="At. Psicología", format=",.0f"),
        ]
    )
    scatter_labels = scatter_base.mark_text(
        align="left", baseline="middle", dx=7, fontSize=11
    ).encode(text="servicio_salud:N")
    scatter_trend = scatter_base.transform_regression(
        "total_area_verde_ha", "atenciones_psicologia"
    ).mark_line(color="#e45756", strokeDash=[4, 4], size=2)

    st.altair_chart(
        (scatter_pts + scatter_labels + scatter_trend).properties(height=460),
        use_container_width=True,
    )

    st.subheader("Ranking Comparativo: Atenciones Psicológicas vs. Áreas Verdes")
    order = df_corr.sort_values("atenciones_psicologia", ascending=False)["servicio_salud"].tolist()
    chart_h = max(len(df_corr) * 22, 250)

    b1 = alt.Chart(df_corr).mark_bar(color="#4c78a8").encode(
        y=alt.Y("servicio_salud:N", sort=order, title="Servicio de Salud"),
        x=alt.X("atenciones_psicologia:Q", title="Atenciones Psicológicas"),
        tooltip=[
            alt.Tooltip("servicio_salud:N", title="Servicio"),
            alt.Tooltip("atenciones_psicologia:Q", title="At. Psicología", format=",.0f"),
        ],
    ).properties(height=chart_h)

    b2 = alt.Chart(df_corr).mark_bar(color="#55a868").encode(
        y=alt.Y("servicio_salud:N", sort=order, axis=None),
        x=alt.X("total_area_verde_ha:Q", title="Áreas Verdes (ha)"),
        tooltip=[
            alt.Tooltip("servicio_salud:N", title="Servicio"),
            alt.Tooltip("total_area_verde_ha:Q", title="Áreas Verdes (ha)", format=",.1f"),
        ],
    ).properties(height=chart_h)

    st.altair_chart((b1 | b2).resolve_scale(y="shared"), use_container_width=True)

    with st.expander("Tabla de Datos Consolidados"):
        st.dataframe(
            df_corr.sort_values("atenciones_psicologia", ascending=False)[
                ["servicio_salud", "atenciones_psicologia", "total_area_verde_ha", "total_area_verde_m2", "total_unidades_vecinales"]
            ].rename(columns={
                "servicio_salud": "Servicio de Salud",
                "atenciones_psicologia": "Atenciones Psicología",
                "total_area_verde_ha": "Áreas Verdes (ha)",
                "total_area_verde_m2": "Áreas Verdes (m²)",
                "total_unidades_vecinales": "Unidades Vecinales",
            }).style.format({
                "Atenciones Psicología": "{:,.0f}",
                "Áreas Verdes (ha)": "{:,.1f}",
                "Áreas Verdes (m²)": "{:,.0f}",
                "Unidades Vecinales": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
