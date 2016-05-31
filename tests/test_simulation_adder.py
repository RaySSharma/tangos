import halo_db as db
import halo_db.config
from halo_db import log
import os
from halo_db.tools import add_simulation
from halo_db.simulation_output_handlers import output_testing
from halo_db import testing

def setup():
    testing.init_blank_db_for_testing(verbose=True)
    db.config.base = os.path.join(os.path.dirname(__name__), "test_simulations")
    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_1"))
    with log.LogCapturer():
        manager.scan_simulation_and_add_all_descendants()

def test_simulation_exists():
    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_2"))
    assert not manager.simulation_exists()

    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_1"))
    assert manager.simulation_exists()

def test_step_halo_count():
    assert db.get_timestep("dummy_sim_1/step.1").halos.count()==10
    assert db.get_timestep("dummy_sim_1/step.2").halos.count()==5

def test_step_info():
    assert db.get_timestep("dummy_sim_1/step.1").time_gyr==1
    assert db.get_timestep("dummy_sim_1/step.1").redshift==0.5

def test_simulation_properties():
    assert db.get_simulation("dummy_sim_1").properties.count()==3
    assert db.get_simulation("dummy_sim_1")['dummy_sim_property']=='42'

def test_readd_simulation():
    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_1"))
    with log.LogCapturer():
        manager.scan_simulation_and_add_all_descendants()

    assert db.core.get_default_session().query(db.core.Simulation).count()==1
    assert len(db.get_simulation("dummy_sim_1").timesteps)==2
    assert db.get_simulation("dummy_sim_1").properties.count()==3

def test_appropriate_loader():
    assert str(db.get_timestep("dummy_sim_1/step.1").load())=="Test string - this would contain the data for step.1"

def _perform_simulation_update():
    db.config.base = os.path.join(os.path.dirname(__name__), "test_simulations_mock_update")
    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_1"))
    with log.LogCapturer():
        manager.scan_simulation_and_add_all_descendants()

def test_update_simulation():
    with testing.autorevert():
        assert db.get_simulation("dummy_sim_1")['dummy_sim_property_2'] == 'banana'
        _perform_simulation_update()
        assert db.get_simulation("dummy_sim_1").properties.count() == 4
        assert db.get_simulation("dummy_sim_1")['dummy_sim_property_2']=='orange'
        assert db.get_simulation("dummy_sim_1")['dummy_sim_property_new'] == 'fruits'
        assert len(db.get_simulation("dummy_sim_1").timesteps) == 3
        assert db.get_timestep("dummy_sim_1/step.3").halos.count()==7
