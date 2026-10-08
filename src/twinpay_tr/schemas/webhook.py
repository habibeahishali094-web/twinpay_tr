from pydantic import BaseModel

class WebhookEndpointCreate(BaseModel):
    url: str

class WebhookEndpointResponse(BaseModel):
    id: int
    url: str
