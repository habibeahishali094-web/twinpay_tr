from pydantic import BaseModel, ConfigDict
from typing import Optional

class SettingsUpdate(BaseModel):
    language: Optional[str] = None
    chaos_mode_enabled: Optional[bool] = None
    error_rate: Optional[int] = None
    delay_ms: Optional[int] = None

class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    language: str
    chaos_mode_enabled: bool
    error_rate: int
    delay_ms: int

class ScenarioCreate(BaseModel):
    name: str
    chaos_mode_enabled: bool = True
    error_rate: int = 0
    delay_ms: int = 0

class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    chaos_mode_enabled: bool
    error_rate: int
    delay_ms: int
