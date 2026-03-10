import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import os
import warnings

warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 12

COLORS = {
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'palette': ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b',
                '#ef4444', '#06b6d4', '#ec4899', '#84cc16']
}

os.makedirs('outputs', exist_ok=True)


def separator(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


separator("1. CHARGEMENT DES DONNEES")

df = pd.read_csv('data/consommation_energie.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df['date'] = pd.to_datetime(df['date'])

print(f"Shape : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
print(f"Periode : {df['date'].min().date()} -> {df['date'].max().date()}")
print(f"Batiments : {df['batiment'].nunique()}")
print(f"Conso totale : {df['consommation_kwh'].sum():,.0f} kWh")
print(f"Cout total : {df['cout_euros'].sum():,.0f} EUR")


separator("2. ANALYSE TEMPORELLE")

# Profil horaire
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

types = df['type_batiment'].unique()
for i, btype in enumerate(types):
    mask = df['type_batiment'] == btype
    hourly = df[mask].groupby('heure')['consommation_kwh'].mean()
    axes[0].plot(hourly.index, hourly.values,
                 linewidth=2.5, marker='o', markersize=4,
                 color=COLORS['palette'][i], label=btype)

axes[0].set_xlabel('Heure de la journee', fontsize=13)
axes[0].set_ylabel('Consommation moyenne (kWh)', fontsize=13)
axes[0].set_title('Profil de Consommation Horaire par Type', fontsize=14, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].set_xticks(range(0, 24, 2))
axes[0].grid(True, alpha=0.3)

for label, is_we, color in [('Semaine', False, COLORS['primary']),
                              ('Weekend', True, COLORS['danger'])]:
    mask = df['est_weekend'] == is_we
    hourly = df[mask].groupby('heure')['consommation_kwh'].mean()
    axes[1].plot(hourly.index, hourly.values, linewidth=2.5,
                 marker='o', markersize=4, color=color, label=label)

axes[1].set_xlabel('Heure', fontsize=13)
axes[1].set_ylabel('Consommation moyenne (kWh)', fontsize=13)
axes[1].set_title('Semaine vs Weekend', fontsize=14, fontweight='bold')
axes[1].legend(fontsize=11)
axes[1].set_xticks(range(0, 24, 2))
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/consommation_journaliere.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/consommation_journaliere.png")


# Heatmap horaire
fig, ax = plt.subplots(figsize=(16, 8))

jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
               'Friday', 'Saturday', 'Sunday']
jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi',
            'Vendredi', 'Samedi', 'Dimanche']

heatmap_data = df.pivot_table(
    values='consommation_kwh',
    index='jour_semaine',
    columns='heure',
    aggfunc='mean'
).reindex(jours_ordre)

sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False,
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Consommation moyenne (kWh)', 'shrink': 0.8},
            ax=ax)

ax.set_yticklabels(jours_fr, rotation=0, fontsize=11)
ax.set_xlabel('Heure de la journee', fontsize=13)
ax.set_ylabel('Jour de la semaine', fontsize=13)
ax.set_title('Heatmap de Consommation : Jour x Heure',
             fontsize=15, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('outputs/heatmap_horaire.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/heatmap_horaire.png")


# Saisonnalite
fig, axes = plt.subplots(2, 1, figsize=(16, 12))

monthly = df.groupby([df['date'].dt.to_period('M')]).agg(
    conso_totale=('consommation_kwh', 'sum'),
    conso_moyenne=('consommation_kwh', 'mean'),
    temp_moyenne=('temperature_ext', 'mean'),
    cout_total=('cout_euros', 'sum')
).reset_index()

monthly['mois_str'] = monthly['date'].astype(str)

axes[0].fill_between(range(len(monthly)), monthly['conso_totale'],
                     alpha=0.3, color=COLORS['primary'])
axes[0].plot(range(len(monthly)), monthly['conso_totale'],
             color=COLORS['primary'], linewidth=2.5, marker='o', markersize=5)

axes[0].set_xlabel('Mois', fontsize=12)
axes[0].set_ylabel('Consommation totale (kWh)', fontsize=12)
axes[0].set_title('Consommation Mensuelle Totale', fontsize=14, fontweight='bold')
axes[0].set_xticks(range(len(monthly)))
axes[0].set_xticklabels(monthly['mois_str'], rotation=45, ha='right', fontsize=8)

ax_temp = axes[1]
ax_conso = ax_temp.twinx()

ax_temp.bar(range(len(monthly)), monthly['temp_moyenne'],
            color=COLORS['warning'], alpha=0.4, label='Temperature moy.')
ax_conso.plot(range(len(monthly)), monthly['conso_moyenne'],
              color=COLORS['danger'], linewidth=2.5, marker='s',
              markersize=6, label='Conso. moyenne')

ax_temp.set_xlabel('Mois', fontsize=12)
ax_temp.set_ylabel('Temperature (C)', fontsize=12)
ax_conso.set_ylabel('Conso. moyenne (kWh)', fontsize=12)
ax_temp.set_title('Temperature vs Consommation', fontsize=14, fontweight='bold')
ax_temp.set_xticks(range(len(monthly)))
ax_temp.set_xticklabels(monthly['mois_str'], rotation=45, ha='right', fontsize=8)

lines1, labels1 = ax_temp.get_legend_handles_labels()
lines2, labels2 = ax_conso.get_legend_handles_labels()
ax_temp.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/saisonnalite.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/saisonnalite.png")


separator("3. CORRELATION TEMPERATURE-CONSOMMATION")

corr, p_value = stats.pearsonr(df['temperature_ext'], df['consommation_kwh'])
print(f"Correlation de Pearson : {corr:.4f}")
print(f"P-value               : {p_value:.2e}")

if p_value < 0.05:
    print("Correlation statistiquement significative")

df['temp_range'] = pd.cut(
    df['temperature_ext'],
    bins=[-10, 0, 5, 10, 15, 20, 25, 30, 40],
    labels=['<0', '0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '>30']
)

temp_analysis = df.groupby('temp_range', observed=True).agg(
    conso_moyenne=('consommation_kwh', 'mean'),
    cout_moyen=('cout_euros', 'mean'),
    nb_mesures=('consommation_kwh', 'count')
).round(2)

print(f"\nConsommation par plage de temperature :")
print(temp_analysis.to_string())


separator("4. ANALYSE PAR TYPE DE BATIMENT")

bat_stats = df.groupby('type_batiment').agg(
    conso_totale=('consommation_kwh', 'sum'),
    conso_moyenne=('consommation_kwh', 'mean'),
    cout_total=('cout_euros', 'sum'),
    nb_batiments=('batiment', 'nunique')
).round(2)

bat_stats['conso_par_batiment'] = (bat_stats['conso_totale'] / bat_stats['nb_batiments']).round(0)
bat_stats['cout_par_batiment'] = (bat_stats['cout_total'] / bat_stats['nb_batiments']).round(0)

print("Statistiques par type de batiment :")
print(bat_stats.to_string())


separator("5. IDENTIFICATION DES PICS")

daily = df.groupby('date').agg(
    conso_totale=('consommation_kwh', 'sum'),
    temp_moyenne=('temperature_ext', 'mean')
).reset_index()

seuil = daily['conso_totale'].mean() + 2 * daily['conso_totale'].std()
pics = daily[daily['conso_totale'] > seuil].sort_values('conso_totale', ascending=False)

print(f"Seuil de pic : {seuil:,.0f} kWh/jour")
print(f"Nb de jours en pic : {len(pics)} / {len(daily)}")

fig, ax = plt.subplots(figsize=(16, 7))

ax.plot(daily['date'], daily['conso_totale'],
        color=COLORS['primary'], linewidth=0.8, alpha=0.7)

ma7 = daily['conso_totale'].rolling(7).mean()
ax.plot(daily['date'], ma7, color=COLORS['danger'], linewidth=2.5,
        label='Moyenne mobile 7j')

ax.axhline(seuil, color=COLORS['warning'], linestyle='--',
           linewidth=2, label=f'Seuil pic ({seuil:,.0f} kWh)')

if len(pics) > 0:
    ax.scatter(pics['date'], pics['conso_totale'],
               color=COLORS['danger'], s=60, zorder=5,
               label=f'Pics ({len(pics)} jours)', edgecolors='white')

ax.set_xlabel('Date', fontsize=13)
ax.set_ylabel('Consommation journaliere (kWh)', fontsize=13)
ax.set_title('Consommation Journaliere et Identification des Pics',
             fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/pics_consommation.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/pics_consommation.png")


separator("6. RECOMMANDATIONS")

conso_weekend = df[df['est_weekend']]['consommation_kwh'].sum()
conso_nuit_bureaux = df[
    (df['type_batiment'] == 'Bureau') &
    ((df['heure'] < 7) | (df['heure'] > 20))
]['consommation_kwh'].sum()

conso_totale = df['consommation_kwh'].sum()

eco_weekend = conso_weekend * 0.15
eco_nuit = conso_nuit_bureaux * 0.40
eco_totale = eco_weekend + eco_nuit
eco_euros = eco_totale * 0.15

print("RECOMMANDATIONS :")
print(f"{'-' * 50}")
print(f"  1. Reduire la consommation des bureaux le weekend")
print(f"     Economie : {eco_weekend:,.0f} kWh/an")
print(f"  2. Automatiser l'extinction apres 20h")
print(f"     Economie : {eco_nuit:,.0f} kWh/an")
print(f"  3. Ajuster chauffage/clim selon temperature")
print(f"  4. Decaler les process en heures creuses")
print(f"\n  TOTAL ECONOMIES ESTIMEES :")
print(f"     Energie : {eco_totale:,.0f} kWh/an ({eco_totale/conso_totale*100:.1f}%)")
print(f"     Cout    : {eco_euros:,.0f} EUR/an")

print(f"\n{'=' * 60}")
print(f"  ANALYSE TERMINEE AVEC SUCCES")
print(f"{'=' * 60}")

print(f"\nOutputs generes :")
for f in sorted(os.listdir('outputs')):
    print(f"   > outputs/{f}")