#!/usr/bin/env python
"""
Seed script for Voltana vehicle and charger database.
Run with: python scripts/seed_db.py
"""

import uuid
from datetime import date
from sqlalchemy.orm import Session

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
    """Seed the vehicle database with top Indian EV models."""

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
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 7.4,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
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
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 7.4,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
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
        # Ather
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
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
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
            "dc_charge_port_type": None,
            "max_ac_charge_kw": 3.3,
            "max_dc_charge_kw": None,
            "dc_10_80_time_minutes": None,
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

    # Bangalore-Goa corridor (NH48) - key charging locations
    chargers_data = [
        # Bangalore area
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
        # Tumakuru
        {
            "network_slug": "statiq",
            "name": "Statiq - NH48 Tumakuru",
            "address": "NH48, Tumakuru Bypass",
            "latitude": 13.3409,
            "longitude": 77.1012,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 60.0,
        },
        # Hassan
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
        # Charmadi Ghat area
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Charmadi Ghat",
            "address": "NH73, Charmadi Ghat",
            "latitude": 12.9500,
            "longitude": 75.4500,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 30.0,
        },
        # Mangalore
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
        # Udupi
        {
            "network_slug": "tata-power-ez",
            "name": "Tata Power EZ - Udupi",
            "address": "NH66, Udupi",
            "latitude": 13.3409,
            "longitude": 74.7421,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Karwar
        {
            "network_slug": "chargezone",
            "name": "ChargeZone - Karwar",
            "address": "NH66, Karwar",
            "latitude": 14.8170,
            "longitude": 74.1284,
            "connector_types": [ConnectorType.CCS2, ConnectorType.TYPE2],
            "power_kw": 50.0,
        },
        # Goa - Panjim
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