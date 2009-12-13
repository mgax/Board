import yaml

import model

def note_representer(dumper, note):
    return dumper.represent_data({'properties': note._properties,
                                  'children': note._children})
yaml.add_representer(model.Note, note_representer)

def dump(root_note):
    return yaml.dump(root_note, default_flow_style=True, default_style='"')
