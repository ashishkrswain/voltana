#!/usr/bin/env python
"""
Seed script for Voltana vehicle and charger database.
Run with: python scripts/seed_db.py
"""

import uuid
import os
import sys
from datetime import date
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine, Base
from app.models import (
    Vehicle,
    VehicleCategory,
    VehicleStatus,
    EfficiencyCurve,
    EfficiencySource,
    RangeConfidence,
    RangeConfidenceLevel,
    ChargerNetwork,
    Charger,
    ChargerStatus,
    ConnectorType,
)


def seed_vehicles(db: Session):
    """Seed (or refresh) the vehicle database from the India EV catalog.

    The catalog (data/india_ev_catalog.py) is the single source of truth for
    vehicles. This upserts by (make, model, variant, model_year): rows that
    already exist are overwritten with the catalog's current specs so
    corrected connector/range data lands on re-seed.
    """
    import importlib.util

    catalog_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "india_ev_catalog.py")
    spec = importlib.util.spec_from_file_location("india_ev_catalog", catalog_path)
    catalog = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(catalog)

    vehicles_data = catalog.VEHICLES
    CATEGORY_MAP = {
        "four_wheeler": VehicleCategory.FOUR_WHEELER,
        "two_wheeler": VehicleCategory.TWO_WHEELER,
        "three_wheeler": VehicleCategory.THREE_WHEELER,
    }

    for v_data in vehicles_data:
        v_data = dict(v_data)  # don't mutate the catalog module
        v_data["category"] = CATEGORY_MAP[v_data["category"]]
        efficiency_curve = v_data.pop("efficiency_curve", [])
        confidence = v_data.pop("confidence", RangeConfidenceLevel.MEDIUM)

        # Overwrite any existing row with the same identity.
        existing = db.query(Vehicle).filter(
            Vehicle.make == v_data["make"],
            Vehicle.model == v_data["model"],
            Vehicle.variant == v_data["variant"],
            Vehicle.model_year == v_data["model_year"]
        ).first()

        if existing:
            for field, value in v_data.items():
                setattr(existing, field, value)
            vehicle = existing
            db.flush()
            db.query(EfficiencyCurve).filter(EfficiencyCurve.vehicle_id == vehicle.id).delete()
            db.query(RangeConfidence).filter(RangeConfidence.vehicle_id == vehicle.id).delete()
            db.flush()
            action = "Updated"
        else:
            vehicle = Vehicle(**v_data)
            db.add(vehicle)
            db.flush()  # Get the ID
            action = "Added"

        # Re-add efficiency curve. Catalog rows don't ship curves, so synthesize
        # a simple speed-based curve from the single efficiency number:
        #   band @40kph -> base * 0.85, @60kph -> base, @80kph -> base * 1.25.
        if not efficiency_curve:
            base = v_data.get("efficiency_wh_per_km") or 0
            if base:
                efficiency_curve = [
                    (40, round(base * 0.85, 1), EfficiencySource.MANUFACTURER),
                    (60, round(base, 1), EfficiencySource.MANUFACTURER),
                    (80, round(base * 1.25, 1), EfficiencySource.ESTIMATED),
                ]
        for speed, wh_per_km, source in efficiency_curve:
            curve = EfficiencyCurve(
                vehicle_id=vehicle.id,
                speed_band_kmph=speed,
                wh_per_km=wh_per_km,
                source=source
            )
            db.add(curve)

        # Re-add range confidence
        rc = RangeConfidence(vehicle_id=vehicle.id, confidence=confidence)
        db.add(rc)

        print(f"{action}: {v_data['make']} {v_data['model']} {v_data['variant']}")

    # Remove vehicles that are in the DB but no longer in the catalog.
    catalog_keys = {(v["make"], v["model"], v["variant"], v["model_year"]) for v in vehicles_data}
    all_vehicles = db.query(Vehicle).all()
    removed = 0
    for v in all_vehicles:
        key = (v.make, v.model, v.variant, v.model_year)
        if key not in catalog_keys:
            db.delete(v)
            removed += 1
            print(f"Removed (not in catalog): {v.make} {v.model} {v.variant}")

    db.commit()
    print(f"Vehicles seeded: {len(vehicles_data)} (removed {removed} stale)")


def _legacy_vehicle_list():
    """Deprecated inline list kept only as a historical reference."""
    vehicles_data = [
        # Tata
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Tata",
            "model": "Nexon EV",
            "variant": "Long Range",
            "model_year": 2024,
            "battery_capacity_kwh": 40.5,
            "battery_chemistry": "LFP",
            "arai_range_km": 465,
            "real_world_range_km": 350,
            "top_speed_kmph": 150,
            "efficiency_wh_per_km": 115.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 56,
            "price_ex_showroom_inr": 1699000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 95.0, EfficiencySource.MANUFACTURER),
                (60, 115.0, EfficiencySource.MANUFACTURER),
                (80, 145.0, EfficiencySource.MANUFACTURER),
                (100, 185.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Tata",
            "model": "Nexon EV",
            "variant": "Medium Range",
            "model_year": 2024,
            "battery_capacity_kwh": 30.0,
            "battery_chemistry": "LFP",
            "arai_range_km": 325,
            "real_world_range_km": 250,
            "top_speed_kmph": 140,
            "efficiency_wh_per_km": 120.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 50,
            "price_ex_showroom_inr": 1499000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 100.0, EfficiencySource.MANUFACTURER),
                (60, 120.0, EfficiencySource.MANUFACTURER),
                (80, 150.0, EfficiencySource.MANUFACTURER),
                (100, 195.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Tata",
            "model": "Tiago EV",
            "variant": "Long Range",
            "model_year": 2024,
            "battery_capacity_kwh": 24.0,
            "battery_chemistry": "LFP",
            "arai_range_km": 315,
            "real_world_range_km": 230,
            "top_speed_kmph": 120,
            "efficiency_wh_per_km": 105.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 25.0,
            "dc_10_80_time_minutes": 57,
            "price_ex_showroom_inr": 999000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 85.0, EfficiencySource.MANUFACTURER),
                (60, 105.0, EfficiencySource.MANUFACTURER),
                (80, 135.0, EfficiencySource.MANUFACTURER),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Tata",
            "model": "Punch EV",
            "variant": "Long Range",
            "model_year": 2024,
            "battery_capacity_kwh": 35.0,
            "battery_chemistry": "LFP",
            "arai_range_km": 421,
            "real_world_range_km": 320,
            "top_speed_kmph": 140,
            "efficiency_wh_per_km": 110.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 55,
            "price_ex_showroom_inr": 1399000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 90.0, EfficiencySource.MANUFACTURER),
                (60, 110.0, EfficiencySource.MANUFACTURER),
                (80, 140.0, EfficiencySource.MANUFACTURER),
                (100, 180.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        # MG
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "MG",
            "model": "ZS EV",
            "variant": "Long Range",
            "model_year": 2024,
            "battery_capacity_kwh": 50.3,
            "battery_chemistry": "NMC",
            "arai_range_km": 461,
            "real_world_range_km": 360,
            "top_speed_kmph": 140,
            "efficiency_wh_per_km": 140.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.4,
            "max_dc_charge_kw": 76.0,
            "dc_10_80_time_minutes": 60,
            "price_ex_showroom_inr": 2299000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 115.0, EfficiencySource.MANUFACTURER),
                (60, 140.0, EfficiencySource.MANUFACTURER),
                (80, 175.0, EfficiencySource.MANUFACTURER),
                (100, 220.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "MG",
            "model": "Comet EV",
            "variant": "Standard",
            "model_year": 2024,
            "battery_capacity_kwh": 17.3,
            "battery_chemistry": "LFP",
            "arai_range_km": 230,
            "real_world_range_km": 170,
            "top_speed_kmph": 100,
            "efficiency_wh_per_km": 100.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
            "price_ex_showroom_inr": 799000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 80.0, EfficiencySource.MANUFACTURER),
                (60, 100.0, EfficiencySource.MANUFACTURER),
                (80, 130.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Mahindra
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Mahindra",
            "model": "XUV400",
            "variant": "EL Pro",
            "model_year": 2024,
            "battery_capacity_kwh": 39.4,
            "battery_chemistry": "LFP",
            "arai_range_km": 456,
            "real_world_range_km": 340,
            "top_speed_kmph": 150,
            "efficiency_wh_per_km": 115.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 50,
            "price_ex_showroom_inr": 1699000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 95.0, EfficiencySource.MANUFACTURER),
                (60, 115.0, EfficiencySource.MANUFACTURER),
                (80, 145.0, EfficiencySource.MANUFACTURER),
                (100, 185.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Mahindra",
            "model": "XUV400",
            "variant": "EC Pro",
            "model_year": 2024,
            "battery_capacity_kwh": 34.5,
            "battery_chemistry": "LFP",
            "arai_range_km": 375,
            "real_world_range_km": 280,
            "top_speed_kmph": 150,
            "efficiency_wh_per_km": 125.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 50,
            "price_ex_showroom_inr": 1599000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 105.0, EfficiencySource.MANUFACTURER),
                (60, 125.0, EfficiencySource.MANUFACTURER),
                (80, 155.0, EfficiencySource.MANUFACTURER),
                (100, 195.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        # Hyundai
        {
            "category": VehicleCategory.FOUR_WHEELER,
            "make": "Hyundai",
            "model": "Kona Electric",
            "variant": "Long Range",
            "model_year": 2024,
            "battery_capacity_kwh": 39.2,
            "battery_chemistry": "NMC",
            "arai_range_km": 452,
            "real_world_range_km": 340,
            "top_speed_kmph": 167,
            "efficiency_wh_per_km": 115.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 7.2,
            "max_dc_charge_kw": 50.0,
            "dc_10_80_time_minutes": 57,
            "price_ex_showroom_inr": 2399000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 95.0, EfficiencySource.MANUFACTURER),
                (60, 115.0, EfficiencySource.MANUFACTURER),
                (80, 145.0, EfficiencySource.MANUFACTURER),
                (100, 190.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        # Ola
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Ola Electric",
            "model": "S1 Pro",
            "variant": "Gen 2",
            "model_year": 2024,
            "battery_capacity_kwh": 4.0,
            "battery_chemistry": "NMC",
            "arai_range_km": 195,
            "real_world_range_km": 140,
            "top_speed_kmph": 120,
            "efficiency_wh_per_km": 28.5,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "Type 6",
            "max_ac_charge_kw": 7.4,
            "max_dc_charge_kw": 12.0,
            "dc_10_80_time_minutes": 130,
            "price_ex_showroom_inr": 147999,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 22.0, EfficiencySource.MANUFACTURER),
                (60, 28.5, EfficiencySource.MANUFACTURER),
                (80, 38.0, EfficiencySource.MANUFACTURER),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Ola Electric",
            "model": "S1 Air",
            "variant": "Standard",
            "model_year": 2024,
            "battery_capacity_kwh": 3.0,
            "battery_chemistry": "NMC",
            "arai_range_km": 151,
            "real_world_range_km": 110,
            "top_speed_kmph": 90,
            "efficiency_wh_per_km": 27.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "Type 6",
            "max_ac_charge_kw": 7.4,
            "max_dc_charge_kw": 12.0,
            "dc_10_80_time_minutes": 100,
            "price_ex_showroom_inr": 119999,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 21.0, EfficiencySource.MANUFACTURER),
                (60, 27.0, EfficiencySource.MANUFACTURER),
                (80, 35.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Ather (newer models charge DC on the IS 17017-2-7 "Type 7" port;
        # the home/portable charger uses the Ather socket at 3.3 kW)
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Ather",
            "model": "450X",
            "variant": "Gen 3",
            "model_year": 2024,
            "battery_capacity_kwh": 3.7,
            "battery_chemistry": "NMC",
            "arai_range_km": 150,
            "real_world_range_km": 105,
            "top_speed_kmph": 90,
            "efficiency_wh_per_km": 35.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "Type 7",
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": 6.0,
            "dc_10_80_time_minutes": 100,
            "price_ex_showroom_inr": 139999,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 28.0, EfficiencySource.MANUFACTURER),
                (60, 35.0, EfficiencySource.MANUFACTURER),
                (80, 45.0, EfficiencySource.MANUFACTURER),
            ],
            "confidence": RangeConfidenceLevel.HIGH,
        },
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Ather",
            "model": "450S",
            "variant": "Standard",
            "model_year": 2024,
            "battery_capacity_kwh": 3.0,
            "battery_chemistry": "NMC",
            "arai_range_km": 115,
            "real_world_range_km": 80,
            "top_speed_kmph": 90,
            "efficiency_wh_per_km": 37.5,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "Type 7",
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": 6.0,
            "dc_10_80_time_minutes": 90,
            "price_ex_showroom_inr": 129999,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 30.0, EfficiencySource.MANUFACTURER),
                (60, 37.5, EfficiencySource.MANUFACTURER),
                (80, 48.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # TVS
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "TVS",
            "model": "iQube",
            "variant": "ST",
            "model_year": 2024,
            "battery_capacity_kwh": 4.56,
            "battery_chemistry": "NMC",
            "arai_range_km": 145,
            "real_world_range_km": 100,
            "top_speed_kmph": 82,
            "efficiency_wh_per_km": 45.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.0,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
            "price_ex_showroom_inr": 149999,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 35.0, EfficiencySource.MANUFACTURER),
                (60, 45.0, EfficiencySource.MANUFACTURER),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Bajaj
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Bajaj",
            "model": "Chetak",
            "variant": "Premium 2024",
            "model_year": 2024,
            "battery_capacity_kwh": 3.2,
            "battery_chemistry": "NMC",
            "arai_range_km": 127,
            "real_world_range_km": 90,
            "top_speed_kmph": 73,
            "efficiency_wh_per_km": 35.5,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
            "price_ex_showroom_inr": 135000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 28.0, EfficiencySource.MANUFACTURER),
                (60, 35.5, EfficiencySource.MANUFACTURER),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Hero
        {
            "category": VehicleCategory.TWO_WHEELER,
            "make": "Hero",
            "model": "Vida V1",
            "variant": "Pro",
            "model_year": 2024,
            "battery_capacity_kwh": 3.94,
            "battery_chemistry": "NMC",
            "arai_range_km": 165,
            "real_world_range_km": 115,
            "top_speed_kmph": 80,
            "efficiency_wh_per_km": 34.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
            "price_ex_showroom_inr": 145000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (40, 27.0, EfficiencySource.MANUFACTURER),
                (60, 34.0, EfficiencySource.MANUFACTURER),
                (80, 44.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Mahindra Treo Zor (3W autorickshaw)
        {
            "category": VehicleCategory.THREE_WHEELER,
            "make": "Mahindra",
            "model": "Treo Zor",
            "variant": "Freight",
            "model_year": 2024,
            "battery_capacity_kwh": 9.0,
            "battery_chemistry": "LFP",
            "arai_range_km": 130,
            "real_world_range_km": 95,
            "top_speed_kmph": 50,
            "efficiency_wh_per_km": 90.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": 15.0,
            "dc_10_80_time_minutes": 55,
            "price_ex_showroom_inr": 320000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (30, 85.0, EfficiencySource.MANUFACTURER),
                (50, 95.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Piaggio Ape E-City (3W passenger)
        {
            "category": VehicleCategory.THREE_WHEELER,
            "make": "Piaggio",
            "model": "Ape E-City",
            "variant": "FX Max",
            "model_year": 2024,
            "battery_capacity_kwh": 8.5,
            "battery_chemistry": "LFP",
            "arai_range_km": 120,
            "real_world_range_km": 88,
            "top_speed_kmph": 55,
            "efficiency_wh_per_km": 92.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": 15.0,
            "dc_10_80_time_minutes": 50,
            "price_ex_showroom_inr": 350000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (30, 88.0, EfficiencySource.MANUFACTURER),
                (50, 96.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
        # Bajaj RE EV (3W passenger)
        {
            "category": VehicleCategory.THREE_WHEELER,
            "make": "Bajaj",
            "model": "RE EV",
            "variant": "Cargo",
            "model_year": 2024,
            "battery_capacity_kwh": 7.0,
            "battery_chemistry": "LFP",
            "arai_range_km": 108,
            "real_world_range_km": 78,
            "top_speed_kmph": 55,
            "efficiency_wh_per_km": 88.0,
            "ac_charge_port_type": "Type 2",
            "dc_charge_port_type": "CCS2",
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": 15.0,
            "dc_10_80_time_minutes": 55,
            "price_ex_showroom_inr": 330000,
            "status": VehicleStatus.ACTIVE,
            "source_last_verified": date(2024, 6, 1),
            "efficiency_curve": [
                (30, 84.0, EfficiencySource.MANUFACTURER),
                (50, 92.0, EfficiencySource.ESTIMATED),
            ],
            "confidence": RangeConfidenceLevel.MEDIUM,
        },
    ]

    for v_data in vehicles_data:
        efficiency_curve = v_data.pop("efficiency_curve", [])
        confidence = v_data.pop("confidence", RangeConfidenceLevel.MEDIUM)

        # Check if vehicle already exists
        existing = db.query(Vehicle).filter(
            Vehicle.make == v_data["make"],
            Vehicle.model == v_data["model"],
            Vehicle.variant == v_data["variant"],
            Vehicle.model_year == v_data["model_year"]
        ).first()

        if existing:
            print(f"Skipping existing: {v_data['make']} {v_data['model']} {v_data['variant']}")
            continue

        vehicle = Vehicle(**v_data)
        db.add(vehicle)
        db.flush()  # Get the ID

        # Add efficiency curve
        for speed, wh_per_km, source in efficiency_curve:
            curve = EfficiencyCurve(
                vehicle_id=vehicle.id,
                speed_band_kmph=speed,
                wh_per_km=wh_per_km,
                source=source
            )
            db.add(curve)

        # Add range confidence
        rc = RangeConfidence(vehicle_id=vehicle.id, confidence=confidence)
        db.add(rc)

        print(f"Added: {v_data['make']} {v_data['model']} {v_data['variant']}")

    db.commit()


def seed_chargers(db: Session):
    """Seed charger networks and stations for Bangalore-Goa corridor (NH48)."""

    networks_data = [
        {
            "name": "Bolt.Earth",
            "slug": "bolt-earth",
            "website": "https://bolt.earth",
        },
        {
            "name": "Statiq",
            "slug": "statiq",
            "website": "https://statiq.in",
        },
        {
            "name": "ChargeZone",
            "slug": "chargezone",
            "website": "https://chargezone.in",
        },
        {
            "name": "Tata Power EZ Charge",
            "slug": "tata-power-ez",
            "website": "https://evcharging.tatapower.com",
        },
        {
            "name": "Jio-BP Pulse",
            "slug": "jio-bp-pulse",
            "website": "https://www.jiobp.com",
        },
        {
            "name": "Ather Grid",
            "slug": "ather-grid",
            "website": "https://atherenergy.com/grid",
        },
    ]

    networks = {}
    for n_data in networks_data:
        existing = db.query(ChargerNetwork).filter(ChargerNetwork.slug == n_data["slug"]).first()
        if not existing:
            network = ChargerNetwork(**n_data)
            db.add(network)
            db.flush()
            networks[n_data["slug"]] = network
        else:
            networks[n_data["slug"]] = existing

    db.commit()

    # Bangalore-Goa corridor (NH48 / NH66) - key charging locations
    chargers_data = [
        # Bangalore area
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Indiranagar Hub",
            "address": "100 Feet Rd, Indiranagar, Bangalore",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 60.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Yeshwanthpur NH48 Exit",
            "address": "Tumkur Main Rd, Yeshwanthpur, Bangalore",
            "latitude": 13.0238,
            "longitude": 77.5503,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - Bangalore Electronic City",
            "address": "Electronic City Phase 1, Bangalore",
            "latitude": 12.8456,
            "longitude": 77.6603,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Bangalore Whitefield",
            "address": "Whitefield Main Road, Bangalore",
            "latitude": 12.9698,
            "longitude": 77.7500,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Bangalore Koramangala",
            "address": "Koramangala 5th Block, Bangalore",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Tumakuru / Sira
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - NH48 Highway Hub Nelamangala",
            "address": "NH48 Toll Plaza, Nelamangala",
            "latitude": 13.0968,
            "longitude": 77.3910,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Kunigal Highway Plaza",
            "address": "NH75 / Kunigal Bypass",
            "latitude": 13.0230,
            "longitude": 77.0340,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - NH48 Tumakuru",
            "address": "NH48, Tumakuru Bypass",
            "latitude": 13.3409,
            "longitude": 77.1012,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Sira Highway Stop",
            "address": "NH48, Near Sira Toll Gate",
            "latitude": 13.7435,
            "longitude": 76.9084,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        # Hiriyur & Chitradurga Hub
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Hiriyur Highway Point",
            "address": "NH48 / NH150A Junction, Hiriyur",
            "latitude": 13.9456,
            "longitude": 76.6190,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Chitradurga Bypass",
            "address": "NH48, Chitradurga",
            "latitude": 14.2251,
            "longitude": 76.3980,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Chitradurga Fort View Station",
            "address": "NH48, Near Chitradurga Town Exit",
            "latitude": 14.2380,
            "longitude": 76.4050,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        # Davanagere & Ranebennur
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Davanagere Expressway Hub",
            "address": "NH48 Bypass, Davanagere",
            "latitude": 14.4644,
            "longitude": 75.9218,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Davanagere",
            "address": "NH48 Toll Area, Davanagere",
            "latitude": 14.4710,
            "longitude": 75.9300,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Ranebennur Highway Stop",
            "address": "NH48, Ranebennur",
            "latitude": 14.6238,
            "longitude": 75.6218,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        # Haveri & Hubli-Dharwad Twin City Hub
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Haveri Express Point",
            "address": "NH48, Haveri Bypass",
            "latitude": 14.7954,
            "longitude": 75.4018,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Hubli Central Supercharger",
            "address": "Gokul Road, Hubli",
            "latitude": 15.3647,
            "longitude": 75.1240,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - Hubli Bypass NH48",
            "address": "NH48 Gabbur Cross, Hubli",
            "latitude": 15.3210,
            "longitude": 75.1580,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Dharwad Highway",
            "address": "NH48 PB Road, Dharwad",
            "latitude": 15.4589,
            "longitude": 75.0078,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Alnavar / Mollem / Goa Ghat entry
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Mollem Ghats Entry Hub",
            "address": "NH748, Mollem Checkpost, Goa Border",
            "latitude": 15.3814,
            "longitude": 74.2045,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        # Channarayapatna / Hassan
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Hassan Highway Stop",
            "address": "BM Road, Near Hassan Junction",
            "latitude": 13.0080,
            "longitude": 76.1050,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - NH48 Hassan",
            "address": "NH48, Near Hassan Bypass",
            "latitude": 13.0033,
            "longitude": 76.1004,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "jio-bp-pulse",
            "name": "Jio-BP Pulse - Hassan",
            "address": "NH48, Hassan",
            "latitude": 13.0050,
            "longitude": 76.1020,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Sakleshpur & Ghat Corridor
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Sakleshpur Gateway",
            "address": "Shiradi Ghat Entry, Sakleshpur",
            "latitude": 12.9430,
            "longitude": 75.7860,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Charmadi Ghat",
            "address": "NH73, Charmadi Ghat",
            "latitude": 12.9500,
            "longitude": 75.4500,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 30.0,
        },
        # Mangalore & Coastal NH66
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Mangalore Port City Hub",
            "address": "Kavoor, Mangalore",
            "latitude": 12.9230,
            "longitude": 74.8620,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - Mangalore NH66",
            "address": "NH66, Mangalore",
            "latitude": 12.9141,
            "longitude": 74.8560,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Mangalore",
            "address": "Mangalore City Center",
            "latitude": 12.8767,
            "longitude": 74.8410,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 7.2,
        },
        # Udupi / Kundapura / Bhatkal
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Udupi NH66 Charging Station",
            "address": "NH66 Santhekatte, Udupi",
            "latitude": 13.3750,
            "longitude": 74.7380,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Udupi",
            "address": "NH66, Udupi",
            "latitude": 13.3409,
            "longitude": 74.7421,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Bhatkal NH66 Express",
            "address": "NH66, Bhatkal Bypass",
            "latitude": 13.9820,
            "longitude": 74.5510,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Karwar
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Karwar Coastal Hub",
            "address": "NH66, Near Karwar Beach",
            "latitude": 14.8210,
            "longitude": 74.1310,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Karwar",
            "address": "NH66, Karwar",
            "latitude": 14.8170,
            "longitude": 74.1284,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Goa (Margao & Panjim)
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - South Goa Margao Hub",
            "address": "NH66, Margao, Goa",
            "latitude": 15.2832,
            "longitude": 73.9681,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 60.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth - Panjim City Hub",
            "address": "Patto Plaza, Panjim, Goa",
            "latitude": 15.4950,
            "longitude": 73.8340,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "statiq",
            "name": "Statiq - Panjim",
            "address": "Panjim, Goa",
            "latitude": 15.4909,
            "longitude": 73.8278,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        {
            "network_slug": "jio-bp-pulse",
            "name": "Jio-BP Pulse - Panjim",
            "address": "Panjim, Goa",
            "latitude": 15.4920,
            "longitude": 73.8300,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Goa Airport",
            "address": "Dabolim Airport, Goa",
            "latitude": 15.3800,
            "longitude": 73.8314,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # --- Two-wheeler AC charging points (Ather Grid / Bolt.Earth) ---
        # Real-world 2W intercity charging is slow AC top-ups at grid points in
        # towns — NOT DC fast bays. These follow actual Ather Grid + Bolt.Earth
        # AC placement along the NH48 corridor towns.
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Tumakuru Grid Point",
            "address": "BH Road, Tumakuru",
            "latitude": 13.3379,
            "longitude": 77.1017,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Chitradurga Grid Point",
            "address": "Old PB Road, Chitradurga",
            "latitude": 14.2240,
            "longitude": 76.3995,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Davanagere Grid Point",
            "address": "PJ Extn, Davanagere",
            "latitude": 14.4644,
            "longitude": 75.9218,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Hubballi Grid Point",
            "address": "Club Road, Hubballi",
            "latitude": 15.3647,
            "longitude": 75.1240,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Panjim Grid Point",
            "address": "Panjim, Goa",
            "latitude": 15.4909,
            "longitude": 73.8278,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Nelamangala Cafe Point",
            "address": "NH48, Nelamangala",
            "latitude": 13.1004,
            "longitude": 77.3934,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Sira Highway Stop",
            "address": "NH48, Sira",
            "latitude": 13.7437,
            "longitude": 76.9084,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Chitradurga Bypass",
            "address": "NH48 bypass, Chitradurga",
            "latitude": 14.2240,
            "longitude": 76.4266,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Ranebennur Highway",
            "address": "NH48, Ranebennur",
            "latitude": 14.6152,
            "longitude": 75.6106,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Haveri Grid Point",
            "address": "NH48, Haveri",
            "latitude": 14.7935,
            "longitude": 75.4043,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Dharwad Cafe Point",
            "address": "NH48, Dharwad",
            "latitude": 15.4589,
            "longitude": 75.0078,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Belagavi Grid Point",
            "address": "Belagavi, NH48 spur",
            "latitude": 15.8497,
            "longitude": 74.4977,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Karwar Grid Point",
            "address": "NH66, Karwar",
            "latitude": 14.8170,
            "longitude": 74.1284,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Margao Grid Point",
            "address": "Margao, Goa",
            "latitude": 15.2832,
            "longitude": 73.9862,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        # --- Fill-in points on the Dharwad->Goa (Anmod ghat) leg ---
        # The route from Dharwad heads due west ~15.4N into Goa. A 2W's ~110km
        # real range needs AC points roughly every 70-90km. Khanapur sits just
        # before the Anmod ghats and Molem is inside Goa on that same road.
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid - Khanapur Grid Point",
            "address": "Khanapur, near Anmod Rd",
            "latitude": 15.6300,
            "longitude": 74.5000,
            "connector_types": [ConnectorType.TYPE2],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth AC - Molem Grid Point",
            "address": "NH-748, Molem, Goa",
            "latitude": 15.3397,
            "longitude": 74.2103,
            "connector_types": [ConnectorType.TYPE2, ConnectorType.BHARAT_AC_001],
            "power_kw": 3.3,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Khanapur DC",
            "address": "Khanapur, near Anmod Rd",
            "latitude": 15.6300,
            "longitude": 74.5000,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Dharwad DC",
            "address": "NH48, Dharwad",
            "latitude": 15.4589,
            "longitude": 75.0078,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Molem DC",
            "address": "NH-748, Molem, Goa",
            "latitude": 15.3397,
            "longitude": 74.2103,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        # --- Light-EV DC fast points (Type 6 / Type 7) ---
        # Bolt.Earth Blaze (Type 7), Ola Hypercharger (Type 6), Ather Grid DC.
        # These are the DC fast bays a modern 2W actually uses on a long run.
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Nelamangala DC",
            "address": "NH48, Nelamangala",
            "latitude": 13.1004,
            "longitude": 77.3934,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Tumakuru DC",
            "address": "BH Road, Tumakuru",
            "latitude": 13.3379,
            "longitude": 77.1017,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Chitradurga DC",
            "address": "NH48, Chitradurga",
            "latitude": 14.2240,
            "longitude": 76.3995,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Sira DC",
            "address": "NH48, Sira",
            "latitude": 13.7437,
            "longitude": 76.9084,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Hiriyur DC",
            "address": "NH48, Hiriyur",
            "latitude": 13.9455,
            "longitude": 76.6094,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Sira",
            "address": "NH48, Sira",
            "latitude": 13.7437,
            "longitude": 76.9084,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Ranebennur DC",
            "address": "NH48, Ranebennur",
            "latitude": 14.6152,
            "longitude": 75.6106,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Haveri DC",
            "address": "NH48, Haveri",
            "latitude": 14.7935,
            "longitude": 75.4043,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Ranebennur",
            "address": "NH48, Ranebennur",
            "latitude": 14.6152,
            "longitude": 75.6106,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Davanagere DC",
            "address": "NH48, Davanagere",
            "latitude": 14.4644,
            "longitude": 75.9218,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "bolt-earth",
            "name": "Bolt.Earth Blaze - Hubballi DC",
            "address": "NH48, Hubballi",
            "latitude": 15.3647,
            "longitude": 75.1240,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Tumakuru",
            "address": "BH Road, Tumakuru",
            "latitude": 13.3379,
            "longitude": 77.1017,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Chitradurga",
            "address": "NH48, Chitradurga",
            "latitude": 14.2240,
            "longitude": 76.3995,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Hubballi",
            "address": "NH48, Hubballi",
            "latitude": 15.3647,
            "longitude": 75.1240,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "ather-grid",
            "name": "Ather Grid DC - Panjim",
            "address": "Panjim, Goa",
            "latitude": 15.4909,
            "longitude": 73.8278,
            "connector_types": [ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Tumakuru LEV DC",
            "address": "BH Road, Tumakuru",
            "latitude": 13.3379,
            "longitude": 77.1017,
            "connector_types": [ConnectorType.TYPE6, ConnectorType.TYPE7],
            "power_kw": 30.0,
        },
    ]

    for c_data in chargers_data:
        network = networks.get(c_data.pop("network_slug"))
        if not network:
            continue

        # Check if charger already exists
        existing = db.query(Charger).filter(
            Charger.network_id == network.id,
            Charger.name == c_data["name"]
        ).first()

        if existing:
            print(f"Skipping existing charger: {c_data['name']}")
            continue

        connector_types = c_data.pop("connector_types")
        c_data["connector_types"] = ",".join([c.value for c in connector_types])
        c_data["network_id"] = network.id
        c_data["status"] = ChargerStatus.UNKNOWN

        charger = Charger(**c_data)
        db.add(charger)
        print(f"Added charger: {charger.name}")

    db.commit()


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding vehicles...")
        seed_vehicles(db)

        print("\nSeeding chargers...")
        seed_chargers(db)

        print("\nDone!")
    finally:
        db.close()


if __name__ == "__main__":
    main()