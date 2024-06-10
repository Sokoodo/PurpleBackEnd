from zope.interface import Interface


class IConfiguration(Interface):
    def get_global_data():
        """Return global data as a dictionary."""

    def get_local_data():
        """Return local data as a dictionary."""

    def get_instances(proc):
        """Return instances for a given process as a set."""

    def get_processes():
        """Return a set of processes."""

    def __eq__(other):
        """Check equality with another configuration."""
