import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df0 = pd.read_csv('outputs/csv/report_assignment.csv')
df1 = df0[df0['type']=='progress'].copy()

x = [
    #'IMK Tahunan 2025 - Pencacahan', 
    'IMK Triwulanan 2025 - PENCACAHAN',
    #'IMK Tahunan 2025 - Listing',
    #'SURVEI TAHUNAN PERUSAHAAN INDUSTRI MANUFAKTUR KOMODITAS 2024 (SKIM)',
    #'SURVEI TAHUNAN PERUSAHAAN INDUSTRI MANUFAKTUR 2024 (STPIM)',
    'PENDATAAN IBS TRIWULANAN 2025',
    'SURVEI TRIWULANAN PELAKU USAHA (TRIWULAN 3 - 4)',
    #'PEMUTAKHIRAN DIREKTORI PERUSAHAAN AWAL - 2025',    
    #'IMK Triwulanan 2025 - LISTING',
    #'SURVEI IBS BULANAN - PENDATAAN 2025',
    #'SURVEI IBS BULANAN - Webentry',
]

cacah_col = [col for col in df1.columns if col.lower().startswith('submitted')]

selesai_col = [col for col in df1.columns if col.lower().startswith(('approved', 'completed', 'edited'))]

A_only = [x for x in df1.columns if x not in cacah_col and x not in selesai_col]

df1['cacah'] = df1[cacah_col].sum(axis=1)
df1['pct_cacah'] = ((df1['cacah'] / df1['total'])).round(2)
df1['selesai'] = df1[selesai_col].sum(axis=1)
df1['pct_selesai'] = ((df1['selesai'] / df1['total'])).round(2)
df1 = df1.loc[df1['name'].isin(x),:]

pivoted = df1.pivot(index='kd_kab', columns='name', values=['total', 'cacah', 'selesai','pct_selesai'])

# Swap column levels: make 'name' the top-level, and 'value' the sub-level
pivoted.columns = pivoted.columns.swaplevel(0, 1)

# Sort columns so they appear grouped by 'name'
pivoted = pivoted.sort_index(axis=1, level=0)

# Desired subcolumn order
suborder = ['total', 'cacah','selesai', 'pct_selesai']

# Reorder subcolumns under each survey
pivoted = pivoted.reindex(columns=suborder, level=1)
pivoted.index= pivoted.index.astype(str)
pivoted.to_excel('outputs/output.xlsx', merge_cells=True)

# --- Compact, rectangle-packed tables; numbers right; kd_kab centered; full headers ---

monitoring_surveys = [
    #'IMK Tahunan 2025 - Listing',
    "IMK Tahunan 2025 - Pencacahan",
    'IMK Triwulanan 2025 - PENCACAHAN',
    #'SURVEI IBS BULANAN - PENDATAAN 2025',
    'PENDATAAN IBS TRIWULANAN 2025',
    'SURVEI TAHUNAN PERUSAHAAN INDUSTRI MANUFAKTUR 2024 (STPIM)',
    'SURVEI TAHUNAN PERUSAHAAN INDUSTRI MANUFAKTUR KOMODITAS 2024 (SKIM)'
]

monitoring_cols = [c for c in df1.columns
                   if c not in ['prov_id','name','time_stamp','cacah','pct_cacah','selesai','pct_selesai']]

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

cards = []

for survey in monitoring_surveys:
    monitoring_df = df1.loc[df1['name'] == survey, monitoring_cols].dropna(axis=1, how='all').copy()

    # Safe numeric sort for kd_kab
    if 'kd_kab' in monitoring_df.columns:
        monitoring_df = monitoring_df.sort_values('kd_kab',
            key=lambda s: pd.to_numeric(s, errors='coerce'))

    # Keep numeric as nullable Int64 for clean rendering
    for col in monitoring_df.columns:
        if is_numeric_dtype(monitoring_df[col].dtype):
            monitoring_df[col] = monitoring_df[col].astype('Int64')

    # Build styles
    styles = [
        {"selector": "thead th",
         "props": "background-color:#004c6d;color:#fff;font-weight:700;text-align:center;"
                  "padding:4px;border:1px solid #cfd8dc;font-size:12px;white-space:normal;"},
        {"selector": "tbody td",
         "props": "border:1px solid #cfd8dc;padding:4px 6px;font-size:12px;"
                  "vertical-align:middle;text-align:center;white-space:normal;"},
        {"selector": "tbody tr:nth-child(even)", "props": "background-color:#f9f9f9;"},
        {"selector": "tbody tr:nth-child(odd)",  "props": "background-color:#ffffff;"}
    ]

    # Right-align numeric columns except kd_kab
    numeric_cols = [col for col in monitoring_df.columns
                    if is_numeric_dtype(monitoring_df[col].dtype) and col != 'kd_kab']
    for col in numeric_cols:
        idx = monitoring_df.columns.get_loc(col) + 1
        styles.append({
            "selector": f"tbody td:nth-child({idx})",
            "props": "text-align:right;vertical-align:middle;border:1px solid #cfd8dc;padding:4px 6px;font-size:12px;"
        })

    # Center kd_kab explicitly
    if 'kd_kab' in monitoring_df.columns:
        idx_kab = monitoring_df.columns.get_loc('kd_kab') + 1
        styles.append({
            "selector": f"tbody td:nth-child({idx_kab})",
            "props": "text-align:center;vertical-align:middle;border:1px solid #cfd8dc;padding:4px 6px;font-size:12px;"
        })

    styled = (
        monitoring_df.style
        .hide(axis="index")
        .format(na_rep="-")
        .set_caption(survey)
        .set_table_attributes('class="tbl"')
        .set_table_styles(styles)
    )

    cards.append(f"<div class='card'>{styled.to_html()}</div>")

html_doc = """
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Monitoring Tables</title>
<style>
  body {font-family: Arial, Helvetica, sans-serif; margin: 18px; font-size: 12px;}
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    grid-auto-rows: 8px;
    grid-auto-flow: dense;
    gap: 18px;
    align-items: start;
  }
  .card {
    background:#fff; border:1px solid #e0e0e0; border-radius:12px; padding:10px;
    box-shadow: 0 1px 2px rgba(0,0,0,.03);
  }
  .tbl {width:100%; border-collapse:collapse;}
  .tbl th, .tbl td {white-space:normal;}
  .tbl caption {
    caption-side: top; text-align: left; font-weight: 700;
    margin-bottom: 6px; font-size: 13px; color: #0a2a3a;
  }
</style>
</head>
<body>
<div class='grid'>
""" + "".join(cards) + """
</div>

<script>
// Masonry packing
(function(){
  var grid = document.querySelector('.grid');
  if (!grid) return;
  var rowH = parseFloat(getComputedStyle(grid).gridAutoRows);
  var gap  = parseFloat(getComputedStyle(grid).gap);
  function resizeAll(){
    document.querySelectorAll('.grid .card').forEach(function(item){
      var span = Math.ceil((item.getBoundingClientRect().height + gap) / (rowH + gap));
      item.style.gridRowEnd = "span " + span;
    });
  }
  window.addEventListener('load', resizeAll);
  window.addEventListener('resize', resizeAll);
  setTimeout(resizeAll, 0);
})();
</script>

</body>
</html>
"""

with open("outputs/monitoring_tables.html", "w", encoding="utf-8") as f:
    f.write(html_doc)

print("✅ Saved: monitoring_tables.html")