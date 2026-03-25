from ..util import to_unicode


def normalize_cli_options(mapping):
    # Prevent circular imports
    from ..user_configs.config_options import ConfigInput

    for k, v in mapping.items():

        if v is None or v is False:
            continue

        # we need special handling for 'with' since it is a reserved
        # keyword in Python, so we call it 'decospecs' in click args
        if k == "decospecs":
            k = "with"

        if k in ("config", "config_value"):
            # we gather them all in one option but actually
            # need to send them one at a time using --config-value <name> kv.<name>.
            if isinstance(v, dict):
                for config_name in v.keys():
                    yield "--config-value"
                    yield to_unicode(config_name)
                    yield to_unicode(ConfigInput.make_key_name(config_name))
                continue

        k = k.replace("_", "-")

        if isinstance(v, (list, tuple, set)):
            if not v:
                continue
            values = v
        else:
            values = [v]

        for value in values:
            yield "--%s" % k
            if not isinstance(value, bool):
                if isinstance(value, tuple):
                    for vv in value:
                        yield to_unicode(vv)
                else:
                    yield to_unicode(value)
