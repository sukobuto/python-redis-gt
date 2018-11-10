from fakeredis import FakeStrictRedis
from redis import StrictRedis
from recter.throttle import Throttle


class TestThrottle:

    def setup_method(self):
        self.r: StrictRedis = FakeStrictRedis()

    def test_run(self):
        throttle = Throttle(self.r)
        throttle.set_string()
        assert throttle.get_string() == 't-value'
