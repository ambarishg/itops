from pydantic import Field
from pydantic_settings import BaseSettings


class ExtractorConfigs(BaseSettings):
    """The configuration settings for the extractor application"""

    HOST: str = Field(default="")
    DATABASE: str = Field(default="")
    USERNAME_MYSQL: str = Field(default="")
    PASSWORD: str = Field(default="")
    AZURE_BLOB_STORAGE_ACCOUNT: str = Field(default="")
    AZURE_BLOB_STORAGE_CONTAINER: str = Field(default="")
    AZURE_BLOB_STORAGE_KEY: str = Field(default="")

    AZURE_OPENAI_API_KEY: str = Field(default="")
    AZURE_OPENAI_ENDPOINT: str = Field(default="")
    AZURE_OPENAI_DEPLOYMENT_ID: str = Field(default="")