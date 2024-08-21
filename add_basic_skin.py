import tkinter as tk
from tkinter import filedialog

import json
import shutil
from os import path


CMD_INDEX_FOLDER = "cmd_index"
RESOURCE_PACK_FOLDER = "resourcepack"

CUSTOM_FOLDER = "mcimcodistxyz"


root = tk.Tk()
root.withdraw()

print("Please provide the texture you would like to use. (Only .png is supported.)")
texture_file_path = filedialog.askopenfilename(title="Select Texture", filetypes=[("PNG", "*.png")])

print("Using texture at %s" % texture_file_path)

item_to_replace = input("\nItem to Replace (ex. minecraft:dirt): ")
item_to_replace_split = item_to_replace.split(":", 1)
item_to_replace_path = path.join(*item_to_replace_split)

cmd_index_path = path.join(CMD_INDEX_FOLDER, item_to_replace_path) + ".json"

cmd_index = {}
regulars_base_item_model_file_path = path.join(RESOURCE_PACK_FOLDER, "assets", item_to_replace_split[0], "models", "item", item_to_replace_split[-1]) + ".json"
base_item_model_file_path = ""
if path.isfile(cmd_index_path):
    cmd_index = json.load(open(cmd_index_path, "r"))
    base_item_model_file_path = regulars_base_item_model_file_path

if base_item_model_file_path == "" or not path.isfile(base_item_model_file_path):
    print("Please provide the base item model for the item you would like to replace.\n(This can be found at https://misode.github.io/assets/model/, click presets, then the item/ITEMNAME you wanna replace, then the download button in the bottom right.)")
    base_item_model_file_path = filedialog.askopenfilename(title="Select Base Item Model", filetypes=[("JSON", "*.json")])

print("Using base item model at %s." % base_item_model_file_path)

print("In use CMD ids: [%s]" % ", ".join(cmd_index))
cmd_id = input("\nCustomModelData id: ")

existing_cmd = cmd_index.get(cmd_id)
if existing_cmd:
    input("CustomModelData id %s is being used by %s. Continuing will overwrite it.\nPress ENTER to continue." % (cmd_id, existing_cmd.get("name", "INVALID NAME")))

skin_name = input("\nSkin Name: ")
skin_formatted_name = skin_name.replace(" ", "_").replace("(", "").replace(")", "").lower()
skin_desc = input("Skin Description: ")
skin_author = input("Skin Author: ")

# Update cmd index
cmd_index[cmd_id] = {
    "name": skin_name,
    "description": skin_desc,
    "author": skin_author
}

json.dump(cmd_index, open(cmd_index_path, "w"), indent=4)

# Update resouce pack files
base_item_model: dict = json.load(open(base_item_model_file_path, "r"))

item_type = "item"
if base_item_model.get("parent", "").startswith("minecraft:block"):
    item_type = "block"

new_overrides = []

overrides: list = base_item_model.get("overrides", [])
i = 0
for override in overrides:
    if override.get("predicate", {}).get("custom_model_data") == int(cmd_id):
        print("FUCK")
        continue

    new_overrides.append(override)

new_override = {
    "predicate": {
        "custom_model_data": int(cmd_id)
    },
    "model": CUSTOM_FOLDER + ":item/" + skin_formatted_name
}
new_overrides.append(new_override)

base_item_model["overrides"] = new_overrides

json.dump(base_item_model, open(regulars_base_item_model_file_path, "w"), indent=4)

# move texture
texture_folder = "item"
if item_type == "block":
    texture_folder = "block"

new_texture_file_path = path.join(RESOURCE_PACK_FOLDER, "assets", CUSTOM_FOLDER, "textures", texture_folder, skin_formatted_name) + ".png"

shutil.copyfile(texture_file_path, new_texture_file_path)

# custom item model
texture_ref_path = CUSTOM_FOLDER + ":" + texture_folder + "/" + skin_formatted_name

custom_item_textures = {}
if item_type == "block":
    custom_item_textures["all"] = texture_ref_path
else:
    custom_item_textures["layer0"] = texture_ref_path

custom_item_model = {
    "parent": base_item_model.get("parent", "minecraft:item/generated"),
    "textures": custom_item_textures
}

custom_item_model_file_path = path.join(RESOURCE_PACK_FOLDER, "assets", CUSTOM_FOLDER, "models", "item", skin_formatted_name) + ".json"
json.dump(custom_item_model, open(custom_item_model_file_path, "w"), indent=4)