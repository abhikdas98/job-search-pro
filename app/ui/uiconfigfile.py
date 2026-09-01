from configparser import ConfigParser

class config:
    def __init__(self, config_file="app/ui/uiconfig.ini"):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS").split(", ")

    def get_groq_model_options(self):
        return self.config["DEFAULT"].get("GROQ_MODEL_OPTION").split(", ")

    def get_usecase_options(self):
        return self.config["DEFAULT"].get("USECASE_OPTIONS")

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")
    