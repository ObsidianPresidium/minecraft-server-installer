import shutil
import os
import dialog
import requests
import urllib.request

run_sh = """#!/bin/bash
java $RUNSH_MEMORY $RUNSH_AIKARS_FLAGS -jar $RUNSH_PATH"""

aikars_flags = """-XX:+UseG1GC -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 \
-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 \
-XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 \
-XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 \
-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 \
-Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true"""

def install_dialog():
    yesno = input("Minecraft Server Installer is missing a small dialog dependency. Install it? (sudo privileges required) (Y/N) ")
    if yesno.upper() == "N":
        raise dialog.ExecutableNotFound("Could not find dialog executable, and user refused to install it.")

    if get_distro() == "debian-like":
        os.system("sudo apt install dialog")
    elif get_distro() == "arch-like":
        # Arch-like system
        os.system("sudo pacman -Sy dialog")
    else:
        raise dialog.ExecutableNotFound("Could not find dialog executable, and I don't know how to install it myself.")

def get_distro():
    if shutil.which("apt") is not None:
        return "debian-like"
    elif shutil.which("pacman") is not None:
        return "arch-like"
    else:
        return False

def get_jar(flavor, version, output):
    print("Getting the latest build...")
    if flavor == "paper":
        response = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds")
        if response.status_code != 200:
            raise Exception("Getting latest build from papermc.io failed, did you specify a correct version, are their servers down, do you have a connection to the internet?")
        response = response.json()
        last_build = response["builds"][len(response["builds"]) - 1]["build"]
        file_name = response["builds"][len(response["builds"]) - 1]["downloads"]["application"]["name"]
        url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{last_build}/downloads/{file_name}"
        print("Downloading...")
        urllib.request.urlretrieve(url, output)
    elif flavor == "fabric":
        response = requests.get(f"https://meta.fabricmc.net/v2/versions/loader/{version}")
        if response.status_code != 200:
            raise Exception("Getting latest build from fabricmc.net failed, did you specify a correct version, are their servers down, do you have a connection to the internet?")
        build_response = response.json()
        last_build = build_response[0]["loader"]["version"]
        response = requests.get(f"https://meta.fabricmc.net/v2/versions/installer")
        installer_response = response.json()
        last_installer = installer_response[0]["version"]
        url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{last_build}/{last_installer}/server/jar"
        print("Downloading...")
        urllib.request.urlretrieve(url, output)

def install(o):
    print("Creating server directory")
    mc_path = o["minecraft_server_path"]
    os.makedirs(mc_path)
    get_jar(o["flavor"], o["version"], os.path.join(mc_path, "server.jar"))
    with open(os.path.join(mc_path, "eula.txt"), "w") as f:
        f.write("eula=true")

    new_run_sh = run_sh.replace("$RUNSH_MEMORY", f"-Xmx{o['xmx']} -Xms{o['xms'] if o['xmx'] else '1024M'}")
    new_run_sh = new_run_sh.replace("$RUNSH_PATH", os.path.join(mc_path, "server.jar"))
    new_run_sh = new_run_sh.replace("$RUNSH_AIKARS_FLAGS", aikars_flags) if o["use_aikars_flags"] else new_run_sh.replace("$RUNSH_AIKARS_FLAGS", "")

    print("Writing run.sh and giving correct perms...")
    with open(os.path.join(mc_path, "run.sh"), "w") as f:
        f.write(new_run_sh)
    os.chmod(os.path.join(mc_path, "run.sh"), 744)

    if o["symlink"]:
        print("Symlinking to /bin/minecraft-server...")
        os.symlink(os.path.join(mc_path, "run.sh"), "/bin/minecraft-server")


