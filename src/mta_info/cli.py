import typer
import logging

logging.basicConfig()
logger = logging.getLogger("mta_info")
logger.setLevel(logging.INFO)


app = typer.Typer()


@app.command()
def open_map():
    """
    Open (in a browser) the custom GoogleMap with all the bus stops
    """
    import subprocess
    from mta_info.utils import map_url

    subprocess.run(["open", map_url])


@app.command()
def update_data():
    """
    Remove all locally-saved data, get the latest from the MTA API,
    and check if there are any changes.
    """
    from mta_info.utils import data_dir, check_for_changes
    from mta_info.create_map_layers import create_layers
    from shutil import rmtree

    try:
        rmtree(data_dir)
    except FileNotFoundError:
        logger.debug(f"{data_dir} already deleted")
    create_layers()
    logger.info("Data updated ✅")
    if check_for_changes():
        logger.info(
            "🚨CHANGES DETECTED🚨! Please review the git diff and update the map"
        )
    else:
        logger.debug("no changes detected")


if __name__ == "__main__":
    app()
