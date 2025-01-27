import argparse
import json
import os
from pathlib import Path

import logging
from R2Log import logger
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from rich.prompt import Prompt
from configparser import ConfigParser

import threading
import queue
import numpy as np

from AWS_profile import AWS_profile, calculate_services
from settings import Config


file_handler = logging.FileHandler("logs.txt")
file_handler.setLevel(logging.INFO)
# Set a formatter for the file handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)



def worker(task_queue, aws_profile, progress, task_progress_ids, bf_endpoints):
    """Worker thread function to process tasks from the queue."""
    while True:
        try:
            services = task_queue.get(timeout=60)  # Wait for a task
        except queue.Empty:
            break  # Exit if the queue is empty
        try:
            aws_profile.launch_discovery(services, progress, task_progress_ids, bf_endpoints)
        except Exception as e:
            for service in services:
                progress.remove_task(task_progress_ids[service])
            logger.error(f"Task ["+",".join(services)+f"] failed with exception: {e}")
        finally:
            task_queue.task_done()  # Mark the task as done

def load_config(credentials_file_path: Path = Path.home() / ".aws" / "credentials",
                config_file_path: Path = Path.home() / ".aws" / "config") -> dict:
    """
        Load credentials and configurations from disk files.
        Fallback to system variables if not found in config file

        :param file_path: Path to the configuration file.
        :return: A dictionary with configuration values.
    """
    settings = dict()
    credentials = ConfigParser()
    config = ConfigParser()

    # logger.info(credentials_file_path)

    # Check if the file exists
    if credentials_file_path.exists():
        credentials.read(credentials_file_path)
    else:
        logger.warning("AWS credentials file does not exist. Using environment variables.")

    # Check if the file exists
    if config_file_path.exists():
        config.read(config_file_path)
    else:
        logger.warning("AWS config file does not exist. Using environment variables.")

    cred_section = "" if len(credentials.sections()) == 0 else credentials.sections()[0]
    if len(config.sections()) > 1:
        cred_section = Prompt.ask(prompt="Choose credentials to use : ", choices=credentials.sections(), show_choices=True)

    config_section = "" if len(config.sections()) == 0 else config.sections()[0]
    if len(config.sections()) > 1:
        config_section = Prompt.ask(prompt="Choose config to use : ", choices=config.sections(), show_choices=True)

    # Get values from config file or environment variables
    settings = {
        "AWS_ACCESS_KEY_ID": credentials.get(cred_section, "aws_access_key_id", fallback=os.getenv("AWS_ACCESS_KEY_ID", "")),
        "AWS_SECRET_ACCESS_KEY": credentials.get(cred_section, "aws_secret_access_key", fallback=os.getenv("AWS_SECRET_ACCESS_KEY", "")),
        "AWS_SESSION_TOKEN": credentials.get(cred_section, "aws_session_token", fallback=os.getenv("AWS_SESSION_TOKEN", "")),
        "AWS_REGION_NAME": config.get(config_section, "region", fallback=os.getenv("AWS_REGION_NAME", "us-east-2")),
        "AWS_OUTPUT": "json",
    }

    # logger.info(settings)

    if not settings["AWS_ACCESS_KEY_ID"] and not settings["AWS_SECRET_ACCESS_KEY"]:
        logger.critical("AWS access key ID not found.")
    if not settings["AWS_SECRET_ACCESS_KEY"] and not settings["AWS_SECRET_ACCESS_KEY"]:
        logger.critical("AWS secret access key not found.")

    return settings


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Bruteforce AWS rights with boto3')
    parser.add_argument('-t', '--threads', type=int, default=75, help='Number of threads to use')
    parser.add_argument('-r', '--remove-services', default="cloudhsm,cloudhsmv2,sms,sms-voice.pinpoint", help='List of services to remove separated by comma')
    parser.add_argument('-u', '--update-services', action="store_true", default=False, help='Update dynamically list of AWS services and associated functions')
    args = parser.parse_args()

    settings = load_config()

    if args.update_services or not Config.SERVICES_FILE_MAPPING.exists() or os.path.getsize(Config.SERVICES_FILE_MAPPING) == 0:
        logger.info("Updating dynamically list of AWS services and associated functions")
        update = AWS_profile(settings)
        update.update_dynamically_services_functions(output_file=Config.SERVICES_FILE_MAPPING)

    with Config.SERVICES_FILE_MAPPING.open("r") as f:
        bf_endpoints = json.load(f)

    services_to_bf = calculate_services(removed_services=args.remove_services, bf_endpoints=bf_endpoints)
    services_chunks = np.array_split(services_to_bf, args.threads)
    services_chunks = [list(chunk) for chunk in services_chunks]

    test_obj = AWS_profile(settings)

    task_queue = queue.Queue()
    for services in services_chunks:
        task_queue.put(services)

    with Progress(
            SpinnerColumn(),
            "[bold blue]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("[cyan]{task.completed}/{task.total}"),
            transient=True,
            refresh_per_second=2
    ) as progress:
        # Add tasks to the progress bar
        task_progress_ids = {
            service: progress.add_task(f"[green]Processing {service}...", total=len(endpoints))
            for service, endpoints in bf_endpoints.items() if service in services_to_bf
        }

        # Start worker threads
        threads = []
        for _ in range(args.threads):  # Adjust the number of threads as needed
            thread = threading.Thread(target=worker, args=(task_queue, test_obj, progress, task_progress_ids, bf_endpoints))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join(timeout=30)



