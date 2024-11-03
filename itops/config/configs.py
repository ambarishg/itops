from dotenv import load_dotenv
from itops.config.extractor_configs import ExtractorConfigs

status: bool = load_dotenv("../.env")
print(status)
CONFIGS = ExtractorConfigs()