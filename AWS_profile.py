import inspect
import json
from configparser import ConfigParser
from pathlib import Path
from typing import List, Dict, Union

from R2Log import logger

import boto3, botocore
from inspect import signature

from rich.emoji import Emoji
from rich.prompt import Prompt

from libs.Services import Services, Service, Function
from settings import Config


def write_rights_to_file(service: Service, arn: str, res: dict):
    """
        Write to output file the result of batch
        :param service:
        :param arn:
        :param res:
        :return:
    """
    output_folder = Path(__file__).parent / arn
    output_file = output_folder / f"{service.name}.json"

    if not output_folder.exists():
        output_folder.mkdir()

    output_file.write_text(json.dumps(res, indent=4, sort_keys=True, default=str))


def check_rights(arn: str, service: Service, session_obj: boto3.session.Session, progress, progress_id) -> dict:
        res = dict()
        res[service.name] = {}

        for function in service.get_functions():
            if any(function.name.startswith(safe_mode) for safe_mode in Config.SAFE_MODE):
                service_function = getattr(session_obj, function.name)
                if service_function is None:
                    res[service.name][function.name] = "unavailable"
                else:
                    try:
                        ret = service_function()
                    except Exception as e:
                        if "AccessDenied" in str(e) or "ForbiddenException" in str(e):
                            res[service.name][function.name] = "Access Denied"
                        elif "Missing required parameter" in str(e):
                            res[service.name][function.name] = "Missing required parameter"
                        else:
                            res[service.name][function.name] = f"Unknwon Exception : {str(e)}"
                        progress.update(progress_id, advance=1)
                        continue
                    if ret is not None:
                        logger.success(f"{service.name}:{function.name} is available")
                        res[service.name][function.name] = ret
                    else:
                        res[service.name][function.name] = "empty"
                progress.update(progress_id, advance=1)
        write_rights_to_file(service=service, arn=arn, res=res)
        progress.remove_task(progress_id)
        return res

class User_config:
    """
        This class will parse config file of user and return a dict with all params to use in boto3.session.Session.
        Because boto3.session.Session params differs from config files (thanks AWS... grrr) we need to reformat them
    """
    default_credentials_file_path: Path = Path.home() / ".aws" / "credentials"
    default_config_file_path: Path = Path.home() / ".aws" / "config"

    @classmethod
    def _load_credentials_file(cls, credentials_file_path: Path = default_credentials_file_path) -> Union[dict, None]:
        res = {}
        credentials = ConfigParser()

        if credentials_file_path.exists():
            credentials.read(credentials_file_path)
            if len(credentials.sections()) > 1:
                cred_section = Prompt.ask(prompt="Choose credentials to use : ", choices=credentials.sections(),
                                          show_choices=True)
            elif len(credentials.sections()) == 1:
                cred_section = credentials.sections()[0]
            else:
                logger.critical(f"{Emoji('hamster')} AWS credentials file detected but no section found.")

            if cred_section:
                tmp = dict(credentials.items(cred_section))
                res["profile_name"] = cred_section

                # Because AWS Boto library Session only accept those params and no other ones... We need to remove all other params... GG AWS
                for k, v in tmp.items():
                    # verify this param exists in boto3.session.Session
                    if k in inspect.signature(boto3.session.Session).parameters.keys():
                        res[k] = v
            return res
        else:
            logger.critical(f"{Emoji('no_entry_sign')} AWS credentials file does not exists. Configure it to launch script")

    @classmethod
    def _load_config(cls, config_file_path: Path = default_config_file_path) -> Union[dict, None]:
        config = ConfigParser()

        if config_file_path.exists():
            config.read(config_file_path)
            if len(config.sections()) > 1:
                config_section = Prompt.ask(prompt="Choose config to use : ", choices=config.sections(),
                                            show_choices=True)
            elif len(config.sections()) == 1:
                config_section = config.sections()[0]
            else:
                logger.critical(f"{Emoji('hamster')} AWS config file detected but no section found.")

            # Because AWS Boto library Session only accept those params and no other ones... We need to remove all other params... GG AWS
            return {"region_name": config.get(config_section, "region")}
        else:
            logger.critical(f"{Emoji('no_entry_sign')} AWS config file does not exist. Using environment variables. Configure it to launch script")

    @staticmethod
    def load(credentials_file_path: Union[Path|str] = default_credentials_file_path,
             config_file_path: Union[Path|str] = default_config_file_path) -> dict:

        credentials_file_path = Path(credentials_file_path) if isinstance(credentials_file_path, str) else credentials_file_path
        config_file_path = Path(config_file_path) if isinstance(config_file_path, str) else config_file_path

        settings = User_config._load_credentials_file(credentials_file_path=credentials_file_path)
        settings.update(User_config._load_config(config_file_path=config_file_path))

        if not settings["aws_access_key_id"]:
            logger.critical("AWS access key ID not found.")
        if not settings["aws_secret_access_key"]:
            logger.critical("AWS secret access key not found.")

        return settings

class AWS_profile:

    def __init__(self, services: Services, creds: Dict) -> None:
        """
            Init object according to input settings (
            :param kwargs: creds used
        """
        self.boto_session = boto3.session.Session(**creds)
        self.__services = services
        self.__safe_mode = True
        self.arn = self.boto_session.client('sts').get_caller_identity().get('Arn')
        self.arn_linux_safe = self.arn.split(':')[-1].replace('/','_') # Get end of Arn which is human-readable and remove '/' inside


    def set_unsafe_mode(self):
        self.__safe_mode = False
        self.__services.set_unsafe_mode()

    def launch_discovery(self, services: List[Service], progress, task_progress_ids):
        """

        """
        all_res = list()
        for service in services:
            try:
                client = self.boto_session.client(service.name)
            except botocore.exceptions.UnknownServiceError:
                progress.remove_task(task_progress_ids[service.name])
                continue
            if client is not None:
                service_rights = check_rights(arn=self.arn_linux_safe, service=service, session_obj=client, progress=progress, progress_id=task_progress_ids[service.name])
                all_res.append(service_rights)
        return all_res

    def update_dynamically_services_functions(self):
        """
            Retrieve boto3 available services and then retrieve all associated functions
        """
        logger.info("Updating dynamically list of AWS services and associated functions")

        available_services = self.boto_session.get_available_services()
        for service in available_services:
            curr_service = Service(name=service)
            try:
                boto_service: boto3.session.Session = self.boto_session.client(service_name=curr_service.name)
            except Exception as e:
                logger.error(f"Impossible to connect to AWS service : {service}\n{str(e)}")
                continue
            for function in dir(boto_service):
                if not function.startswith("_") and not "delete" in function.lower():
                    func = getattr(boto_service, function)
                    try:
                        sig = signature(func)
                        if len(sig.parameters) <= 2:
                            curr_service.add_function(function=Function(name=function))
                    except TypeError as e:
                        pass
            self.__services.update_service(name=curr_service.name, service_info=curr_service)

        self.save_to_filemap()
        logger.success("Update finished !")
        return

    def save_to_filemap(self):
        if self.__services is None:
            raise ValueError("Services are not provided")
        res = dict()
        for service in self.__services.services:
            res[service.name] = [function.name for function in service.functions]
        with open(self.__services.filemap, 'w') as f:
            f.write(json.dumps(res, indent=4, sort_keys=True, default=str))
