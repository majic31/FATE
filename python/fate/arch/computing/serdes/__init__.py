from fate.arch.config import cfg


def get_serdes_by_type(serdes_type: int):
    if serdes_type == 0:
        if cfg.safety.serdes.restricted_type == "unrestricted":
            from ._unrestricted_serdes import get_unrestricted_serdes

            return get_unrestricted_serdes()
        elif cfg.safety.serdes.restricted_type == "restricted":
            from ._restricted_serdes import get_restricted_serdes

            return get_restricted_serdes()
        else:
            raise ValueError(f"restricted type `{cfg.safety.serdes.restricted_type}` not supported")
    elif serdes_type == 1:
        from ._integer_serdes import get_integer_serdes

        return get_integer_serdes()
    else:
        raise ValueError(f"serdes type `{serdes_type}` not supported")