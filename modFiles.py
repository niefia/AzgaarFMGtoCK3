import os


def modFile(modname, output_dir, modpath):
    escaped_output_dir = output_dir.replace("\\", "/")
    content = f"""version="1"
tags={{
        "Total Conversion"
}}
name="{modname}"
supported_version="1.3.1"
path="{escaped_output_dir}"
    """

    with open(os.path.join(modpath, f"{modname}.mod"), "w") as f:
        f.write(content)

    with open(os.path.join(output_dir, f"descriptor.mod"), "w") as f:
        f.write(content)


