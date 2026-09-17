import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.node import Node
from app.models.prediction import Prediction
from app.models.localization import LocalizationResult
from app.models.recommendation import Recommendation
from app.models.alert import Alert
from app.models.sensor_cycle import SensorCycle
from app.models.environment import EnvironmentReading
from app.models.connectivity import ConnectivityLog
from app.models.activity import ActivityLog
from app.models.user import User, UserRole
from app.schemas.dashboard import (
    Coordinates,
    FarmerDashboardResponse,
    FarmerSystemOverviewResponse,
)


class FarmerDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _verify_farm_access(self, farm_id: int, current_user: Optional[User] = None) -> Farm:
        farm = self.db.query(Farm).filter(Farm.farm_id == farm_id).first()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {farm_id} not found"
            )
        if current_user and current_user.role == UserRole.FARMER:
            farmer = self.db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
            if not farmer or farm.farmer_id != farmer.farmer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this farm's dashboard"
                )
        return farm

    def get_dashboard(
        self,
        farm_id: int,
        current_user: Optional[User] = None
    ) -> FarmerDashboardResponse:
        farm = self._verify_farm_access(farm_id, current_user)
        farmer = farm.farmer

        # 1. Parse or synthesize boundary
        boundary_coords: List[Coordinates] = []
        if farm.boundary_geojson:
            try:
                bg = json.loads(farm.boundary_geojson)
                if isinstance(bg, list):
                    for pt in bg:
                        if isinstance(pt, dict) and "lat" in pt and "lng" in pt:
                            boundary_coords.append(Coordinates(lat=pt["lat"], lng=pt["lng"]))
                        elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
                            boundary_coords.append(Coordinates(lat=pt[1], lng=pt[0]))
                elif isinstance(bg, dict) and "coordinates" in bg:
                    # GeoJSON polygon ring
                    ring = bg["coordinates"][0] if bg["type"] == "Polygon" else []
                    for pt in ring:
                        boundary_coords.append(Coordinates(lat=pt[1], lng=pt[0]))
            except Exception:
                boundary_coords = []

        if not boundary_coords:
            # Default boundary box around farm coordinates (~4.6 acres)
            lat, lng = farm.latitude, farm.longitude
            boundary_coords = [
                Coordinates(lat=lat + 0.0014, lng=lng - 0.0011),
                Coordinates(lat=lat + 0.0010, lng=lng + 0.0015),
                Coordinates(lat=lat - 0.0011, lng=lng + 0.0011),
                Coordinates(lat=lat - 0.0007, lng=lng - 0.0015),
                Coordinates(lat=lat + 0.0014, lng=lng - 0.0011),
            ]

        # 2. Nodes and latest node states
        nodes = self.db.query(Node).filter(Node.farm_id == farm_id).order_by(Node.node_id.asc()).all()
        latest_node_states: List[Dict[str, Any]] = []
        total_battery = 0.0
        total_signal = 0.0
        battery_count = 0

        for n in nodes:
            # Fetch latest sensor cycle for readings
            latest_cycle = (
                self.db.query(SensorCycle)
                .filter(SensorCycle.node_id == n.node_id)
                .order_by(desc(SensorCycle.cycle_timestamp))
                .first()
            )

            gas10 = latest_cycle.gas_readings if latest_cycle and latest_cycle.gas_readings else [
                145.2, 138.4, 124.6, 112.8, 98.4, 88.5, 76.2, 65.4, 52.1, 41.8
            ]
            temp = latest_cycle.temperature if latest_cycle else 28.4
            hum = latest_cycle.humidity if latest_cycle else 72.0
            press = latest_cycle.pressure if latest_cycle else 1008.0

            node_dict = {
                "id": n.node_id,
                "node_id": n.node_id,
                "name": n.node_name,
                "status": n.status,
                "battery": round(n.battery_percentage, 1),
                "signal": "Excellent" if n.signal_strength > -70 else "Good" if n.signal_strength > -85 else "Fair",
                "signal_dbm": n.signal_strength,
                "coordinates": {"lat": n.latitude, "lng": n.longitude},
                "last_seen": n.last_seen.strftime("%d %b %Y, %I:%M %p") if n.last_seen else None,
                "firmware_version": n.firmware_version,
                "is_master": n.is_master,
                "readings": {
                    "temperature": round(temp, 1),
                    "humidity": round(hum, 1),
                    "pressure": round(press, 1),
                    "total_voc": round(sum(gas10[:3]) / 3.0, 1),
                    "gas_resistance_10": gas10,
                    "iaq": "Good"
                }
            }
            latest_node_states.append(node_dict)
            total_battery += n.battery_percentage
            total_signal += n.signal_strength
            battery_count += 1

        avg_battery = round(total_battery / max(battery_count, 1), 1) if battery_count > 0 else 90.0
        avg_signal_val = total_signal / max(battery_count, 1) if battery_count > 0 else -75.0
        avg_signal = "Excellent" if avg_signal_val > -70 else "Good" if avg_signal_val > -85 else "Fair"

        # 3. Latest Predictions
        predictions = (
            self.db.query(Prediction)
            .filter(Prediction.farm_id == farm_id)
            .order_by(desc(Prediction.timestamp))
            .limit(10)
            .all()
        )

        all_node_predictions: List[Dict[str, Any]] = []
        latest_pred_dict: Optional[Dict[str, Any]] = None
        detected_diseases: List[str] = []
        highest_conf = 0.0

        # Group by node_id to get latest per node
        seen_nodes = set()
        for p in predictions:
            if p.predicted_class and p.predicted_class != "Rice_Healthy" and p.predicted_class not in detected_diseases:
                detected_diseases.append(p.predicted_class)
            
            pred_item = {
                "prediction_id": p.prediction_id,
                "node_id": p.node_id,
                "predicted_class": p.predicted_class,
                "disease_detected": p.disease_detected,
                "confidence": round(p.confidence * (100.0 if p.confidence <= 1.0 else 1.0), 1),
                "timestamp": p.timestamp.strftime("%d %b %Y, %I:%M %p") if p.timestamp else None,
                "all_class_probabilities": p.all_class_probabilities or p.raw_probabilities,
            }

            if p.node_id not in seen_nodes:
                seen_nodes.add(p.node_id)
                all_node_predictions.append(pred_item)

            if latest_pred_dict is None:
                latest_pred_dict = pred_item
                highest_conf = pred_item["confidence"]

        # 4. Health Status
        if farm.status != "active":
            health_status = "inactive"
        elif len(detected_diseases) > 0:
            health_status = "diseased"
        else:
            health_status = "healthy"

        # 5. Localization & Affected Zone
        latest_loc = (
            self.db.query(LocalizationResult)
            .filter(LocalizationResult.farm_id == farm_id)
            .order_by(desc(LocalizationResult.created_at))
            .first()
        )

        loc_dict = None
        affected_zone_dict = None
        if latest_loc and latest_loc.status == "active":
            loc_dict = {
                "localization_id": latest_loc.localization_id,
                "status": latest_loc.status,
                "estimated_latitude": latest_loc.estimated_latitude,
                "estimated_longitude": latest_loc.estimated_longitude,
                "source_score": latest_loc.source_score,
                "confidence_radius_meters": latest_loc.confidence_radius_meters,
                "trigger_nodes": latest_loc.trigger_nodes,
                "detected_conditions": latest_loc.detected_conditions,
                "affected_zone": latest_loc.affected_zone,
                "created_at": latest_loc.created_at.strftime("%d %b %Y, %I:%M %p")
            }
            affected_zone_dict = latest_loc.affected_zone or {
                "name": "North-East Sector",
                "center": {"lat": latest_loc.estimated_latitude, "lng": latest_loc.estimated_longitude},
                "radius_m": latest_loc.confidence_radius_meters,
                "severity": latest_loc.severity
            }

        # 6. Environment & Wind
        env_reading = (
            self.db.query(EnvironmentReading)
            .filter(EnvironmentReading.farm_id == farm_id)
            .order_by(desc(EnvironmentReading.recorded_at))
            .first()
        )

        temp = env_reading.ambient_temp if env_reading else (latest_node_states[0]["readings"]["temperature"] if latest_node_states else 28.0)
        hum = env_reading.humidity if env_reading else (latest_node_states[0]["readings"]["humidity"] if latest_node_states else 72.0)
        press = env_reading.pressure if env_reading and env_reading.pressure else (latest_node_states[0]["readings"]["pressure"] if latest_node_states else 1008.0)
        wind_speed = env_reading.wind_speed if env_reading else 2.4
        wind_dir = env_reading.wind_direction if env_reading and env_reading.wind_direction else "NE (48°)"

        # 7. Recommendations
        latest_rec = (
            self.db.query(Recommendation)
            .filter(Recommendation.farm_id == farm_id)
            .order_by(desc(Recommendation.created_at))
            .first()
        )
        rec_dict = None
        if latest_rec:
            rec_dict = {
                "recommendation_id": latest_rec.recommendation_id,
                "disease_name": latest_rec.disease_name,
                "title": latest_rec.title,
                "action_type": latest_rec.action_type,
                "details": latest_rec.details,
                "dosage": latest_rec.dosage,
                "urgency": latest_rec.urgency,
                "created_at": latest_rec.created_at.strftime("%d %b %Y, %I:%M %p")
            }

        # 8. Alerts
        alerts = (
            self.db.query(Alert)
            .filter(Alert.farm_id == farm_id)
            .order_by(desc(Alert.created_at))
            .limit(20)
            .all()
        )
        active_alerts_list = []
        unread_count = 0
        for a in alerts:
            if not a.is_read:
                unread_count += 1
            active_alerts_list.append({
                "alert_id": a.alert_id,
                "node_id": a.node_id,
                "type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "is_read": a.is_read,
                "time": a.created_at.strftime("%I:%M %p"),
                "created_at": a.created_at.isoformat(),
            })

        last_update_str = datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p")
        if predictions:
            last_update_str = predictions[0].timestamp.strftime("%d %b %Y, %I:%M %p")

        farmer_dict = {
            "farmer_id": farmer.farmer_id if farmer else 0,
            "full_name": farmer.full_name if farmer else "Farmer",
            "phone": farmer.phone if farmer else "",
            "email": farmer.email if farmer else "",
            "state": farmer.state if farmer else "Maharashtra",
            "district": farmer.district if farmer else "Ahmednagar",
            "address": farmer.address if farmer else "",
        }

        farm_dict = {
            "farm_id": farm.farm_id,
            "name": farm.farm_name,
            "area_acres": farm.area,
            "crop": farm.crop,
            "crop_variety": farm.crop_variety or "Rice (Paddy)",
            "growth_stage": farm.growth_stage or "Vegetative",
            "address": farm.address or "",
            "status": farm.status,
            "coordinates": {"lat": farm.latitude, "lng": farm.longitude},
        }

        weather_summary = {
            "temperature": round(temp, 1),
            "humidity": round(hum, 1),
            "pressure": round(press, 1),
            "wind_speed": wind_speed,
            "wind_direction": wind_dir,
            "weather_condition": "Partly cloudy",
            "soil_moisture": 68.0
        }

        alerts_summary = {
            "total": len(alerts),
            "unread": unread_count,
            "critical": sum(1 for a in alerts if a.severity == "critical"),
            "warning": sum(1 for a in alerts if a.severity == "warning"),
            "info": sum(1 for a in alerts if a.severity == "info")
        }

        recommended_action_summary = (
            rec_dict["details"] if rec_dict and "details" in rec_dict
            else "Crop health baseline nominal. Maintain routine canopy scouting."
        )

        disease_status_str = (
            f"{', '.join(detected_diseases)} Detected" if detected_diseases
            else "Healthy"
        )

        # 24-hour prediction trend
        prediction_trend_24h = []
        for p in reversed(predictions[:12]):
            prediction_trend_24h.append({
                "time": p.timestamp.strftime("%I:%M %p") if p.timestamp else "",
                "confidence": round(p.confidence * (100.0 if p.confidence <= 1.0 else 1.0), 1),
                "condition": p.predicted_class,
                "disease_detected": p.disease_detected
            })

        system_connectivity_summary = {
            "mesh_status": "Operational",
            "active_nodes": sum(1 for n in nodes if n.status == "online"),
            "total_nodes": len(nodes),
            "gateway_status": "Online (4G LTE)",
            "last_sync": last_update_str
        }

        return FarmerDashboardResponse(
            farmer=farmer_dict,
            farm=farm_dict,
            crop=farm.crop,
            crop_variety=farm.crop_variety,
            farm_coordinates=Coordinates(lat=farm.latitude, lng=farm.longitude),
            farm_boundary=boundary_coords,
            health_status=health_status,
            latest_node_states=latest_node_states,
            battery=avg_battery,
            signal=avg_signal,
            latest_prediction=latest_pred_dict,
            confidence=round(highest_conf, 1) if highest_conf > 0 else 92.0,
            all_node_predictions=all_node_predictions,
            detected_diseases=detected_diseases,
            disease_status=disease_status_str,
            localization=loc_dict,
            affected_zone=affected_zone_dict,
            localized_source=loc_dict,
            wind={"speed": wind_speed, "direction": wind_dir, "angle": 48.0},
            wind_speed=wind_speed,
            wind_direction=wind_dir,
            temperature=round(temp, 1),
            humidity=round(hum, 1),
            pressure=round(press, 1),
            soil_moisture=68.0,
            weather_summary=weather_summary,
            alerts_summary=alerts_summary,
            latest_recommendation=rec_dict,
            recommended_action_summary=recommended_action_summary,
            prediction_trend_24h=prediction_trend_24h,
            system_connectivity_summary=system_connectivity_summary,
            active_alerts=active_alerts_list,
            unread_alerts_count=unread_count,
            last_update=last_update_str
        )

    def get_system_overview(
        self,
        farm_id: int,
        current_user: Optional[User] = None
    ) -> FarmerSystemOverviewResponse:
        farm = self._verify_farm_access(farm_id, current_user)
        nodes = self.db.query(Node).filter(Node.farm_id == farm_id).order_by(Node.node_id.asc()).all()

        nodes_summary: Dict[str, Any] = {}
        for i, n in enumerate(nodes):
            key = f"Node {i + 1}"
            latest_cycle = (
                self.db.query(SensorCycle)
                .filter(SensorCycle.node_id == n.node_id)
                .order_by(desc(SensorCycle.cycle_timestamp))
                .first()
            )
            gas10 = latest_cycle.gas_readings if latest_cycle and latest_cycle.gas_readings else [
                145.2, 138.4, 124.6, 112.8, 98.4, 88.5, 76.2, 65.4, 52.1, 41.8
            ]
            temp = latest_cycle.temperature if latest_cycle else 28.4
            hum = latest_cycle.humidity if latest_cycle else 72.0
            press = latest_cycle.pressure if latest_cycle else 1008.0

            nodes_summary[key] = {
                "node_id": n.node_id,
                "name": n.node_name,
                "status": n.status,
                "battery": round(n.battery_percentage, 1),
                "signal": "Excellent" if n.signal_strength > -70 else "Good" if n.signal_strength > -85 else "Fair",
                "signal_dbm": n.signal_strength,
                "firmware": n.firmware_version,
                "is_master": n.is_master,
                "coordinates": {"lat": n.latitude, "lng": n.longitude},
                "last_seen": n.last_seen.strftime("%d %b %Y, %I:%M %p") if n.last_seen else None,
                "sensor_state": "normal" if n.status == "online" else "offline",
                "device_temp": 24,
                "battery_voltage": 5.1,
                "readings": {
                    "temperature": round(temp, 1),
                    "humidity": round(hum, 1),
                    "pressure": round(press, 1),
                    "total_voc": round(sum(gas10[:3]) / 3.0, 1),
                    "gas_resistance_10": gas10,
                }
            }

        # 5G/Connectivity Summary
        conn_log = (
            self.db.query(ConnectivityLog)
            .filter(ConnectivityLog.farm_id == farm_id)
            .order_by(desc(ConnectivityLog.recorded_at))
            .first()
        )
        connectivity_summary = {
            "status": conn_log.status.capitalize() if conn_log else "Connected",
            "carrier": conn_log.carrier if conn_log else "Jio",
            "gateway_type": conn_log.gateway_type if conn_log else "5G",
            "rssi": conn_log.rssi if conn_log else -78,
            "latency_ms": conn_log.latency_ms if conn_log else 18.0,
            "uplink": "8.4 Mbps",
            "downlink": "24.6 Mbps",
            "uptime": "99.8%",
            "module_status": "Operational"
        }

        # Environment & Wind Summary
        env = (
            self.db.query(EnvironmentReading)
            .filter(EnvironmentReading.farm_id == farm_id)
            .order_by(desc(EnvironmentReading.recorded_at))
            .first()
        )
        wind_summary = {
            "speed": env.wind_speed if env else 2.4,
            "direction": env.wind_direction or "NE (48°)" if env else "NE (48°)",
            "angle": 48.0
        }
        environment_summary = {
            "temperature": round(env.ambient_temp, 1) if env else 28.0,
            "humidity": round(env.humidity, 1) if env else 72.0,
            "pressure": round(env.pressure, 1) if env and env.pressure else 1008.0,
            "soil_moisture": round(env.soil_moisture, 1) if env and env.soil_moisture else 72.0
        }

        # Farm Health Summary
        recent_pred = (
            self.db.query(Prediction)
            .filter(Prediction.farm_id == farm_id)
            .order_by(desc(Prediction.timestamp))
            .first()
        )
        farm_health = {
            "status": "diseased" if recent_pred and recent_pred.disease_detected else "healthy",
            "condition": recent_pred.predicted_class if recent_pred else "Rice_Healthy",
            "confidence": round(recent_pred.confidence * (100.0 if recent_pred.confidence <= 1.0 else 1.0), 1) if recent_pred else 92.0
        }

        # Latest activity
        activities = (
            self.db.query(ActivityLog)
            .filter(ActivityLog.farm_id == farm_id)
            .order_by(desc(ActivityLog.created_at))
            .limit(10)
            .all()
        )
        activity_list = []
        for act in activities:
            activity_list.append({
                "activity_id": act.activity_id,
                "action": act.action,
                "details": act.details,
                "created_at": act.created_at.strftime("%d %b %Y, %I:%M %p")
            })

        return FarmerSystemOverviewResponse(
            farm_id=farm_id,
            nodes=nodes_summary,
            connectivity_summary=connectivity_summary,
            wind_summary=wind_summary,
            environment_summary=environment_summary,
            farm_health=farm_health,
            latest_activity=activity_list
        )
