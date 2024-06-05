import gc
from typing import Optional, Type, Union


class CodeErrorFactory(Exception):
    '''Payok API Exception'''

    def __init__(self, code: int = None, desc: str = None) -> None:
        self.code = int(code) if code else None
        self.desc = desc
        super().__init__(self.code)

    @classmethod
    def __call__(
            cls, code: Optional[int] = None, desc: Optional[int] = None
    ) -> Union["CodeErrorFactory", Type["CodeErrorFactory"]]:
        if desc:
            return cls.exception_to_raise(code, desc)
        return cls.exception_to_handle(code)

    @classmethod
    def exception_to_handle(
            cls, code: Optional[int] = None
    ) -> Type["CodeErrorFactory"]:
        if code is None:
            return cls

        catch_exc_classname = cls.generate_exc_classname(code)

        for obj in gc.get_objects():
            if obj.__class__.__name__ == catch_exc_classname:
                return obj.__class__

        return type(catch_exc_classname, (cls,), {})

    @classmethod
    def exception_to_raise(
            cls, code: int, desc: str
    ) -> "CodeErrorFactory":
        """ Returns an error with error code and error_description"""
        exception_type = type(cls.generate_exc_classname(code), (cls,), {})
        return exception_type(code, desc)

    @classmethod
    def generate_exc_classname(cls, code: Optional[int]) -> str:
        """ Generates unique exception classname based on error code """
        return f"{cls.__name__}_{code}"

    def __str__(self):
        return f"[{self.code}] {self.desc}\n"
