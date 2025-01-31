import yaml


class YAMLParser(yaml.YAMLObject):
    def __init__(self, **kwargs):
        params = list(vars(self.__class__)['__annotations__'].keys())
        kwargs = {k: v for k, v in kwargs.items() if k in params}

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.yaml_tag = u'!{}'.format(cls.__name__)

    def __repr__(self):
        vars = self.__dict__
        var_string = ', '.join(
            [f"{key}={value}" for key, value in vars.items()])
        return f"{self.__class__.__name__}({var_string})"

    @classmethod
    def from_yaml(cls, loader, node):
        if isinstance(node.value, list):
            return cls(**loader.construct_mapping(node))
        else:
            unique_param = list(vars(cls)['__annotations__'].keys())[0]
            return cls(**{unique_param: node.__dict__["value"]})

    @classmethod
    def to_yaml(cls, dumper, data):
        if hasattr(cls, "scalar") and cls.scalar is True:
            return dumper.represent_scalar(cls.yaml_tag, list(data.__dict__.values())[0])
        else:
            return dumper.represent_mapping(cls.yaml_tag, data.__dict__)
