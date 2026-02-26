from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class JWTToken(BaseModel):
    token: str
    algorithm: str
    
    @property
    def get_algorithm(self):
        return self.algorithm
    
    @property
    def get_token(self):
        return self.token

class DBSettigns(BaseModel):    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_host: str
    
    @property
    def get_db(self):
        return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
    
    
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )
    db: DBSettigns
    jwt: JWTToken
        
settings = Settings()