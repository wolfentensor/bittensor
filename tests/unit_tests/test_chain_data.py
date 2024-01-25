import pytest
from bittensor.chain_data import AxonInfo


# Sample data for tests
axon_info_example = AxonInfo(version=1, ip="127.0.0.1", port=8080, ip_type=4, hotkey="hotkey123", coldkey="coldkey123")


@pytest.fixture
def axon_info_fixture():
    """Provides a standard AxonInfo instance for tests."""
    return AxonInfo(version=1, ip="127.0.0.1", port=8080, ip_type=4, hotkey="hotkey123", coldkey="coldkey123")


def test_is_serving(axon_info_fixture):
    assert axon_info_fixture.is_serving == True, "Should be serving when IP is not 0.0.0.0"


def test_ip_str(axon_info_fixture):
    # This test assumes the existence of a functioning net.ip__str__() method
    expected_str = "127.0.0.1:8080"  # Adjust expected output based on net.ip__str__() implementation
    assert axon_info_fixture.ip_str() == expected_str, "IP string representation should match expected format"
