import unittest

from meta_aws.meta_aws import MetaAWS

class TestConfig(unittest.TestCase):

    def test_is_role_arn(self):
        res = []
        arns = [
            "arn:aws:iam::123456789012:user/alice",
            "arn:aws:iam::123456789012:role/AdminRole",
            "arn:aws:sts::123456789012:assumed-role/AdminRole/my-session",
            "arn:aws:sts::123456789012:federated-user/Bob"
        ]
        for arn in arns:
            res.append(MetaAWS._is_role_arn(arn=arn))
        self.assertEqual(res, [False, True, True, False])

    def test_set_role_from_arn(self):
        arns = [
            "arn:aws:iam::123456789012:user/alice",
            "arn:aws:iam::123456789012:role/toto",
            "arn:aws:sts::123456789012:assumed-role/AR/my-session",
            "arn:aws:sts::123456789012:federated-user/ROLE"
        ]
        self.assertEqual(MetaAWS.set_role_from_arn(arn=arns[0]), "")
        self.assertEqual(MetaAWS.set_role_from_arn(arn=arns[1]), "toto")
        self.assertEqual(MetaAWS.set_role_from_arn(arn=arns[2]), "AR")
        self.assertEqual(MetaAWS.set_role_from_arn(arn=arns[3]), "")




