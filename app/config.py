
#Defined class with .env file values details: their expected types, values and default values
#We do that in order to avoid in production crashes if a variable is missing 
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore") #Read from .env
    app_name: str = "Veil"
    debug: bool = False
    secret_key: str
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
settings = Settings() #We create an instance here and import it along the project