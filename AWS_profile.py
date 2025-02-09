import json
from pathlib import Path
from typing import List, Union, Dict

from R2Log import logger

import boto3, botocore
from inspect import signature

from libs.Services import Services, Service, Function
from settings import Config


def write_rights_to_file(service: Service, res: dict):
    """
        Write to output file the result of batch
        :param service:
        :param res:
        :return:
    """
    arn = boto3.client('sts').get_caller_identity().get('Arn')  # retrieve user Arn
    arn = arn.split(':')[-1].replace('/', '_')  # Get end of Arn which is human-readable and remove '/' inside
    output_folder = Path(__file__).parent / arn
    output_file = output_folder / f"{service.name}.json"

    if not output_folder.exists():
        output_folder.mkdir()

    output_file.write_text(json.dumps(res, indent=4, sort_keys=True, default=str))


def check_rights(service: Service, session_obj: boto3.session.Session, progress, progress_id) -> dict:
        res = dict()
        res[service.name] = {}

        for function in service.get_functions():
            if any(function.name.startswith(safe_mode) for safe_mode in Config.SAFE_MODE):
                service_function = getattr(session_obj, function.name)
                if service_function is None:
                    # logger.warning(f"Function {function} is not available")
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
                        # logger.warning(f"Function {function} empty")
                        res[service.name][function.name] = "empty"
                progress.update(progress_id, advance=1)
        write_rights_to_file(service=service, res=res)
        progress.remove_task(progress_id)
        return res



class AWS_profile:

    def __init__(self, services: Services, creds: Dict) -> None:
        """
            Init object according to input settings (
            :param kwargs: creds used
        """
        self.boto_session = boto3.session.Session()
        self.__services = services
        self.__safe_mode = True
        self.arn = boto3.client('sts').get_caller_identity().get('Arn')
        self.arn_linux_safe = self.arn.split(':')[-1].replace('/','_') # Get end of Arn which is human-readable and remove '/' inside
        for k, v in creds.items():
            setattr(self, k, v)

    def set_unsafe_mode(self):
        self.__safe_mode = False
        self.__services.set_unsafe_mode()

    def launch_discovery(self, services: List[Service], progress, task_progress_ids):
        """

        """
        all_res = list()
        for service in services:
            try:
                client = self.connect(service=service.name)
            except botocore.exceptions.UnknownServiceError:
                progress.remove_task(task_progress_ids[service.name])
                continue
            if client is not None:
                service_rights = check_rights(service=service, session_obj=client, progress=progress, progress_id=task_progress_ids[service.name])
                all_res.append(service_rights)
        return all_res

    def connect(self, service: str) -> Union[boto3.session.Session | None]:
        """
            Connect to boto service and return client instance
            :param service: name of the service
        """
        # logger.info(f"Connecting to AWS service : {service}")
        try:
            return self.boto_session.client(service,
                                            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                                            aws_session_token=self.AWS_SESSION_TOKEN,
                                            region_name=self.AWS_REGION_NAME,
                                            )
        except Exception as e:
            if "AccessDenied" in str(e):
                logger.error(f"Impossible to connect to AWS service : {service}\n{str(e)}")
            else:
                raise e


    def update_dynamically_services_functions(self):
        """
            Retrieve boto3 available services and then retrieve all associated functions
        """
        logger.info("Updating dynamically list of AWS services and associated functions")

        available_services = self.boto_session.get_available_services()
        # logger.info(available_services)
        for service in available_services:
            curr_service = Service(name=service)
            try:
                boto_service: boto3.session.Session = self.connect(service=service)
            except Exception as e:
                continue
            # logger.info(service)
            for function in dir(boto_service):
                if not function.startswith("_") and not "delete" in function.lower():
                    func = getattr(boto_service, function)
                    try:
                        sig = signature(func)
                        # logger.info(f"{service} -> {function} len({len(sig.parameters)})")
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
