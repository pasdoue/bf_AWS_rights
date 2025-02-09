import sys
import argparse
import os
from pathlib import Path
import time

import logging
from typing import List

from R2Log import logger
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console

from rich.prompt import Prompt, Confirm
from configparser import ConfigParser

import threading
import queue
import numpy as np

from AWS_profile import AWS_profile
from libs.Services import Services, Service
from settings import Config

NUMBER_OF_THREADS = 0

file_handler = logging.FileHandler("logs.txt")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

console = Console()

def print_banner() -> None:
    banner = """
          ____  ______        __          _______       _____  _____ _____ _    _ _______ _____ 
         |  _ \\|  ____|      /\\ \\        / / ____|     |  __ \\|_   _/ ____| |  | |__   __/ ____|
         | |_) | |__ ______ /  \\ \\  /\\  / / (___ ______| |__) | | || |  __| |__| |  | | | (___  
         |  _ <|  __|______/ /\\ \\ \\/  \\/ / \\___ \\______|  _  /  | || | |_ |  __  |  | |  \\___ \\ 
         | |_) | |        / ____ \\  /\\  /  ____) |     | | \\ \\ _| || |__| | |  | |  | |  ____) |
         |____/|_|       /_/    \\_\\/  \\/  |_____/      |_|  \\_\\_____\\_____|_|  |_|  |_| |_____/ 
         Made by pasdoue
    """
    logger.info(banner)
    logger.info("Be patient, script can take up to 6min to BF.\nWhen finished you can Ctrl+C or wait threads to exit.")

def worker(task_queue, aws_profile: AWS_profile, progress, task_progress_ids):
    """Worker thread function to process tasks from the queue."""
    while True:
        try:
            service_list: List[Service] = task_queue.get(timeout=60)  # Wait for a task
        except queue.Empty:
            break  # Exit if the queue is empty
        try:
            aws_profile.launch_discovery(service_list, progress, task_progress_ids)
        except Exception as e:
            for service in service_list:
                progress.remove_task(task_progress_ids[service.name])
            # logger.error(f"Task ["+",".join(services)+f"] failed with exception: {e}")
            logger.error(f"Error occurred : {e}")
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

def verify_unsafe(unsafe: bool, aws_profile: AWS_profile):
    if unsafe:
        resp = Confirm.ask("Are you sure you want to run this script in unsafe mode ?", show_choices=True)
        if resp == "n":
            sys.exit(0)
        else:
            logger.warning("Running in unsafe mode.")
            aws_profile.set_unsafe_mode()

def print_elapsed_time(start: time.time) -> None:
    end = time.time()
    logger.info(f"Script took : {str(end - start)} seconds")


if __name__ == "__main__":

    print_banner()

    start = time.time()

    services = Services(filemap=Config.SERVICES_FILE_MAPPING)
    services_choices = services.get_services_names()

    parser = argparse.ArgumentParser(description='Bruteforce AWS rights with boto3')
    parser.add_argument('-t', '--threads', type=int, default=75, help='Number of threads to use')
    parser.add_argument('--thread-timeout', type=int, default=30, help='Timeout consumed before killing thread')
    parser.add_argument('-u', '--update-services', action="store_true", default=False,
                        help='Update dynamically list of AWS services and associated functions')
    parser.add_argument('-b', '--black-list', nargs='*',
                        default="cloudhsm,cloudhsmv2,sms,sms-voice.pinpoint",
                        choices=services_choices,
                        help='List of services to remove separated by comma. Launch script with -p to see services',
                        metavar='PARAMETER')
    parser.add_argument('-w', '--white-list', nargs='*',
                        default=[],
                        choices=services_choices,
                        help='List of services to whitelist/scan separated by comma. Launch script with -p to see services',
                        metavar='PARAMETER')
    parser.add_argument('-p', '--print-services', action="store_true", default=False, help='List of services to whitelist/scan separated by comma')
    parser.add_argument('--unsafe-mode', action="store_true", default=False, help='Perform potentially destructive functions. Disabled by default.')
    args = parser.parse_args()

    settings = load_config()

    aws_profile = AWS_profile(services=services, creds=settings)

    if args.update_services or not services.filemap.exists() or os.path.getsize(services.filemap) == 0:
        aws_profile.update_dynamically_services_functions()
        print_elapsed_time(start=start)
        logger.info("Run this script a second time to perform actions.")
        sys.exit(0)

    if args.print_services:
        logger.info('\t'.join([service.name for service in services.get_services()]))
        print_elapsed_time(start=start)
        sys.exit(0)

    verify_unsafe(unsafe=args.unsafe_mode, aws_profile=aws_profile)

    services.calculate_white_and_black_list(white_list=args.white_list, black_list=args.black_list)
    services.calculate_safe_mode()

    NUMBER_OF_THREADS = services.nb_activated_services if services.nb_activated_services < args.threads else args.threads

    services_chunks = np.array_split(services.get_services(), NUMBER_OF_THREADS)
    services_chunks = [list(chunk) for chunk in services_chunks]

    task_queue = queue.Queue()
    for chunk in services_chunks:
        task_queue.put(chunk)

    with Progress(
            SpinnerColumn(),
            "[bold blue]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("[cyan]{task.completed}/{task.total}"),
            transient=True,
            refresh_per_second=2,
            console=console
    ) as progress:
        # Add tasks to the progress bar
        task_progress_ids = {
            service.name: progress.add_task(f"[green]Processing {service.name}...", total=len(service.get_functions()))
            for service in services.get_services()
        }

        # Start worker threads
        threads = []
        for _ in range(NUMBER_OF_THREADS):  # Adjust the number of threads as needed
            thread = threading.Thread(target=worker, args=(task_queue, aws_profile, progress, task_progress_ids))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join(timeout=args.thread_timeout)

    print_elapsed_time(start=start)
    logger.info("You can check availabled functions inside log file")



