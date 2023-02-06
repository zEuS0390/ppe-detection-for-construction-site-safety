class Singleton(type):

    _instances = {}

    def __call__(_cls, *args, **kwargs) -> any:
        if _cls not in _cls._instances:
            _cls._instances[_cls] = super(Singleton, _cls).__call__(*args, **kwargs)
        return _cls._instances[_cls]

    def getInstance(_cls) -> any:
        if _cls in _cls._instances:
            return _cls._instances[_cls]
        raise KeyError(f"Instance of '{_cls.__name__}' does not exist!")