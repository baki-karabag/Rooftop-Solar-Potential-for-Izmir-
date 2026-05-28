# Baki Karabağ
# Izmir Rooftop Solar Potential, 2024
#
# Aim:
# This project examines the solar radiation potential of Izmir in 2024.
# It uses daily NASA POWER data and estimates how much electricity
# different rooftop solar panel areas could produce in one year.
#
# Data:
# The data is downloaded from NASA POWER Daily API for the coordinate
# 38.4237 N, 27.1428 E, which approximately represents Izmir city center.
# The solar radiation data is given in kWh/m²/day.
#
# Calculation:
# Estimated annual electricity production is calculated with:
# annual energy = annual solar radiation * panel area * panel efficiency

from pathlib import Path
import json
import urllib.request

import pandas as pd
import matplotlib.pyplot as plt


LATITUDE = 38.4237
LONGITUDE = 27.1428

START_DATE = "20240101"
END_DATE = "20241231"

PANEL_EFFICIENCY = 0.20
HOUSEHOLD_REFERENCE_KWH_YEAR = 2824


def download_data():
    project_folder = Path(__file__).resolve().parent
    data_folder = project_folder / "data"
    data_folder.mkdir(exist_ok=True)

    csv_path = data_folder / "izmir_nasa_power_2024.csv"

    if csv_path.exists():
        return csv_path

    # T2M: temperature at 2 meters above the ground
    # ALLSKY_SFC_SW_DWN: daily solar radiation reaching the surface
    parameters = "T2M,ALLSKY_SFC_SW_DWN"

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={parameters}"
        "&community=RE"
        f"&longitude={LONGITUDE}"
        f"&latitude={LATITUDE}"
        f"&start={START_DATE}"
        f"&end={END_DATE}"
        "&format=JSON"
    )

    print("Downloading data from NASA POWER...")

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    values = data["properties"]["parameter"]

    df = pd.DataFrame({
        "date": list(values["T2M"].keys()),
        "temperature_C": list(values["T2M"].values()),
        "solar_radiation_kWh_m2_day": list(values["ALLSKY_SFC_SW_DWN"].values()),
    })

    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.replace(-999, pd.NA)

    df.to_csv(csv_path, index=False)
    return csv_path


def main():
    print("\nIzmir Rooftop Solar Potential, 2024")
    print("Baki Karabağ")
    print("-" * 45)
    print("Location: Izmir, Turkey")
    print("Coordinates:", LATITUDE, "N,", LONGITUDE, "E")
    print("Data source: NASA POWER Daily API")
    print("Period: 2024")

    csv_path = download_data()
    df = pd.read_csv(csv_path)

    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month

    print("\nFirst rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nSummary:")
    print(df.describe().round(2))

    yearly_average_solar = df["solar_radiation_kWh_m2_day"].mean()
    annual_solar_radiation = df["solar_radiation_kWh_m2_day"].sum()

    # Daily graph shows the seasonal change of solar radiation.
    plt.figure(figsize=(11, 5))
    plt.plot(df["date"], df["solar_radiation_kWh_m2_day"], label="Daily solar radiation")
    plt.axhline(
        yearly_average_solar,
        linestyle="--",
        label=f"Yearly average = {yearly_average_solar:.2f} kWh/m²/day"
    )
    plt.title("Daily Solar Radiation in Izmir, 2024")
    plt.xlabel("Date")
    plt.ylabel("Solar radiation (kWh/m²/day)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Monthly averages make the seasonal pattern easier to see.
    monthly_solar = df.groupby("month")["solar_radiation_kWh_m2_day"].mean()

    plt.figure(figsize=(8, 5))
    plt.bar(monthly_solar.index, monthly_solar.values)
    plt.axhline(
        yearly_average_solar,
        linestyle="--",
        label=f"Yearly average = {yearly_average_solar:.2f} kWh/m²/day"
    )
    plt.title("Monthly Average Solar Radiation in Izmir, 2024")
    plt.xlabel("Month")
    plt.ylabel("Solar radiation (kWh/m²/day)")
    plt.xticks(range(1, 13))
    plt.legend()
    plt.tight_layout()
    plt.show()

    # This graph compares temperature and solar radiation.
    plt.figure(figsize=(8, 5))
    plt.scatter(
        df["temperature_C"],
        df["solar_radiation_kWh_m2_day"],
        alpha=0.7
    )
    plt.title("Temperature and Solar Radiation in Izmir, 2024")
    plt.xlabel("Temperature at 2 m (°C)")
    plt.ylabel("Solar radiation (kWh/m²/day)")
    plt.tight_layout()
    plt.show()

    # The final graph estimates annual electricity production
    # for different rooftop panel areas.
    panel_areas = list(range(1, 31))

    annual_energy = [
        annual_solar_radiation * area * PANEL_EFFICIENCY
        for area in panel_areas
    ]

    required_area = (
        HOUSEHOLD_REFERENCE_KWH_YEAR
        / (annual_solar_radiation * PANEL_EFFICIENCY)
    )

    plt.figure(figsize=(10, 6))
    plt.plot(
        panel_areas,
        annual_energy,
        marker="o",
        label="Estimated annual production"
    )

    plt.axhline(
        HOUSEHOLD_REFERENCE_KWH_YEAR,
        linestyle="--",
        label=f"Household reference = {HOUSEHOLD_REFERENCE_KWH_YEAR} kWh/year"
    )

    plt.axvline(
        required_area,
        linestyle=":",
        label=f"Required panel area ≈ {required_area:.1f} m²"
    )

    plt.title("Rooftop Panel Area and Annual Electricity Production")
    plt.xlabel("Panel area (m²)")
    plt.ylabel("Estimated electricity production (kWh/year)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("\nResults:")
    print("Average daily solar radiation:", round(yearly_average_solar, 2), "kWh/m²/day")
    print("Annual solar radiation:", round(annual_solar_radiation, 2), "kWh/m²/year")
    print("Best month:", monthly_solar.idxmax())
    print("Weakest month:", monthly_solar.idxmin())
    print("Panel efficiency:", int(PANEL_EFFICIENCY * 100), "%")
    print("Household reference:", HOUSEHOLD_REFERENCE_KWH_YEAR, "kWh/year")
    print("Estimated panel area needed:", round(required_area, 2), "m²")

    print("\nPanel area examples:")
    for area in [5, 10, 15, 20, 25, 30]:
        energy = annual_solar_radiation * area * PANEL_EFFICIENCY
        percentage = energy / HOUSEHOLD_REFERENCE_KWH_YEAR * 100
        print(f"{area:2d} m²: {energy:7.1f} kWh/year  ({percentage:5.1f}% of reference)")


if __name__ == "__main__":
    main()
