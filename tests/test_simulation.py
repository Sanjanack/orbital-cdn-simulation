import simpy
from enhanced_satellite_cdn import Satellite, SimulationConfig, create_content_catalog


def test_satellite_caching_and_stats():
    env = simpy.Environment()
    config = SimulationConfig(simulation_duration=10.0, request_interval=1.0, cache_size=3, content_catalog_size=5, user_count=1, log_interval=2.0)
    catalog = create_content_catalog(config)
    satellite = Satellite(env, config)

    # Simulate a few requests for two items
    content_a = catalog[0]
    content_b = catalog[1]

    # First miss, then hit
    satellite.request_content(content_a.content_id, content_a, 'User_1')
    satellite.request_content(content_a.content_id, content_a, 'User_1')

    # Another content causes cache to grow
    satellite.request_content(content_b.content_id, content_b, 'User_1')

    # Log performance
    satellite.log_performance()

    stats = satellite.get_final_statistics()
    assert stats['total_requests'] >= 3
    assert stats['cache_hits'] >= 1
    assert stats['cache_misses'] >= 1


