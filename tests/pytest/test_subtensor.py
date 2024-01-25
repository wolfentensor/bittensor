import pytest
from bittensor import subtensor


class bittensor:
    __finney_entrypoint__ = "ws://finney.entrypoint"
    __local_entrypoint__ = "ws://localhost:9944"
    __finney_test_entrypoint__ = "ws://test.finney.entrypoint"
    __archive_entrypoint__ = "ws://archive.entrypoint"
    defaults = type('obj', (object,), {
        "subtensor": type('obj', (object,), {"network": "finney"})
    })


@pytest.mark.parametrize("input_network, expected_output", [
    ("finney", ("finney", bittensor.__finney_entrypoint__)),
    ("local", ("local", bittensor.__local_entrypoint__)),
    ("test", ("test", bittensor.__finney_test_entrypoint__)),
    ("archive", ("archive", bittensor.__archive_entrypoint__)),
    (bittensor.__finney_entrypoint__, ("finney", bittensor.__finney_entrypoint__)),
    ("entrypoint-finney.opentensor.ai", ("finney", bittensor.__finney_entrypoint__)),
    ("127.0.0.1", ("local", "127.0.0.1")),
    ("localhost", ("local", "localhost")),
    ("unknown.network", ("unknown", "unknown.network")),
    (None, ("unknown", None)),
])
def test_determine_chain_endpoint_and_network(input_network, expected_output):
    assert subtensor.determine_chain_endpoint_and_network(input_network) == expected_output


def test_setup_config_with_direct_network():
    config_mock = {"subtensor": {}}
    network = "finney"
    expected_endpoint_url = "ws://finney.entrypoint"
    expected_network = "finney"
    endpoint_url, evaluated_network = subtensor.setup_config(network, config_mock)
    assert endpoint_url == expected_endpoint_url and evaluated_network == expected_network


def test_setup_config_with_config_network():
    config_mock = {
        "get": lambda x, y: {},
        "subtensor": {
            "get": lambda x: "ws://finney.entrypoint" if x == "chain_endpoint" else "finney",
            "__is_set": {"subtensor.chain_endpoint": True}
        }
    }
    network = None  # Emulating no direct network provided
    expected_endpoint_url = "ws://finney.entrypoint"
    expected_network = "finney"
    endpoint_url, evaluated_network = subtensor.setup_config(network, config_mock)
    assert endpoint_url == expected_endpoint_url and evaluated_network == expected_network

