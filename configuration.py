SOURCE = {
    "SDK": {
        "module": "wandb",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.template.pyi",
        "hugo_specs" : {
            "title": "SDK Python Reference",
            "description": "Use during training to log experiments, track metrics, and save model artifacts.",
            "frontmatter": "object_type: api",
            "folder_name": "actions",
        },
    },
    "DATATYPE": {
        "module": "wandb",
        "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.template.pyi",
        "hugo_specs": {
            "title": "Data Types",
            "description": "Defines Data Types for logging interactive visualizations to W&B.",
            "frontmatter": "object_type: data-type",
            "folder_name": "data-type",
            "parent_key": "SDK",  # <- this defines the parent-child relationship
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
}