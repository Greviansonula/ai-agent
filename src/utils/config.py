import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path="src/configs/agent_configs.yaml") -> dict:
    """Load and interpolate configuration from YAML file."""
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    # Interpolate environment variables
    for section in config.values():  
        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, str) and value.startswith("$"):
                    env_var = value[2:-1]  # Remove ${ and }
                    section[key] = os.getenv(env_var)

    return config
