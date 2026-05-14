import yaml
from pydantic import BaseModel
import os

class Config(BaseModel):
    model: str
    api_key: str
    max_turns: int

def load_config():
    with open('config/config.yaml') as f:
        data = yaml.safe_load(f)
    # Expand env vars
    data['api_key'] = os.path.expandvars(data['api_key'])
    return Config(**data)