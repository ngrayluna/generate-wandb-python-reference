from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # go up from `generate-wandb-python-reference/config/config.py`

SOURCE = {
    "SDK": {
        "module": "wandb",
        "file_path": BASE_DIR / "wandb" / "wandb" / "__init__.template.pyi",
        "hugo_specs": {
            "title": "Global Functions",
            "description": "Core W&B functions for initializing runs, logging data, and managing experiments.",
            "frontmatter": "object_type: python_sdk_actions",
            "folder_name": "global-functions",
            "weight": 10,
        },
    },
    "ARTIFACT": {
        "module": "wandb.sdk",
        "file_path": BASE_DIR / "wandb" / "wandb" / "sdk" / "artifacts" / "artifact.py",
        "hugo_specs": {
            "title": "Artifact",
            "description": "Manage versioned datasets and models.",
            "frontmatter": "object_type: python_sdk_artifact",
            "folder_name": "artifact",
            "weight": 20,
        },
    },
    "RUN": {
        "module": "wandb.sdk",
        "file_path": BASE_DIR / "wandb" / "wandb" / "sdk" / "wandb_run.py",
        "hugo_specs": {
            "title": "Run",
            "description": "Track and manage experiments.",
            "frontmatter": "object_type: python_sdk_run",
            "folder_name": "run",
            "weight": 30,
        },
    },
    "SETTINGS": {
        "module": "wandb.sdk",
        "file_path": BASE_DIR / "wandb" / "wandb" / "sdk" / "wandb_settings.py",
        "hugo_specs": {
            "title": "Settings",
            "description": "Configure W&B behavior and preferences.",
            "frontmatter": "object_type: python_sdk_settings",
            "folder_name": "settings",
            "weight": 40,
        },
    },
    "CUSTOMCHARTS": {
        "module": "wandb.plot",
        "file_path": BASE_DIR / "wandb" / "wandb" / "plot" / "__init__.py",
        "hugo_specs": {
            "title": "Custom Charts",
            "description": "Create custom charts and visualizations.",
            "frontmatter": "object_type: python_sdk_custom_charts",
            "folder_name": "custom-charts",
            "weight": 80,
        },
    },    
    "DATATYPE": {
        "module": "wandb.sdk.data_types",
        "file_path": BASE_DIR / "wandb" / "wandb" / "__init__.template.pyi",
        "hugo_specs": {
            "title": "Data Types",
            "description": "Defines Data Types for logging interactive visualizations to W&B.",
            "frontmatter": "object_type: python_sdk_data_type",
            "folder_name": "data-types",
            "weight": 70,
        },
    },    
    "PUBLIC_API": {
        "module": "wandb.apis.public",
        "file_path": BASE_DIR / "wandb" / "wandb" / "apis" / "public" / "__init__.py",
        "hugo_specs": {
            "title": "Public API Reference",
            "description": "Query and analyze data logged to W&B.",
            "frontmatter": "object_type: public_apis_namespace",
            "folder_name": "public-api",
            "weight": 90,
        },
    },
    "AUTOMATIONS": {
        "module": "wandb.automations",
        "file_path": BASE_DIR / "wandb" / "wandb" / "automations" / "__init__.py",
        "hugo_specs": {
            "title": "Automations",
            "description": "Automate your W&B workflows.",
            "frontmatter": "object_type: automations_namespace",
            "folder_name": "automations",
            "weight": 100,
        },
    },
    "REPORTS": {
        "module": "wandb_workspaces.reports.v2",
        "file_path": BASE_DIR / "wandb-workspaces" / "wandb_workspaces" / "reports" / "v2" / "__init__.py",
        "hugo_specs": {
            "title": "Reports",
            "description": "Create and manage W&B reports programmatically.",
            "frontmatter": "object_type: python_sdk_reports",
            "folder_name": "reports",
            "weight": 110,
        },
    },
    "WORKSPACES": {
        "module": "wandb_workspaces.workspaces",
        "file_path": BASE_DIR / "wandb-workspaces" / "wandb_workspaces" / "workspaces" / "__init__.py",
        "hugo_specs": {
            "title": "Workspaces",
            "description": "Manage W&B workspaces and dashboards.",
            "frontmatter": "object_type: python_sdk_workspaces",
            "folder_name": "workspaces",
            "weight": 120,
        },
    },
}