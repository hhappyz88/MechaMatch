from pydantic import RootModel


class ProcessorConfig(RootModel[dict[str, list[dict[str, str]]]]):
    """
    Mapping of states to processor configuration files
    configuration should be in the format
    {
        class: str
        **optional additional params
    }
    """
