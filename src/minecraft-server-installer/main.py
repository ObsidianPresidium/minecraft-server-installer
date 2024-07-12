from dialog import Dialog
import shutil
import os
import sys
import msi_func as msi_func
import msi_guide as msi_guide




if __name__ == "__main__":
    # check if dialog is installed
    if shutil.which("dialog") is None:
        msi_func.install_dialog()

    d = Dialog(dialog="dialog", autowidgetsize=True)
    d.set_background_title("Minecraft Server Installer")

    if os.geteuid() != 0:
        d.msgbox("Please run this script as root.")
        sys.exit(1)

    msi_func.install(msi_guide.guide(d))

    d.msgbox("Minecraft server has been installed. Your user will need to take ownership of the directory you chose (sudo chown -R [your user] [minecraft directory]). You should be able to start it by running run.sh in this directory.")



