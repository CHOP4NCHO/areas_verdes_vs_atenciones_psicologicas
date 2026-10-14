#!/usr/bin/env python3
"""
Parsea dump.html y exporta a CSV usando pandas.
"""

import re
from pathlib import Path
import pandas as pd


def parse_dump(file_path: str = "dump.html") -> pd.DataFrame:
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    trs = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)
    rows = []
    region = ""
    provincia = ""

    for tr in trs:
        if "<th" in tr:
            continue

        if 'colspan="5"' in tr and "alt" in tr:
            m = re.search(r"<td\b[^>]*>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE)
            if m:
                clean = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                if clean:
                    region = re.split(r"\s*-\s*\d+\s+Provincias", clean)[0].strip()
                    provincia = ""
            continue

        tds = list(re.finditer(r"<td\b([^>]*)>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE))
        if not tds:
            continue

        attrs, content = tds[0].group(1), tds[0].group(2)
        if "prov" in attrs:
            provincia = re.sub(r"<[^>]+>", "", re.split(r"<br\s*/?>|<span", content, flags=re.I)[0]).strip()
            tds = tds[1:]

        if len(tds) == 4:
            vals = [re.sub(r"<[^>]+>", "", td.group(2)).strip() for td in tds]
            rows.append({
                "region": region,
                "provincia": provincia,
                "comuna": vals[0],
                "habitantes": vals[1],
                "superficie_km2": vals[2],
                "densidad": vals[3],
            })

    df = pd.DataFrame(rows)

    # Conversión de formatos numéricos chilenos (. para miles, , para decimales)
    df["habitantes"] = pd.to_numeric(df["habitantes"].str.replace(".", "", regex=False), errors="coerce").astype("Int64")
    df["superficie_km2"] = pd.to_numeric(
        df["superficie_km2"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df["densidad"] = pd.to_numeric(
        df["densidad"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )

    return df


if __name__ == "__main__":
    src = "dump.html"
    out = "info_comunas_chile.csv"

    df = parse_dump(src)
    df.to_csv(out, index=False)
    print(f"Exportadas {len(df)} comunas a '{out}'.")
