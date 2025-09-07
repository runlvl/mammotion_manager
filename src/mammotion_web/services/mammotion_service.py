from __future__ import annotations

import asyncio
import logging
import time
import secrets
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..config import get_settings


class ServiceError(Exception):
    pass


class AuthError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class CommandError(ServiceError):
    pass


@dataclass
class LastTelemetry:
    battery: Optional[int] = None
    position: Optional[Dict[str, float]] = None
    work_mode: Optional[int] = None
    updated_at: float = 0.0


@dataclass
class AuthSession:
    email: str
    created_at: float = field(default_factory=time.time)
    client: Any = None  # CloudIOTGateway or similar
    manager: Any = None  # MammotionMixedDeviceManager or similar
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    # High-level Mammotion orchestrator (manages MQTT and device managers)
    mammotion: Any = None
    # Cache typed cloud devices by iotId (from ListingDevByAccountResponse.Data.data)
    devices_by_iot: Dict[str, Any] = field(default_factory=dict)
    # Cache per-device managers by iotId
    managers_by_iot: Dict[str, Any] = field(default_factory=dict)
    # Last known good telemetry per device
    last_known_by_iot: Dict[str, LastTelemetry] = field(default_factory=dict)


# In-memory session store (single-process). For multi-worker, replace by shared store.
_SESSION_STORE: Dict[str, AuthSession] = {}


def _new_sid() -> str:
    return secrets.token_urlsafe(32)


def _store_session(session: AuthSession) -> str:
    sid = _new_sid()
    _SESSION_STORE[sid] = session
    return sid


def _get_session(sid: str) -> AuthSession:
    sess = _SESSION_STORE.get(sid)
    if not sess:
        raise AuthError("Session not found or expired")
    return sess


def _delete_session(sid: str) -> None:
    _SESSION_STORE.pop(sid, None)


class MammotionService:
    def __init__(self, region: str = "eu"):
        self.region = region
        self.logger = logging.getLogger(self.__class__.__name__)

    async def login(self, email: str, password: str) -> str:
        """Login against Mammotion Cloud via PyMammotion (EU region)."""
        try:
            # Imports are deferred so that unit tests can mock them easily
            from pymammotion import MammotionHTTP  # type: ignore
            from pymammotion.aliyun.cloud_gateway import CloudIOTGateway  # type: ignore
            from pymammotion.mammotion.devices.mammotion import (  # type: ignore
                MammotionMixedDeviceManager,
            )
        except Exception as e:
            raise AuthError(f"PyMammotion import failed: {e}")

        # Create Mammotion HTTP client and Cloud IoT gateway (EU region enforced upstream by library)
        try:
            mammotion_http = MammotionHTTP()
        except Exception as e:
            raise AuthError(f"Failed to initialize MammotionHTTP: {e}")

        try:
            cloud = CloudIOTGateway(mammotion_http)
        except Exception as e:
            raise AuthError(f"Failed to initialize CloudIOTGateway: {e}")

        # PyMammotion 0.5.14 flow (verified from installed source):
        # 1) Authenticate via HTTP client (sets authorization_code used by get_region)
        try:
            await mammotion_http.login(email, password)
        except Exception as e:
            self.logger.error(f"MammotionHTTP.login failed: {e}")
            raise AuthError("Authentication failed")
        # 2) Discover region using country code (requires authorization_code)
        from ..config import get_settings as _gs
        cc = _gs().COUNTRY_CODE
        try:
            self.logger.info("MammotionService: discovering region...")
            await cloud.get_region(cc)
        except Exception as e:
            self.logger.error(f"get_region failed: {e}")
            raise AuthError(f"Region discovery failed: {e}")
        # 3) Connect (produces connect_response needed by login_by_oauth)
        try:
            self.logger.info("MammotionService: connecting (OA connect)...")
            await cloud.connect()
        except Exception as e:
            self.logger.error(f"connect failed: {e}")
            raise AuthError(f"Connect failed: {e}")
        # 4) Login by OAuth (needs region and connect responses)
        try:
            self.logger.info("MammotionService: login_by_oauth...")
            await cloud.login_by_oauth(cc)
        except Exception as e:
            self.logger.error(f"login_by_oauth failed: {e}")
            raise AuthError(f"OAuth login failed: {e}")
        # 5) Create session by auth code
        try:
            self.logger.info("MammotionService: obtaining session by auth code...")
            await cloud.session_by_auth_code()
        except Exception as e:
            self.logger.error(f"session_by_auth_code failed: {e}")
            raise AuthError(f"Session creation failed: {e}")
        # Required for MQTT setup downstream
        try:
            await cloud.aep_handle()
        except Exception as e:
            self.logger.error(f"aep_handle failed (continuing): {e}")
        self.logger.info("MammotionService: cloud connected and session established.")

        # Initialize Mammotion high-level manager and connect MQTT
        mammotion_obj = None
        try:
            from pymammotion.mammotion.devices.mammotion import Mammotion  # type: ignore
            mammotion_obj = Mammotion()
            # Let Mammotion orchestrate the full cloud + MQTT flow to ensure AEP/session fields are set
            await mammotion_obj.login_and_initiate_cloud(email, password)
            # Wait briefly for MQTT connection
            try:
                mqtt_client = mammotion_obj.mqtt_list.get(email)
                for _ in range(40):  # ~10s max
                    if mqtt_client and mqtt_client.is_connected():
                        break
                    await asyncio.sleep(0.25)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"Mammotion MQTT init failed (continuing with HTTP only): {e}")
            mammotion_obj = None

        # Store session with cloud client; device managers will be created on-demand per device
        session = AuthSession(email=email, client=cloud, manager=None, mammotion=mammotion_obj)
        sid = _store_session(session)
        return sid

    async def list_devices(self, session: AuthSession) -> List[Dict[str, Any]]:
        cloud = session.client
        if cloud is None:
            raise AuthError("Not authenticated")
        # Query devices bound to the account and refresh caches under lock
        async with session.lock:
            # First try via our CloudIOTGateway
            resp = None
            data_dict = None
            try:
                resp = await cloud.list_binding_by_account()
            except Exception as e:
                # Fallback path: try to read listing from the Mammotion orchestrator's cloud client
                self.logger.warning(f"list_binding_by_account failed ({e}); attempting Mammotion fallback")
                try:
                    if session.mammotion is not None:
                        mqtt_client = getattr(session.mammotion, "mqtt_list", {}).get(session.email)
                        if mqtt_client is not None and hasattr(mqtt_client, "cloud_client"):
                            cc = getattr(mqtt_client, "cloud_client", None)
                            if cc is not None and hasattr(cc, "devices_by_account_response") and cc.devices_by_account_response is not None:
                                resp = cc.devices_by_account_response
                            else:
                                # As a last resort, try to connect_iot which also refreshes listing
                                try:
                                    from pymammotion.mammotion.devices.mammotion import Mammotion  # type: ignore
                                    await Mammotion.connect_iot(cc)  # type: ignore[arg-type]
                                    if hasattr(cc, "devices_by_account_response"):
                                        resp = cc.devices_by_account_response
                                except Exception:
                                    pass
                except Exception:
                    pass
                if resp is None:
                    raise ServiceError(f"Geräteliste fehlgeschlagen: {e}")

            # Typed response expected: ListingDevByAccountResponse(code:int, data: Data, id:str)
            if resp is not None and hasattr(resp, "to_dict"):
                try:
                    data_dict = resp.to_dict()
                except Exception:
                    data_dict = None
            if data_dict is None and hasattr(cloud, "devices_by_account_response") and cloud.devices_by_account_response is not None:
                try:
                    data_dict = cloud.devices_by_account_response.to_dict()
                except Exception:
                    data_dict = None

            # Diagnose-Logging for dict view
            if isinstance(data_dict, dict):
                try:
                    self.logger.info(f"Devices response top-level keys: {list(data_dict.keys())}")
                    if "data" in data_dict and isinstance(data_dict["data"], dict):
                        self.logger.info(f"data.keys: {list(data_dict['data'].keys())}")
                except Exception:
                    pass

            # Build a typed list if available to also cache raw Device objects
            typed_devices = []
            try:
                # Prefer the method return value
                if hasattr(resp, "data") and resp.data is not None and hasattr(resp.data, "data"):
                    typed_devices = list(resp.data.data or [])
                # Fallback to attribute on cloud object
                elif hasattr(cloud, "devices_by_account_response") and cloud.devices_by_account_response is not None:
                    d = cloud.devices_by_account_response
                    if hasattr(d, "data") and d.data is not None and hasattr(d.data, "data"):
                        typed_devices = list(d.data.data or [])
            except Exception:
                typed_devices = []

            # Cache typed Device objects by iotId for later manager creation
            session.devices_by_iot.clear()
            for dev in typed_devices:
                try:
                    iot_id_val = getattr(dev, "iotId", None)
                    if iot_id_val:
                        session.devices_by_iot[str(iot_id_val)] = dev
                except Exception:
                    continue

            # Now produce normalized list for UI
            result: List[Dict[str, Any]] = []
            if typed_devices:
                for dev in typed_devices:
                    try:
                        iot_id = getattr(dev, "iotId", None)
                        name = getattr(dev, "nickName", None) or getattr(dev, "deviceName", None) or iot_id
                        model = getattr(dev, "productModel", None) or getattr(dev, "productName", None) or "Unknown"
                        cat = getattr(dev, "categoryName", "") or ""
                        nm = (str(name) or "").lower()
                        mdl = (str(model) or "").lower()
                        catl = (str(cat) or "").lower()
                        is_base = any(k in nm or k in mdl or k in catl for k in ["rtk", "base", "station", "rasenradar"])
                        # Listing does not include live battery; keep None so UI shows '—' for base stations
                        result.append({
                            "id": str(iot_id),
                            "name": str(name) if name is not None else str(iot_id),
                            "model": str(model),
                            "battery": None,
                            "status": "unknown",
                            "position": None,
                            "is_base": bool(is_base),
                        })
                    except Exception:
                        continue
                return result

            # If we couldn't build typed list, fall back to dict heuristics
            if not isinstance(data_dict, dict):
                raise ServiceError("Unerwartete Antwortstruktur der Geräteliste")

            devices_raw = None
            for key in ("data", "devices", "list", "result"):
                if key in data_dict and isinstance(data_dict[key], list):
                    devices_raw = data_dict[key]
                    break
                if key in data_dict and isinstance(data_dict[key], dict) and "data" in data_dict[key] and isinstance(data_dict[key]["data"], list):
                    devices_raw = data_dict[key]["data"]
                    break
            if devices_raw is None:
                # As a last resort, if response is already a list
                if isinstance(data_dict, list):
                    devices_raw = data_dict
                else:
                    devices_raw = []

            for item in devices_raw:
                if not isinstance(item, dict):
                    continue
                # Common fields observed in Aliyun responses
                iot_id = item.get("iotId") or item.get("iot_id") or item.get("id") or item.get("deviceId") or item.get("device_id")
                name = item.get("nickName") or item.get("deviceName") or item.get("name") or iot_id
                model = item.get("productModel") or item.get("model") or item.get("productName") or "Unknown"
                cat = item.get("categoryName") or ""
                nm = (str(name) or "").lower()
                mdl = (str(model) or "").lower()
                catl = (str(cat) or "").lower()
                is_base = any(k in nm or k in mdl or k in catl for k in ["rtk", "base", "station", "rasenradar"])
                # Battery/status may not be present in listing; keep None to display '—'
                battery = item.get("battery") if item.get("battery") is not None else item.get("batteryLevel")
                status = item.get("status") or item.get("work_mode") or "unknown"
                pos = None
                lat = item.get("latitude") or (item.get("position", {}) or {}).get("lat")
                lon = item.get("longitude") or (item.get("position", {}) or {}).get("lon")
                if lat is not None and lon is not None:
                    pos = {"lat": lat, "lon": lon}
                result.append({
                    "id": str(iot_id) if iot_id is not None else name,
                    "name": str(name),
                    "model": str(model),
                    "battery": int(battery) if isinstance(battery, (int, float)) else None,
                    "status": str(status),
                    "position": pos,
                    "is_base": bool(is_base),
                })
            return result

    async def get_device_status(self, session: AuthSession, device_id: str) -> Dict[str, Any]:
        """Return live status if possible; gracefully fall back to listing info."""
        # Try live status via per-device manager
        live: Optional[Dict[str, Any]] = None
        try:
            mgr = await self._get_or_create_manager(session, device_id)

            # 1) Prefer the unified device state exposed by the manager
            state_obj = None
            try:
                state_obj = getattr(mgr, "state")
            except Exception:
                state_obj = None

            battery = None
            status_text = None
            pos = None
            dock_pos = None
            rtk_pos = None
            work_mode_val: Optional[int] = None
            online_bool: Optional[bool] = None

            # Log diagnostic info once per device
            if not hasattr(self, "_diagged"):
                self._diagged = set()  # type: ignore[attr-defined]
            if device_id not in self._diagged:  # type: ignore[operator]
                try:
                    attrs = []
                    for name in ("state", "state_manager", "cloud"):
                        try:
                            val = getattr(mgr, name)
                            attrs.append(f"{name}={type(val).__name__}")
                        except Exception:
                            attrs.append(f"{name}=<err>")
                    self.logger.info(f"Mgr attrs for {device_id}: {', '.join(attrs)}")
                    if state_obj is not None:
                        for sub in ("status_properties", "mqtt_properties", "mow_info", "location"):
                            try:
                                v = getattr(state_obj, sub, None)
                                if v is not None and hasattr(v, "to_dict"):
                                    d = v.to_dict()
                                    self.logger.info(f"state.{sub} keys: {list(d.keys())}")
                            except Exception:
                                pass
                finally:
                    try:
                        self._diagged.add(device_id)  # type: ignore[attr-defined]
                    except Exception:
                        pass

            if state_obj is not None:
                # Extra diagnostics: dump a compact snapshot once
                try:
                    if device_id not in getattr(self, "_diag_state_dumped", set()):
                        sd = None
                        try:
                            sd = state_obj.to_dict()
                        except Exception:
                            sd = None
                        if sd is not None:
                            # Log a compact JSON length and a few interesting extracted values
                            try:
                                batt_hint = _deep_find_first(sd, ["batt", "battery"])
                                stat_hint = _deep_find_first(sd, ["work", "mode", "status"])
                                lat_hint = _deep_find_first(sd, ["latitude", "lat"])
                                lon_hint = _deep_find_first(sd, ["longitude", "lon"])
                                self.logger.info(
                                    f"state.to_dict snapshot ({len(str(sd))} chars) hints: batt={batt_hint}, status={stat_hint}, lat={lat_hint}, lon={lon_hint}"
                                )
                            except Exception:
                                pass
                            try:
                                if not hasattr(self, "_diag_state_dumped"):
                                    self._diag_state_dumped = set()  # type: ignore[attr-defined]
                                self._diag_state_dumped.add(device_id)  # type: ignore[attr-defined]
                            except Exception:
                                pass
                except Exception:
                    pass
                # Try direct location on state first
                try:
                    loc = getattr(state_obj, "location", None)
                    if loc is not None:
                        # device point
                        dev_point = getattr(loc, "device", None)
                        lat = getattr(dev_point, "latitude", None)
                        lon = getattr(dev_point, "longitude", None)
                        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and (lat != 0 or lon != 0):
                            pos = {"lat": float(lat), "lon": float(lon)}
                        # RTK point (record separately)
                        rtk_point = getattr(loc, "RTK", None)
                        lat = getattr(rtk_point, "latitude", None)
                        lon = getattr(rtk_point, "longitude", None)
                        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and (lat != 0 or lon != 0):
                            rtk_pos = {"lat": float(lat), "lon": float(lon)}
                        # dock point (record separately and as fallback for robot only if nothing else)
                        dock = getattr(loc, "dock", None)
                        lat = getattr(dock, "latitude", None)
                        lon = getattr(dock, "longitude", None)
                        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and (lat != 0 or lon != 0):
                            dock_pos = {"lat": float(lat), "lon": float(lon)}
                        if pos is None and dock_pos is not None:
                            pos = dict(dock_pos)
                except Exception:
                    pass
                # Try status_properties
                try:
                    props = getattr(state_obj, "status_properties", None)
                    if props is not None and hasattr(props, "to_dict"):
                        pd = props.to_dict()
                        # Extract battery by key search
                        for k, v in pd.items():
                            if isinstance(v, (int, float)) and "batt" in k.lower():
                                battery = int(v)
                                break
                        # Work mode / status indicator
                        for k, v in pd.items():
                            if (isinstance(v, int) and ("work" in k.lower() or "mode" in k.lower())):
                                work_mode_val = int(v)
                                break
                            if isinstance(v, str) and ("work" in k.lower() or "mode" in k.lower() or k.lower() == "status"):
                                status_text = str(v)
                                break
                        # Position if present
                        lat = pd.get("latitude") or pd.get("lat")
                        lon = pd.get("longitude") or pd.get("lon")
                        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                            pos = {"lat": float(lat), "lon": float(lon)}
                except Exception:
                    pass
                # Fallback to mqtt_properties
                if battery is None or status_text is None:
                    try:
                        mprops = getattr(state_obj, "mqtt_properties", None)
                        if mprops is not None and hasattr(mprops, "to_dict"):
                            md = mprops.to_dict()
                            if battery is None:
                                for k, v in md.items():
                                    if isinstance(v, (int, float)) and "batt" in k.lower():
                                        battery = int(v)
                                        break
                            if work_mode_val is None:
                                for k, v in md.items():
                                    if isinstance(v, int) and ("work" in k.lower() or "mode" in k.lower()):
                                        work_mode_val = int(v)
                                        break
                            if status_text is None and work_mode_val is None:
                                for k, v in md.items():
                                    if isinstance(v, str) and ("work" in k.lower() or "mode" in k.lower() or k.lower() == "status"):
                                        status_text = str(v)
                                        break
                            lat = md.get("latitude") or md.get("lat")
                            lon = md.get("longitude") or md.get("lon")
                            if pos is None and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                                pos = {"lat": float(lat), "lon": float(lon)}
                    except Exception:
                        pass

                # Last resort: deep search in state.to_dict()
                if (battery is None or status_text is None or pos is None or work_mode_val is None) and hasattr(state_obj, "to_dict"):
                    try:
                        sd = state_obj.to_dict()
                        if battery is None:
                            val = _deep_find_first(sd, ["batt", "battery"])
                            if isinstance(val, (int, float)):
                                battery = int(val)
                        if work_mode_val is None:
                            wv = _deep_find_work_mode(sd)
                            if isinstance(wv, int):
                                work_mode_val = int(wv)
                        if status_text is None:
                            # Prefer textual fields; skip booleans
                            val = _deep_find_first(sd, ["mode_text", "work_mode_text", "state_text", "stateName", "status_text", "status_name", "status_str", "status"])
                            if isinstance(val, str):
                                status_text = val
                        if pos is None:
                            lat = _deep_find_first(sd, ["latitude", "lat"])  # type: ignore[assignment]
                            lon = _deep_find_first(sd, ["longitude", "lon"])  # type: ignore[assignment]
                            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                                pos = {"lat": float(lat), "lon": float(lon)}
                    except Exception:
                        pass

            # Read online flag separately (do not convert to status)
            try:
                online = getattr(state_obj, "online", None)
                if isinstance(online, bool):
                    online_bool = bool(online)
            except Exception:
                pass

            # 2) If still empty, attempt cloud->mower model as before
            if battery is None and status_text is None and pos is None:
                cloud_dev = None
                try:
                    cloud_dev = mgr.cloud()
                except Exception:
                    cloud_dev = None
                if cloud_dev is not None:
                    mower_obj = None
                    try:
                        mower_obj = getattr(cloud_dev, "mower", None)
                        if callable(mower_obj):
                            mower_obj = mower_obj()
                    except Exception:
                        mower_obj = None
                    if mower_obj is not None:
                        try:
                            loc = getattr(mower_obj, "location", None)
                            if loc is not None:
                                dev_point = getattr(loc, "device", None)
                                lat = getattr(dev_point, "latitude", None)
                                lon = getattr(dev_point, "longitude", None)
                                if lat is not None and lon is not None:
                                    pos = {"lat": float(lat), "lon": float(lon)}
                        except Exception:
                            pass
                        for path in (
                            ("mower_state", "battery_level"),
                            ("mower_state", "battery"),
                            ("mowing_state", "battery"),
                            ("status_properties", "battery_level"),
                            ("status_properties", "batteryPercent"),
                            ("mqtt_properties", "batteryPercent"),
                        ):
                            try:
                                base = getattr(mower_obj, path[0], None)
                                val = getattr(base, path[1], None) if base is not None else None
                                if isinstance(val, (int, float)):
                                    battery = int(val)
                                    break
                            except Exception:
                                continue
                        for path in (
                            ("mower_state", "work_mode"),
                            ("mowing_state", "work_mode"),
                            ("status_properties", "work_mode"),
                        ):
                            try:
                                base = getattr(mower_obj, path[0], None)
                                val = getattr(base, path[1], None) if base is not None else None
                                if isinstance(val, int):
                                    work_mode_val = int(val)
                                    break
                                if val is not None and status_text is None:
                                    status_text = str(val)
                                    break
                            except Exception:
                                continue

            # Decode work_mode enum if available
            if work_mode_val is not None:
                status_text = _map_work_mode(work_mode_val)
            # Do not treat boolean-ish values as status text; keep None if no work_mode textual mapping

            # Drop invalid or near-zero coordinates (robot, dock, rtk)
            def _clean(p):
                try:
                    if not isinstance(p, dict):
                        return None
                    plat = float(p.get("lat", 0.0))
                    plon = float(p.get("lon", 0.0))
                    if not (-90.0 <= plat <= 90.0 and -180.0 <= plon <= 180.0):
                        return None
                    if abs(plat) < 0.0001 and abs(plon) < 0.0001:
                        return None
                    return {"lat": plat, "lon": plon}
                except Exception:
                    return None
            pos = _clean(pos)
            dock_pos = _clean(dock_pos)
            rtk_pos = _clean(rtk_pos)

            # Update last known cache with live values
            now_ts = time.time()
            try:
                lk = session.last_known_by_iot.get(device_id) or LastTelemetry()
                updated = False
                if isinstance(battery, int):
                    lk.battery = int(battery)
                    updated = True
                if isinstance(work_mode_val, int):
                    lk.work_mode = int(work_mode_val)
                    updated = True
                if isinstance(pos, dict):
                    lk.position = {"lat": float(pos["lat"]), "lon": float(pos["lon"]) }
                    updated = True
                if updated:
                    lk.updated_at = now_ts
                    session.last_known_by_iot[device_id] = lk
            except Exception:
                pass

            # Prefer live position; otherwise use last known and label as cached
            pos_source = None
            pos_out = None
            pos_updated_at = None
            lk = session.last_known_by_iot.get(device_id)
            if isinstance(pos, dict):
                pos_out = pos
                pos_source = "live"
                pos_updated_at = int(now_ts)
            elif lk and lk.position:
                pos_out = lk.position
                pos_source = "cached"
                pos_updated_at = int(lk.updated_at)

            if battery is not None or status_text is not None or pos_out is not None or online_bool is not None:
                live = {
                    "id": device_id,
                    "battery": int(battery) if isinstance(battery, int) else None,
                    "status": status_text,  # only from work_mode mapping
                    "position": pos_out,
                    "position_source": pos_source,
                    "position_updated_at": pos_updated_at,
                    "dock_position": dock_pos,
                    "rtk_position": rtk_pos,
                    "online": online_bool,
                    "updated_at": int(now_ts),
                }
                try:
                    self.logger.info(f"Live status for {device_id}: {live}")
                except Exception:
                    pass
        except NotFoundError:
            # Will fall back below
            pass
        except Exception as e:
            # Log but continue with fallback
            self.logger.debug(f"Live status attempt failed for {device_id}: {e}")

        if live is not None:
            return live

        # Fallback: reuse last listing information
        devices = await self.list_devices(session)
        for d in devices:
            if str(d.get("id")) == str(device_id):
                result = {
                    "id": device_id,
                    "battery": d.get("battery"),
                    "status": d.get("status", "unknown"),
                    "position": d.get("position"),
                    "updated_at": int(time.time()),
                }
                try:
                    self.logger.info(f"Fallback status for {device_id}: {result}")
                except Exception:
                    pass
                return result
        raise NotFoundError("Device not found")

    async def send_command(self, session: AuthSession, device_id: str, command: str) -> None:
        """Best-effort command dispatch via cloud device; fall back to 400 if unsupported."""
        cmd = command.lower().strip()
        mgr = await self._get_or_create_manager(session, device_id)
        cloud_dev = None
        try:
            cloud_dev = mgr.cloud()
        except Exception:
            cloud_dev = None
        if cloud_dev is None:
            raise CommandError("Cloud-Verbindung zum Gerät nicht verfügbar")
        # Some library versions expose high-level methods on the mower/cloud classes; use queue_command otherwise
        try:
            mower_obj = getattr(cloud_dev, "mower", None)
            if callable(mower_obj):
                mower_obj = mower_obj()
        except Exception:
            mower_obj = None
        try:
            if cmd in ("start", "start_mowing"):
                # Try a few plausible entry points
                for path in ("start_map_hash", "start", "start_sync"):
                    target = mower_obj if mower_obj and hasattr(mower_obj, path) else cloud_dev if hasattr(cloud_dev, path) else None
                    if target is not None:
                        res = getattr(target, path)()
                        if asyncio.iscoroutine(res):
                            await res
                        return
                # Fallback: queue a generic command if available
                if hasattr(cloud_dev, "queue_command"):
                    res = cloud_dev.queue_command("start")
                    if asyncio.iscoroutine(res):
                        await res
                    return
            elif cmd in ("pause", "stop"):
                for path in ("pause_device", "stop_device", "stop"):
                    target = mower_obj if mower_obj and hasattr(mower_obj, path) else cloud_dev if hasattr(cloud_dev, path) else None
                    if target is not None:
                        res = getattr(target, path)()
                        if asyncio.iscoroutine(res):
                            await res
                        return
                if hasattr(cloud_dev, "queue_command"):
                    res = cloud_dev.queue_command("stop")
                    if asyncio.iscoroutine(res):
                        await res
                    return
            elif cmd in ("dock", "return", "return_to_dock"):
                for path in ("return_to_dock",):
                    target = mower_obj if mower_obj and hasattr(mower_obj, path) else cloud_dev if hasattr(cloud_dev, path) else None
                    if target is not None:
                        res = getattr(target, path)()
                        if asyncio.iscoroutine(res):
                            await res
                        return
                if hasattr(cloud_dev, "queue_command"):
                    res = cloud_dev.queue_command("return_to_dock")
                    if asyncio.iscoroutine(res):
                        await res
                    return
            else:
                raise CommandError(f"Unbekannter Befehl: {command}")
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Befehl fehlgeschlagen: {e}")

    async def logout(self, session: AuthSession) -> None:
        # Try to close resources gracefully
        for obj in (session.manager, session.client):
            if obj is None:
                continue
            for meth in ("close", "disconnect", "shutdown", "logout"):
                if hasattr(obj, meth):
                    try:
                        res = getattr(obj, meth)()
                        if asyncio.iscoroutine(res):
                            await res
                    except Exception:
                        pass

    async def _get_or_create_manager(self, session: AuthSession, device_id: str):
        """Create and cache a per-device MammotionMixedDeviceManager if needed."""
        cloud = session.client
        if cloud is None:
            raise AuthError("Not authenticated")
        # Fast-path: return cached manager
        async with session.lock:
            mgr = session.managers_by_iot.get(str(device_id))
            if mgr is not None:
                return mgr
            # Ensure we have the typed cloud device cached
            dev = session.devices_by_iot.get(str(device_id))
            if dev is None:
                # Refresh device cache
                await self.list_devices(session)
                dev = session.devices_by_iot.get(str(device_id))
            if dev is None:
                raise NotFoundError(f"Device not found: {device_id}")
            # Ensure identityId is present (required by cloud commands); refresh per-device if missing
            try:
                ident = getattr(dev, "identityId", None)
                if ident is None or str(ident).strip() == "":
                    cloud = session.client
                    if cloud is not None and hasattr(cloud, "list_binding_by_dev"):
                        try:
                            detail = await cloud.list_binding_by_dev(str(device_id))
                            if hasattr(detail, "data") and detail.data and hasattr(detail.data, "data") and detail.data.data:
                                d0 = detail.data.data[0]
                                if getattr(d0, "iotId", None):
                                    dev = d0
                                    session.devices_by_iot[str(device_id)] = d0
                                    self.logger.info(f"Refreshed device {device_id} from list_binding_by_dev; identityId now: {getattr(d0, 'identityId', None)}")
                        except Exception as e:
                            self.logger.warning(f"list_binding_by_dev failed for {device_id}: {e}")
            except Exception:
                pass
            # Use Mammotion high-level orchestrator if available to integrate MQTT
            if session.mammotion is not None:
                try:
                    mqtt_client = getattr(session.mammotion, "mqtt_list", {}).get(session.email)
                except Exception:
                    mqtt_client = None
                try:
                    if mqtt_client is not None and hasattr(session.mammotion, "get_or_create_device_by_name"):
                        mgr = await _maybe_await(session.mammotion.get_or_create_device_by_name(dev, mqtt_client))
                        # Ensure MQTT is connected before requesting sync
                        try:
                            for _ in range(20):  # ~5s
                                if mqtt_client.is_connected():
                                    break
                                await asyncio.sleep(0.25)
                        except Exception:
                            pass
                        # Trigger cloud sync so that state.* gets populated
                        try:
                            await _maybe_await(session.mammotion.start_sync(dev.deviceName, retry=0))  # type: ignore[arg-type]
                        except Exception:
                            pass
                        session.managers_by_iot[str(device_id)] = mgr
                        return mgr
                except Exception:
                    mgr = None
            # Fallback: compose parameters for manager directly
            try:
                from pymammotion.mammotion.devices.mammotion import (
                    MammotionMixedDeviceManager,
                )  # type: ignore
            except Exception as e:
                raise ServiceError(f"PyMammotion import failed: {e}")
            name = getattr(dev, "nickName", None) or getattr(dev, "deviceName", None) or str(device_id)
            try:
                mgr = MammotionMixedDeviceManager(
                    name=str(name),
                    iot_id=str(device_id),
                    cloud_client=cloud,
                    cloud_device=dev,
                )
            except TypeError as e:
                # Older lib versions may accept no-arg and require init; re-raise with context
                raise ServiceError(f"Gerätemanager-Initialisierung fehlgeschlagen: {e}")
            # Optionally start telemetry sync if available
            try:
                cloud_dev = mgr.cloud()
                if cloud_dev is not None and hasattr(cloud_dev, "start_sync"):
                    res = cloud_dev.start_sync()
                    if asyncio.iscoroutine(res):
                        await res
            except Exception:
                pass
            session.managers_by_iot[str(device_id)] = mgr
            return mgr


async def _maybe_list_devices_objects(mgr: Any) -> List[Any]:
    if hasattr(mgr, "get_devices_by_account_response"):
        resp = await _maybe_await(mgr.get_devices_by_account_response())
        if isinstance(resp, (list, tuple)):
            return list(resp)
        devs = getattr(resp, "devices", None)
        if devs is not None:
            return list(devs)
    if hasattr(mgr, "get_devices"):
        devs = await _maybe_await(mgr.get_devices())
        return list(devs)
    return []


def _first_attr(obj: Any, names: List[str]) -> Optional[Any]:
    for n in names:
        if hasattr(obj, n):
            try:
                return getattr(obj, n)
            except Exception:
                continue
    return None


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


def _map_work_mode(value: int) -> str:
    try:
        from pymammotion.utility.constant.device_constant import WorkMode  # type: ignore
        mapping = {
            getattr(WorkMode, "MODE_READY", 11): "standby",
            getattr(WorkMode, "MODE_NOT_ACTIVE", 0): "standby",
            getattr(WorkMode, "MODE_WORKING", 13): "mowing",
            getattr(WorkMode, "MODE_RETURNING", 14): "returning",
            getattr(WorkMode, "MODE_CHARGING", 15): "charging",
            getattr(WorkMode, "MODE_PAUSE", 19): "paused",
            getattr(WorkMode, "MODE_ONLINE", 1): "online",
            getattr(WorkMode, "MODE_OFFLINE", 2): "offline",
            getattr(WorkMode, "MODE_LOCK", 17): "locked",
            getattr(WorkMode, "MODE_UPDATING", 16): "updating",
            getattr(WorkMode, "MODE_OTA_UPGRADE_FAIL", 23): "update_failed",
        }
        return mapping.get(int(value), f"mode_{int(value)}")
    except Exception:
        return f"mode_{int(value)}"


def _deep_find_first(d: Any, keys_substr: List[str]) -> Optional[Any]:
    """Search recursively for a value whose key contains one of substrings.

    Returns the first matching value encountered in DFS order.
    """
    try:
        if isinstance(d, dict):
            for k, v in d.items():
                kl = str(k).lower()
                if any(s in kl for s in keys_substr):
                    return v
                res = _deep_find_first(v, keys_substr)
                if res is not None:
                    return res
        elif isinstance(d, list):
            for item in d:
                res = _deep_find_first(item, keys_substr)
                if res is not None:
                    return res
    except Exception:
        return None
    return None


def _deep_find_work_mode(d: Any) -> Optional[int]:
    """Search recursively for an integer work_mode value.

    This prefers keys like 'work_mode' or 'workmode', but will also accept any key name containing
    both 'work' and 'mode'. Returns the first integer value found.
    """
    try:
        if isinstance(d, dict):
            for k, v in d.items():
                kl = str(k).lower()
                if ("work_mode" in kl or "workmode" in kl or ("work" in kl and "mode" in kl)) and isinstance(v, int):
                    return int(v)
                res = _deep_find_work_mode(v)
                if res is not None:
                    return res
        elif isinstance(d, list):
            for item in d:
                res = _deep_find_work_mode(item)
                if res is not None:
                    return res
    except Exception:
        return None
    return None


# Singleton service used by routers
_service = MammotionService(region=get_settings().REGION)


def get_service() -> MammotionService:
    return _service


def resolve_session(sid: str) -> AuthSession:
    return _get_session(sid)


def create_session_for(email: str, client: Any, manager: Any) -> str:
    return _store_session(AuthSession(email=email, client=client, manager=manager))


def delete_session(sid: str) -> None:
    _delete_session(sid)
