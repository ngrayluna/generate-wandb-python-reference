from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # go up from `generate-wandb-python-reference/config/config.py`

SOURCE = {
    "SDK": {
        "module": "wandb",
        "file_path": BASE_DIR / "wandb" / "wandb" / "__init__.template.pyi",
        "hugo_specs": {
            "title": "Actions",
            "description": "Use during training to log experiments, track metrics, and save model artifacts.",
            "frontmatter": "namespace: python_sdk_actions",
            "folder_name": "global",
        },
    },
    "CUSTOMCHARTS": {
        "module": "wandb.plot",
        "file_path": BASE_DIR / "wandb" / "wandb" / "plot" / "__init__.py",
        "hugo_specs": {
            "title": "Custom Charts",
            "description": "Create custom charts and visualizations.",
            "frontmatter": "namespace: python_sdk_custom_charts",
            "folder_name": "custom-charts",
        },
    },    
    "DATATYPE": {
        "module": "wandb.sdk.data_types",
        "file_path": BASE_DIR / "wandb" / "wandb" / "__init__.template.pyi",
        "hugo_specs": {
            "title": "Data Types",
            "description": "Defines Data Types for logging interactive visualizations to W&B.",
            "frontmatter": "namespace: python_sdk_data_type",
            "folder_name": "data-types",
        },
    },    
    "PUBLIC_API": {
        "module": "wandb.apis.public",
        "file_path": BASE_DIR / "wandb" / "wandb" / "apis" / "public" / "__init__.py",
        "hugo_specs": {
            "title": "Query API",
            "description": "Query and analyze data logged to W&B.",
            "frontmatter": "namespace: public_apis_namespace",
            "folder_name": "public-api",
        },
    },
    "AUTOMATIONS": {
        "module": "wandb.automations",
        "file_path": BASE_DIR / "wandb" / "wandb" / "automations" / "__init__.py",
        "hugo_specs": {
            "title": "Automations",
            "description": "Automate your W&B workflows.",
            "frontmatter": "namespace: automations_namespace",
            "folder_name": "automations",
        },
    },
}