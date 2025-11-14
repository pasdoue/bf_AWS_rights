import json
import os
from pathlib import Path
from typing import List

from settings import Config


class Param:

    def __init__(self, name: str):
        self.name = name

class Function:

    def __init__(self, name: str, arguments: List[Param] = None, activated: bool = True):
        self.name = name
        self.arguments = list() if arguments is None else arguments
        self.activated = activated

    def add_raw_args(self, args_names: List[str]):
        for arg_name in args_names:
            self.arguments.append(Param(arg_name))

class Service:

    def __init__(self, name: str, functions: List[Function] = None, activated: bool = True) -> None:
        self.name = name
        self.functions = list() if functions is None else functions
        self.activated = activated
        self.nb_functions = 0
        self.nb_activated_functions = 0

    def add_function(self, function: Function):
        self.functions.append(function)

    def calc_functions_length(self) -> None:
        self.nb_functions += len(self.functions)
        for f in self.functions:
            if f.activated:
                self.nb_activated_functions += 1

    def get_functions(self) -> List[Function]:
        """
            Return only functions that are activated
        """
        return [function for function in self.functions if function.activated]


class Services:

    def __init__(self, filemap: Path, safe_mode: bool = True) -> None:
        self.filemap = filemap
        self.safe_mode = safe_mode # by default is True to avoid wrong behaviors
        self.__whitelist: List[str] = []
        self.__blacklist: List[str] = []
        self.nb_services = 0
        self.nb_activated_services = 0
        if not self.filemap.exists() or os.path.getsize(self.filemap) == 0:
            self.services: List[Service] = list()
        else:
            self.services: List[Service] = self.__load_from_filemap()

    def set_unsafe_mode(self):
        self.safe_mode = False

    def __load_from_filemap(self) -> List[Service]:
        res = list()
        with open(self.filemap) as f:
            content = json.loads(f.read())

        for k,v in content.items():
            curr_service = Service(name=k)
            for func in v:
                function = Function(name=func)
                curr_service.add_function(function)
            res.append(curr_service)
        return res

    def get_services(self) -> List[Service]:
        """
            Return only list of services that are activated
        """
        return [service for service in self.services if service.activated]

    def get_services_names(self) -> List[str]:
        """
            Return only list of services names
        """
        return [service.name for service in self.get_services()] if len(self.get_services()) > 0 else None

    def update_service(self, name: str, service_info: Service) -> None:
        for service in self.services:
            if service.name == name:
                service = service_info
                return
        # if service does not already exists, we push it
        self.services.append(service_info)

    def calculate_white_and_black_list(self, white_list: List[str], black_list: List[str]):
        """
            Return list of AWS services to bruteforce first including white list if exists and then always exclude black list.
            :param white_list: list of services to scan
            :param black_list: list of services to avoid
        """
        self.__blacklist = black_list
        self.__whitelist = white_list
        self.nb_services = len(self.services)

        if isinstance(self.__blacklist, str):
            self.__blacklist = self.__blacklist.strip().split(",")
        if isinstance(self.__whitelist, str):
            self.__whitelist = self.__whitelist.strip().split(",")

        for service in self.services:
            if self.__whitelist:
                service.activated = True if service.name in self.__whitelist else False
            if self.__blacklist:
                service.activated = False if service.name in self.__blacklist else service.activated

            if service.activated:
                self.nb_activated_services += 1

    def calculate_safe_mode(self):
        """
            Deactivate some functions if we are in safe mode.
        """
        if not self.safe_mode:
            return
        for service in self.services:
            if service.activated:
                for function in service.functions:
                    if any(function.name.startswith(safe_mode) for safe_mode in Config.SAFE_MODE):
                       function.activated = True
                    else:
                        function.activated = False
