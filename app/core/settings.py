from pydantic_settings import BaseSettings, SettingsConfigDict

class JWTToken(BaseSettings):
    token: str
    
    @property
    def get_token(self):
        return self.token

class DBSettigns(BaseSettings):    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_host: str
    
    @property
    def get_db(self):
        return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
    
    
class Settings:
    model_config = SettingsConfigDict(env_file=".env")
    def __init__(self):        
        self.db = DBSettigns()
        self.jwt = JWTToken()
        
settings = Settings()