import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import palette_options
import time
from datetime import datetime

def get_color(col_name):
    pattern_colors = palette_options['Pastel']
    for pattern, color in pattern_colors.items():
        if col_name.upper().startswith(pattern.upper()):
            return color
    return '#C9C9C9'  # fallback for unrecognized statuses

def generate_plots(df, survey_collection_df, prefered_status_order, option:int):
    if option not in [1, 2]:
        raise ValueError("Parameter 'option' must be either 1 or 2.")
    os.makedirs("images", exist_ok=True)
    

    show = pd.read_excel('input/show.xlsx')

    show_ls = show.loc[show['show']==1,'name'].tolist()

    if option==1:
        status_order = [col for col in df.columns if col not in ['kd_kab', 'time_stamp', 'name', 'prov_id', 'total', 'assigned', 'have-not-assigned', 'type']]
    else:
        status_order = ['assigned', 'have-not-assigned']
    status_order.sort()
    


    prefered_status_order = [col for col in prefered_status_order if col in df.columns] if option ==1 else ['assigned', 'have-not-assigned']

    if option==1:
        color_map = {col: get_color(col) for col in df.columns if col not in ['kd_kab', 'time_stamp', 'name', 'prov_id', 'total']}
    else:
        color_map = {'assigned': '#B5EAD7', 'have-not-assigned': '#E57373'}

    n = len(show_ls)
    cols = 2
    total_plots = n + 1  # +1 for legend
    rows = math.ceil(total_plots / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 6, rows * 4))
    axes = axes.flatten()

    for i, survey_name in enumerate(show_ls):
        temp_df = df.loc[
            df['name'] == survey_name,
            ['kd_kab'] + prefered_status_order
        ].copy()

        # Clean numeric columns
        for col in prefered_status_order:
            if pd.api.types.is_numeric_dtype(temp_df[col]):
                temp_df[col] = temp_df[col].fillna(0).astype(int)

        temp_df.set_index('kd_kab', inplace=True)
        temp_df.sort_index(inplace=True)
        x_labels = temp_df.index.tolist()
        x_pos = np.arange(len(x_labels))

        # Adjust bar width dynamically
        if len(x_pos) == 1:
            bar_width = 0.2
        elif len(x_pos) == 2:
            bar_width = 0.15
        else:
            bar_width = 0.5

        bottom = np.zeros(len(x_pos))
        for col in prefered_status_order:
            axes[i].bar(
                x_pos,
                temp_df[col].values,
                width=bar_width,
                bottom=bottom,
                label=col,
                color=color_map.get(col, 'black'),
                align='center'
            )
            bottom += temp_df[col].values

        # Title with optional date range
        info = survey_collection_df[survey_collection_df['name'] == survey_name]
        if not info.empty:
            start = pd.to_datetime(info['startDate'].values[0]).strftime('%d %b')
            end = pd.to_datetime(info['endDate'].values[0]).strftime('%d %b')
            title = f"{survey_name}\n({start} – {end})"
        else:
            title = survey_name

        axes[i].set_title(title, fontsize=10)
        axes[i].set_ylabel("Jumlah")
        axes[i].set_xticks(x_pos)
        axes[i].set_xticklabels(x_labels, rotation=45, fontsize=8)
        axes[i].grid(True, axis='y', linestyle='--', alpha=0.5)
        if len(x_pos) == 1:
            axes[i].set_xlim(x_pos[0] - 0.5, x_pos[0] + 0.5)

    # Add legend in the last subplot
    legend_ax = axes[n]
    legend_ax.axis('off')
    legend_labels = [col for col in prefered_status_order if col in color_map]
    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[col]) for col in legend_labels]
    legend_ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        loc='center',
        fontsize=8,
        frameon=False
    )

    # Remove extra axes
    for j in range(n + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.figtext(1, 0.05, f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", horizontalalignment='right')
    fig.suptitle("Monitoring Statistik Ekonomi Produksi" if option==1 else "Report User Assignments", fontsize=18)
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])

    # Save once
    plt.savefig(f"images/progress_assignment.png" if option==1 else "images/user_assignment.png", dpi=600, bbox_inches='tight', pad_inches=0)
    plt.show()

def generate_plots_2(df, survey_collection_df, prefered_status_order, option:int, show_ls=None, filename=None, title_map=None):
    if option not in [1, 2]:
        raise ValueError("Parameter 'option' must be either 1 or 2.")
    os.makedirs("images", exist_ok=True)
    plt.rcParams['font.family'] = ['Roboto Condensed', 'Arial Narrow', 'sans-serif']

    if show_ls is None:
        from survey_selector import load_selected_surveys
        show_ls = load_selected_surveys()

    if title_map is None:
        from survey_selector import load_survey_config
        _config = load_survey_config()
        title_map = {e['name']: e['title'] for e in _config if e.get('title')}

    import json, os as _os
    _cfg_path = "input/survey_config.json"
    _top = json.load(open(_cfg_path)) if _os.path.exists(_cfg_path) else {}
    _chart_title = _top.get("chart_title", "Monitoring Statistik Industri")
    _user_title = _top.get("user_assignment_title", "Report User Assignments")

    excluded_cols = {'kd_kab', 'time_stamp', 'name', 'prov_id', 'total', 'assigned', 'have-not-assigned', 'type'}
    if option == 1:
        known = [col for col in prefered_status_order if col in df.columns]
        known_set = set(known)
        extra = [col for col in df.columns if col not in known_set and col not in excluded_cols]
        prefered_status_order = known + extra
    else:
        prefered_status_order = ['assigned', 'have-not-assigned']

    if option==1:
        color_map = {col: get_color(col) for col in df.columns if col not in ['kd_kab', 'time_stamp', 'name', 'prov_id', 'total']}
    else:
        color_map = {'assigned': '#B5EAD7', 'have-not-assigned': '#E57373'}

    n = len(show_ls)
    cols = 2
    total_plots = n + 1  # +1 for legend
    rows = math.ceil(total_plots / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 6, rows * 4))
    axes = axes.flatten()

    for i, survey_name in enumerate(show_ls):
        temp_df = df.loc[
            df['name'] == survey_name,
            ['kd_kab'] + prefered_status_order
        ].copy()

        # Clean numeric columns
        for col in prefered_status_order:
            if pd.api.types.is_numeric_dtype(temp_df[col]):
                temp_df[col] = temp_df[col].fillna(0).astype(int)

        temp_df.set_index('kd_kab', inplace=True)
        temp_df.sort_index(inplace=True)
        x_labels = temp_df.index.tolist()
        x_pos = np.arange(len(x_labels))

        # Adjust bar width dynamically
        if len(x_pos) == 1:
            bar_width = 0.2
        elif len(x_pos) == 2:
            bar_width = 0.15
        else:
            bar_width = 0.5

        bottom = np.zeros(len(x_pos))
        for col in prefered_status_order:
            values = temp_df[col].values

            bars = axes[i].bar(
                x_pos,
                values,
                width=bar_width,
                bottom=bottom,
                label=col,
                color=color_map.get(col, 'black'),
                align='center'
            )

            # Add labels inside each stacked segment
            for j, v in enumerate(values):
                if v > 0:
                    y_center = bottom[j] + v / 2
                    axes[i].text(
                        x_pos[j],
                        y_center,
                        str(v),
                        ha='center',
                        va='center',
                        fontsize=7,
                        color='black'
                    )

            bottom += values

        # Title with optional date range
        display_title = title_map.get(survey_name, survey_name)
        info = survey_collection_df[survey_collection_df['name'] == survey_name]
        if not info.empty:
            start = pd.to_datetime(info['startDate'].values[0]).strftime('%d %b')
            end = pd.to_datetime(info['endDate'].values[0]).strftime('%d %b')
            other_jadwal = info['other_jadwal'].values[0] if 'other_jadwal' in info.columns and pd.notna(info['other_jadwal'].values[0]) else "-"

            axes[i].set_title(display_title, fontsize=11, pad=14)
            axes[i].text(
                0.5, 1.02,
                f"[Pencacahan: {start} – {end} {other_jadwal}]",
                transform=axes[i].transAxes,
                ha='center', va='bottom',
                fontsize=8
            )
        else:
            axes[i].set_title(display_title, fontsize=11)
    
        axes[i].set_ylabel("Jumlah")

        eps = 1e-6  # small positive constant
        axes[i].set_yscale(
            "function",
            functions=(
                lambda y: np.power(np.clip(y, eps, None), 2/3),
                lambda y: np.power(np.clip(y, eps, None), 3/2)
            )
        )
        
        axes[i].set_xticks(x_pos)
        axes[i].set_xticklabels(x_labels, rotation=45, fontsize=8)
        axes[i].grid(True, axis='y', linestyle='--', alpha=0.5)
        if len(x_pos) == 1:
            axes[i].set_xlim(x_pos[0] - 0.5, x_pos[0] + 0.5)

    # Add legend with section headers if both pencacahan and pemutakhiran are present
    from matplotlib.patches import Patch
    from config import pemutakhiran_status_order as _pem_order

    legend_ax = axes[n]
    legend_ax.axis('off')

    all_legend_labels = [col for col in prefered_status_order if col in color_map]
    pem_set = set(_pem_order)
    pencacahan_labels = [col for col in all_legend_labels if col not in pem_set]
    pemutakhiran_labels = [col for col in all_legend_labels if col in pem_set]
    has_both = bool(pencacahan_labels) and bool(pemutakhiran_labels)

    spacer = Patch(facecolor='none', edgecolor='none')
    handles, labels = [], []

    if has_both:
        handles.append(spacer)
        labels.append('Pencacahan')
    for col in pencacahan_labels:
        handles.append(plt.Rectangle((0, 0), 1, 1, color=color_map[col]))
        labels.append(col)

    if has_both:
        handles.append(spacer)
        labels.append('Pemutakhiran')
    for col in pemutakhiran_labels:
        handles.append(plt.Rectangle((0, 0), 1, 1, color=color_map[col]))
        labels.append(col)

    legend = legend_ax.legend(
        handles=handles,
        labels=labels,
        loc='center',
        fontsize=8,
        frameon=False,
    )
    if has_both:
        for text in legend.get_texts():
            if text.get_text() in ('Pencacahan', 'Pemutakhiran'):
                text.set_fontweight('bold')
                text.set_fontsize(9)

    # Remove extra axes
    for j in range(n + 1, len(axes)):
        fig.delaxes(axes[j])


    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1:"st", 2:"nd", 3:"rd"}.get(day % 10, "th")
    timestamp = f"{now.day}{suffix} {now.strftime('%b, %Y')} {now.strftime('%I:%M %p')}"

    plt.figtext(
        1, 0.05,
        f"Note *: y-scaled-axis | Last updated: {timestamp}",
        horizontalalignment='right'
    )
    fig.suptitle(_chart_title if option==1 else _user_title, fontsize=18)
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])

    # Save once
    default_name = "images/progress_assignment.png" if option==1 else "images/user_assignment.png"
    plt.savefig(filename or default_name, dpi=600, bbox_inches='tight', pad_inches=0)
    plt.show()