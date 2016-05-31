import halo_db as db
import halo_db.config
import os
from halo_db.tools import add_simulation
from halo_db.tools import property_writer
from halo_db.simulation_output_handlers import output_testing
from halo_db import parallel_tasks, log, testing
import properties

def setup():
    parallel_tasks.use('null')

class DummyProperty(properties.HaloProperties):
    @classmethod
    def name(self):
        return "dummy_property",

    def requires_property(self):
        return []

    def calculate(self, data, entry):
        return data.time*data.halo,

class DummyPropertyCausingException(properties.HaloProperties):
    @classmethod
    def name(self):
        return "dummy_property_with_exception",

    def calculate(self, data, entry):
        raise RuntimeError, "Test of exception handling"

def init_blank_simulation():
    testing.init_blank_db_for_testing()
    db.config.base = os.path.join(os.path.dirname(__name__), "test_simulations")
    manager = add_simulation.SimulationAdderUpdater(output_testing.TestOutputSetHandler("dummy_sim_1"))
    with log.LogCapturer():
        manager.scan_simulation_and_add_all_descendants()

def run_writer_with_args(*args):
    stored_log = log.LogCapturer()
    writer = property_writer.PropertyWriter()
    writer.parse_command_line(args)
    with stored_log:
        writer.run_calculation_loop()
    return stored_log.get_output()

def test_basic_writing():
    init_blank_simulation()
    run_writer_with_args("dummy_property")

    assert db.get_halo("dummy_sim_1/step.1/1")['dummy_property'] == 1.0
    assert db.get_halo("dummy_sim_1/step.1/2")['dummy_property'] == 2.0
    assert db.get_halo("dummy_sim_1/step.2/1")['dummy_property'] == 2.0

def test_error_ignoring():
    init_blank_simulation()
    log = run_writer_with_args("dummy_property", "dummy_property_with_exception")
    assert "Uncaught exception during property calculation" in log

    assert db.get_halo("dummy_sim_1/step.1/1")['dummy_property'] == 1.0
    assert db.get_halo("dummy_sim_1/step.1/2")['dummy_property'] == 2.0
    assert db.get_halo("dummy_sim_1/step.2/1")['dummy_property'] == 2.0

    assert 'dummy_property' in db.get_halo("dummy_sim_1/step.1/1").keys()
    assert 'dummy_property_with_exception' not in db.get_halo("dummy_sim_1/step.1/1").keys()

