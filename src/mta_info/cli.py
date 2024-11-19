import typer
import subprocess
from mta_info.create_map_layers import create_layers
from shutil import rmtree
from mta_info.utils import data_dir
import logging

logging.basicConfig()
logger = logging.getLogger("mta_info")
logger.setLevel(logging.INFO)


app = typer.Typer()

map_url = (
    "https://www.google.com/maps/d/u/0/viewer?mid=1Y-euNeFcsu06Zxfdl6u6-sca3Yp-KYY"
)


@app.command()
def open_map():
    subprocess.run(["open", map_url])


@app.command()
def update_data():
    try:
        rmtree(data_dir)
    except FileNotFoundError:
        logger.debug(f"{data_dir} already deleted")
    create_layers()


if __name__ == "__main__":
    app()
