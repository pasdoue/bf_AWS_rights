import json
from pathlib import Path
from typing import List, Union

from R2Log import logger

import boto3, botocore
from inspect import signature


class AWS_profile:

    def __init__(self, kwargs):
        """
            Init object according to input settings (
            :param kwargs:
        """
        self.boto_session = boto3.session.Session()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update_dynamically_services_functions(self, output_file: Path):
        """

            :return:
        """
        available_services = self.boto_session.get_available_services()
        # logger.info(available_services)
        res = dict()
        for service in available_services:
            try:
                conn: boto3.session.Session = self.connect(service=service)
            except Exception as e:
                continue
            # logger.info(service)
            for function in dir(conn):
                if not function.startswith("_") and not "delete" in function.lower():
                    func = getattr(conn, function)
                    try:
                        sig = signature(func)
                        # logger.info(f"{service} -> {function} len({len(sig.parameters)})")
                        if len(sig.parameters) <= 2:
                            if not res.get(service):
                                res[service] = [function]
                            else:
                                res[service].append(function)
                    except TypeError as e:
                        pass

        output_file.write_text(json.dumps(res, indent=4, sort_keys=True, default=str))

    def launch_discovery(self, services: List[str], progress, task_progress_ids, bf_endpoints):
        all_res = list()
        for service in services:
            try:
                client = self.connect(service=service)
            except botocore.exceptions.UnknownServiceError:
                progress.remove_task(task_progress_ids[service])
                continue
            if client is not None:
                all_res.append(AWS_profile.check_rights(service=service, session_obj=client, progress=progress, progress_id=task_progress_ids[service], bf_endpoints=bf_endpoints))
        return all_res

    def connect(self, service: str) -> Union[boto3.session.Session | None]:
        """
            Connect to boto service and return bot instance
            :param service: name of the service
            :return:
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

    @staticmethod
    def check_rights(service: str, session_obj: boto3.session.Session, progress, progress_id, bf_endpoints) -> dict:
        res = dict()
        res[service] = {}
        functions = bf_endpoints.get(service)

        if functions:
            for function in functions:
                service_function = getattr(session_obj, function)
                if service_function is None:
                    # logger.warning(f"Function {function} is not available")
                    res[service][function] = "unavailable"
                else:
                    try:
                        ret = service_function()
                    except Exception as e:
                        if "AccessDenied" in str(e) or "ForbiddenException" in str(e):
                            res[service][function] = "Access Denied"
                        elif "Missing required parameter" in str(e):
                            res[service][function] = "Missing required parameter"
                        else:
                            res[service][function] = f"Unknwon Exception : {str(e)}"
                        progress.update(progress_id, advance=1)
                        continue
                    if ret is not None:
                        logger.success(f"{service}:{function} is available")
                        res[service][function] = ret
                    else:
                        # logger.warning(f"Function {function} empty")
                        res[service][function] = "empty"
                progress.update(progress_id, advance=1)
        AWS_profile._write_right_to_file(service=service, res=res)
        progress.remove_task(progress_id)
        return res

    @staticmethod
    def _write_right_to_file(service: str, res: dict):
        """
            Write to output file the result of batch
            :param service:
            :param res:
            :return:
        """
        output_folder = Path(__file__).parent / "out"
        output_file = output_folder / f"{service}.json"

        if not output_folder.exists():
            output_folder.mkdir()

        output_file.write_text(json.dumps(res, indent=4, sort_keys=True, default=str))

def calculate_services(removed_services: List[str], bf_endpoints: dict) -> List[str]:
    """
        Return list of AWS services to bruteforce excluding removed ones
        :param removed_services:
        :return:
    """
    if isinstance(removed_services, str):
        removed_services = removed_services.split(",")

    return [i for i in list(bf_endpoints.keys()) if i not in removed_services]
