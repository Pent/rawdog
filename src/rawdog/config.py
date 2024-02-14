import yaml

from rawdog.utils import rawdog_dir

config_path = rawdog_dir / "config.yaml"


default_config = {
    "llm_api_key": None,
    "llm_base_url": None,
    "llm_model": "gpt-4-turbo-preview",
    "llm_custom_provider": None,
    "llm_temperature": 1.0,
    "dry_run": False,
}

setting_descriptions = {
    "dry_run": "Print the script before executing and prompt for confirmation.",
}


_config = None


def read_config_file():
    global _config
    if _config is None:
        if config_path.exists():
            with open(config_path, "r") as f:
                _config = yaml.safe_load(f)
            # These fields may be null in older config files
            for field in ("llm_model", "llm_temperature"):
                if not _config.get(field):
                    _config[field] = default_config[field]
        else:
            _config = default_config.copy()
            with open(config_path, "w") as f:
                yaml.safe_dump(_config, f)
    return _config


def add_config_flags_to_argparser(parser):
    for k in default_config.keys():
        normalized = k.replace("_", "-")
        if k in setting_descriptions:
            help_text = setting_descriptions[k]
        else:
            help_text = f"Set the {normalized} config value"
        if default_config[k] is False:
            parser.add_argument(f"--{normalized}", action="store_true", help=help_text)
        else:
            parser.add_argument(f"--{normalized}", default=None, help=help_text)


def get_config(args=None):
    config = read_config_file()
    if args:
        config_args = {
            k.replace("-", "_"): v
            for k, v in vars(args).items()
            if k in default_config and v is not None and v is not False
        }
        config = {**config, **config_args}
    return config