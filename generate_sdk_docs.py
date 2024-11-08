#! /bin/usr/python
import os
import re
import inspect

import wandb 
import lazydocs

# To do, import this from pyi
__all__ = (
    "__version__",
    "init",
    "finish",
    "setup",
    "login",
    "save",
    "sweep",
    "controller",
    "agent",
    "config",
    "log",
    "summary",
    "Api",
    "Graph",
    "Image",
    "Plotly",
    "Video",
    "Audio",
    "Table",
    "Html",
    "box3d",
    "Object3D",
    "Molecule",
    "Histogram",
    "ArtifactTTL",
    "log_artifact",
    "use_artifact",
    "log_model",
    "use_model",
    "link_model",
    "define_metric",
    "Error",
    "termsetup",
    "termlog",
    "termerror",
    "termwarn",
    "Artifact",
    "Settings",
    "teardown",
    "watch",
    "unwatch",
)



def create_public_api_list(module):
    # Remove any from list that are supposed to be hidden
    dir_output = [name for name in dir(module) if not name.startswith('_')]

    # Return alphabetize the list
    return sorted(list(set(dir_output) and set(__all__)))    


def create_class_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write("\n\n")
        file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1]))
        file.write(generator.class2md(obj))

def create_function_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write("\n\n")
        file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1]))
        file.write(generator.function2md(obj))


def create_markdown(api_list, module, src_base_url):

    # Testing a single gen object
    obj = getattr(module, api_list[1])
    filename = api_list[1] + '.md'

    # Get generator object
    generator = lazydocs.MarkdownGenerator(src_base_url=src_base_url)

    if str(type(obj)) == "<class 'type'>":
        print("This is class")
        create_class_markdown(obj, module, generator, filename=filename)
    elif str(type(obj)) == "<class 'function'>":
        print("This is function")
        create_function_markdown(obj, module, generator, filename=filename)
    else:
        print(f"Skipping {obj}")    



def main():

    module = wandb
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    
    # Get list of public APIs
    api_list = create_public_api_list(module)

    # To do: Get api_list from module
    create_markdown(api_list, module, src_base_url)

if __name__  == "__main__":
    main()