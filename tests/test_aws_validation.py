from validator.aws_validation import validate_aws_state
from validator.config import ValidationConfig
from validator.result import Status


class EC2Client:
    def describe_instances(self, **kwargs):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Project", "Value": "cloud-deployment-validator"}],
                            "SecurityGroups": [{"GroupId": "sg-example"}],
                        }
                    ]
                }
            ]
        }


def test_optional_aws_state_validation_with_mock() -> None:
    config = ValidationConfig(
        host="192.0.2.1",
        instance_id="i-example",
        expected_project_tag="cloud-deployment-validator",
    )
    results = validate_aws_state(config, EC2Client())
    assert all(result.status == Status.PASS for result in results)
