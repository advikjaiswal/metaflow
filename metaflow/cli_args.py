from .user_configs.config_options import ConfigInput
from .util import to_unicode


class CLIArgs(object):
    def __init__(self):
        self._top_kwargs = {}
        self._step_kwargs = {}

    def _set_step_kwargs(self, kwargs):
        self._step_kwargs = kwargs or {}

    def _set_top_kwargs(self, kwargs):
        self._top_kwargs = kwargs or {}

    @property
    def top_kwargs(self):
        return self._top_kwargs

    @property
    def step_kwargs(self):
        return self._step_kwargs

    def step_command(
        self, executable, script, step_name, top_kwargs=None, step_kwargs=None
    ):
        cmd = [executable, "-u", script]

        top_kwargs = top_kwargs or self._top_kwargs
        step_kwargs = step_kwargs or self._step_kwargs

        cmd.extend(list(self._options(top_kwargs)))
        cmd.extend(["step", step_name])
        cmd.extend(list(self._options(step_kwargs)))

        return cmd

    @staticmethod
    def _options(mapping):
        if not mapping:
            return

        if not isinstance(mapping, dict):
            raise TypeError("Expected mapping to be a dict, got %s" % type(mapping))

        for k, v in mapping.items():

            # Ignore None or explicitly False
            if v is None or v is False:
                continue

            # Handle reserved keyword
            if k == "decospecs":
                k = "with"

            # Special config handling
            if k in ("config", "config_value"):
                if not isinstance(v, dict):
                    continue
                for config_name in v.keys():
                    yield "--config-value"
                    yield to_unicode(config_name)
                    yield to_unicode(ConfigInput.make_key_name(config_name))
                continue

            k = k.replace("_", "-")

            # Normalize values
            if isinstance(v, (list, tuple, set)):
                values = v
            else:
                values = [v]

            for value in values:
                yield "--%s" % k
                if not isinstance(value, bool):
                    yield to_unicode(value)


cli_args = CLIArgs()
