SOURCE = {
    "SDK": {
        "module": "wandb",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.template.pyi",
        "hugo_specs" : {
            "title": "Actions",
            "description": "Use during training to log experiments, track metrics, and save model artifacts.",
            "frontmatter": "object_type: python_sdk_actions",
            "folder_name": "actions",
            "weight": 1,
        },
    },
    "DATATYPE": {
        "module": "wandb.sdk.data_types",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.template.pyi",
        "hugo_specs": {
            "title": "Data Types",
            "description": "Defines Data Types for logging interactive visualizations to W&B.",
            "frontmatter": "object_type: python_sdk_data_type",
            "folder_name": "data-type",
            "weight": 2,
        },
    },
    "LAUNCH_API": {
        "module": "wandb.sdk.launch",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/sdk/launch/__init__.py",
        "hugo_specs": {
            "title": "Launch Library Reference",
            "description": "A collection of launch APIs for W&B.",
            "frontmatter": "object_type: launch_apis_namespace",
            "folder_name": "launch-library",
        },
    },    
    "PUBLIC_API": {
        "module": "wandb.apis.public",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/apis/public/__init__.py",
        "hugo_specs": {
            "title": "Analytics and Query API",
            "description": "Query and analyze data logged to W&B.",
            "frontmatter": "object_type: public_apis_namespace",
            "folder_name": "public-api",
            "weight": 3,
        },
    },
    "AUTOMATIONS" : {
        "module" : "wandb.automations",
        "file_path" : "/Users/noahluna/Documents/GitHub/wandb/wandb/automations/__init__.py",
        "hugo_specs" : {
            "title": "Automations",
            "description": "Automate your W&B workflows.",
            "frontmatter": "object_type: automations_namespace",
            "folder_name": "automations"
        },
    }
}