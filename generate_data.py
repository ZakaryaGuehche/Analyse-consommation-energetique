import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

np.random.seed(42)

BUILDINGS = {
    'Bureau_A': {'type': 'Bureau', 'surface_m2': 2500, 'base_kwh': 45},
    'Bureau_B': {'type': 'Bureau', 'surface_m2': 1800, 'base_kwh': 35},
    'Bureau_C': {'type': 'Bureau', 'surface_m2': 3200, 'base_kwh': 55},
    'Residence_1': {'type': 'Residentiel', 'surface_m2': 1200, 'base_kwh': 20},
    'Residence_2': {'type': 'Residentiel', 'surface_m2': 900, 'base_kwh': 15},
    'Commerce_1': {'type': 'Commercial', 'surface_m2': 800, 'base_kwh': 30},
    'Commerce_2': {'type': 'Commercial', 'surface_m2': 1500, 'base_kwh': 40},
    'Entrepot_1': {'type': 'Industriel', 'surface_m2': 5000, 'base_kwh': 60}
}


def get_temperature(month, hour):
    monthly_avg = {1: 4, 2: 5, 3: 9, 4: 12, 5: 16, 6: 20,
                   7: 22, 8: 22, 9: 18, 10: 13, 11: 8, 12: 5}
    base_temp = monthly_avg[month]
    hour_factor = -3 * np.cos(2 * np.pi * (hour - 14) / 24)
    noise = np.random.normal(0, 2)
    return round(base_temp + hour_factor + noise, 1)


def get_hourly_profile(building_type, hour, is_weekend):
    if building_type == 'Bureau':
        if is_weekend:
            return 0.2
        if 8 <= hour <= 12: return 1.0
        elif 13 <= hour <= 14: return 0.7
        elif 14 <= hour <= 18: return 0.95
        elif 7 <= hour <= 8 or 18 <= hour <= 20: return 0.5
        else: return 0.15
    elif building_type == 'Residentiel':
        if 7 <= hour <= 9: return 0.8
        elif 9 <= hour <= 17: return 0.3 if not is_weekend else 0.6
        elif 18 <= hour <= 22: return 1.0
        elif 22 <= hour or hour <= 6: return 0.2
        else: return 0.4
    elif building_type == 'Commercial':
        if is_weekend and 10 <= hour <= 19: return 1.1
        elif not is_weekend and 9 <= hour <= 20: return 0.9
        elif 7 <= hour <= 9 or 20 <= hour <= 21: return 0.4
        else: return 0.1
    else:
        if is_weekend: return 0.3
        if 6 <= hour <= 22: return 0.85
        else: return 0.25


def generate_energy_data():
    records = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    current = start_date

    while current <= end_date:
        for hour in range(24):
            for building_name, building_info in BUILDINGS.items():
                is_weekend = current.weekday() >= 5
                month = current.month
                temperature = get_temperature(month, hour)
                hour_factor = get_hourly_profile(building_info['type'], hour, is_weekend)

                temp_confort = 20
                temp_diff = abs(temperature - temp_confort)

                if temperature < 15:
                    temp_factor = 1.0 + (temp_diff * 0.04)
                elif temperature > 25:
                    temp_factor = 1.0 + (temp_diff * 0.06)
                else:
                    temp_factor = 1.0

                if month in [11, 12, 1, 2]:
                    season_factor = 1.1
                elif month in [6, 7, 8]:
                    season_factor = 0.95
                else:
                    season_factor = 1.0

                base = building_info['base_kwh']
                conso = base * hour_factor * temp_factor * season_factor
                conso *= np.random.normal(1.0, 0.05)
                conso = max(0.5, round(conso, 2))

                if 6 <= hour <= 22:
                    tarif = 0.1740
                else:
                    tarif = 0.1230

                cout = round(conso * tarif, 2)

                records.append({
                    'datetime': current.replace(hour=hour),
                    'date': current.strftime('%Y-%m-%d'),
                    'heure': hour,
                    'batiment': building_name,
                    'type_batiment': building_info['type'],
                    'surface_m2': building_info['surface_m2'],
                    'consommation_kwh': conso,
                    'temperature_ext': temperature,
                    'cout_euros': cout,
                    'tarif_type': 'Heures Pleines' if 6 <= hour <= 22 else 'Heures Creuses',
                    'jour_semaine': current.strftime('%A'),
                    'est_weekend': is_weekend,
                    'mois': current.month,
                    'trimestre': f'Q{(current.month - 1) // 3 + 1}',
                    'annee': current.year
                })

        current += timedelta(days=1)

    return pd.DataFrame(records)


def main():
    print("=" * 60)
    print("  GENERATION DES DONNEES ENERGETIQUES")
    print("=" * 60)

    os.makedirs('data', exist_ok=True)

    print("\n> Generation en cours (730 jours x 24h x 8 batiments)...")
    print("  Cela peut prendre quelques secondes...\n")

    df = generate_energy_data()

    filepath = 'data/consommation_energie.csv'
    df.to_csv(filepath, index=False, encoding='utf-8')

    print(f"Dataset sauvegarde : {filepath}")
    print(f"\n{'-' * 45}")
    print(f"  Nb enregistrements  : {len(df):,}")
    print(f"  Periode             : {df['date'].min()} -> {df['date'].max()}")
    print(f"  Batiments           : {df['batiment'].nunique()}")
    print(f"  Conso totale        : {df['consommation_kwh'].sum():,.0f} kWh")
    print(f"  Cout total          : {df['cout_euros'].sum():,.0f} EUR")
    print(f"{'-' * 45}")
    print("\nDone!")


if __name__ == '__main__':
    main()