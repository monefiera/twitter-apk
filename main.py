from apkmirror import Version, Variant
from download_bins import download_apkeditor, download_revanced_bins
import subprocess
from utils import panic
import apkmirror
import os
        
def merge_apk(path: str):
    subprocess.run(["java", "-jar", "./bins/apkeditor.jar", "m", "-i", path]).check_returncode()

def patch_apk(cli: str, integrations: str, patches: str, apk: str, includes: list[str]):
    command = [
        "java", "-jar", cli, "patch", "-b", patches, "-m", integrations, 
        # use j-hc's keystore so we wouldn't need to reinstall
        "--keystore", "ks.keystore", "--keystore-entry-password", "123456789", "--keystore-password", "123456789",
        "--signer", "jhc", "--keystore-entry-alias", "jhc"
    ]

    for i in includes:
        command.append("-i")
        command.append(i)

    command.append(apk)

    subprocess.run(command).check_returncode()


def get_latest_release(versions: list[Version]) -> Version | None:
    for i in versions:
        if i.version.find("release") >= 0:
            return i

if __name__ == "__main__":
    # get latest version
    url: str = "https://www.apkmirror.com/apk/x-corp/twitter/"
    repo_url: str = "crimera/twitter-apk"

    versions = apkmirror.get_versions(url)

    latest_version = get_latest_release(versions)
    if latest_version is None:
        raise Exception("Could not find the latest version")

    latest_version = latest_version

    # only continue if it's a release
    if latest_version.version.find("release") < 0:
        panic("Latest version is not a release version")

    last_build_version = apkmirror.get_last_build_version(repo_url)
    if last_build_version is None:
        panic("Failed to fetch the latest build version")

    # Begin stuff
    if last_build_version != latest_version.version:
        print(f"New version found: {latest_version.version}")
    else:
        panic("No new version found")

    # get bundle and universal variant
    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants: 
        if variant.is_bundle and variant.arcithecture == "universal":
            download_link = variant
            break

    if download_link is None:
        raise Exception("Bundle not Found")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    download_apkeditor()

    # merge apkm
    # merge command java -jar ./bins/APKEditor-1.3.8.jar
    merge_apk("big_file.apkm")

    download_revanced_bins()

    # patch
    patch_apk(
        "bins/cli.jar",
        "bins/integrations.apk",
        "bins/patches.jar",
        "big_file_merged.apk",
        [
            "Enable app downgrading",
            "Hide FAB",
            "Disable chirp font",
            "Add ability to copy media link",
            "Hide Banner",
            "Hide promote button"
            "Hide Community Notes"
            "Delete from database"
        ],
    )