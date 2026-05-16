"""Module docstring."""  # pylint: disable=too-few-public-methods
class WorkloadBalancer:
    """Class docstring."""

    def distribute(
        self,
        nodes,
        workloads
    ):
        """Function docstring."""

        assignments = {}

        for index, workload in enumerate(workloads):

            node = nodes[
                index % len(nodes)
            ]

            assignments[
                workload
            ] = node

        return assignments
