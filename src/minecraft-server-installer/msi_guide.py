from dialog import Dialog
import os


# TODO: implement systemd service and running as separate user

def guide(d: Dialog):
    d.msgbox("Welcome to Minecraft Server Installer by ObsidianPresidium, a TUI guide to install a Minecraft server "
             "on a headless Linux system.")

    code = d.yesno("Do you agree with Minecraft's EULA? (aka.ms/MinecraftEULA)")
    if code != d.OK:
        raise Exception("User does not agree with Minecraft's EULA, and cannot use a Minecraft server.")

    code, tag = d.menu("Which Minecraft server flavor do you want to install?", choices=[
        ("Paper", "papermc.io"),
        ("Fabric", "fabricmc.net")
    ])
    if code == d.OK:
        if tag == "Paper":
            flavor = "paper"
        elif tag == "Fabric":
            flavor = "fabric"
        else:
            flavor = None
    else:
        raise Exception("User cancel")

    code, string = d.inputbox("What server version do you want to install?", init="1.20.6")
    if code == d.OK:
        version = string
    else:
        raise Exception("User cancel")

    code, string = d.inputbox("How much RAM do you want to dedicate to the server (Xmx)", init="2048M")
    if code == d.OK:
        xmx = string
    else:
        raise Exception("User cancel")

    code = d.yesno("Do you also want to define an Xms RAM value for the server? (default no)")
    if code == d.OK:
        code, string = d.inputbox("How much RAM do you want to dedicate to the server (Xms)", init="1024M")
        if code == d.OK:
            xms = string
        else:
            raise Exception("User cancel")
    else:
        xms = None

    code = d.yesno("Use aikar's flags? (docs.papermc.io/paper/aikars-flags) (default yes)")
    if code == d.OK:
        use_aikars_flags = True
    else:
        use_aikars_flags = False

    code, path = d.dselect("/home", title="What directory should the Minecraft server directory be stored in?")
    if code == d.OK:
        code, string = d.inputbox("What should the Minecraft server directory be called (directory name)?", init="minecraft")
        if code == d.OK:
            minecraft_server_path = os.path.join(path, string)
        else:
            raise Exception("User cancel")
    else:
        raise Exception("User cancel")

    code = d.yesno("Symlink minecraft-server with the run.sh executable in /bin/? This will make you able to run the minecraft server by typing minecraft-server in a terminal anywhere. (default yes)")
    if code == d.OK:
        symlink = True
    else:
        symlink = False

    return {
        "flavor": flavor,
        "version": version,
        "xmx": xmx,
        "xms": xms,
        "use_aikars_flags": use_aikars_flags,
        "minecraft_server_path": minecraft_server_path,
        "symlink": symlink
    }
