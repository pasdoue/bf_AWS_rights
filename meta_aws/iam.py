from R2Log import logger

from meta_aws.meta_aws import MetaAWS


class MetaIAM(MetaAWS):

    def list_attached_role_policies(self):
        if not self.role_name:
            return ""
        else:
            logger.info(f"Listing attached policies for {self.arn}. Role name: {self.role_name}")
            return self.boto_func(RoleName=self.role_name)