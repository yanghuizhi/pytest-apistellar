import json
import asyncio

from toolkit import load_class as _load


class Prop(object):

    def __init__(self,
                 obj,
                 name,
                 ret_val=None,
                 ret_factory=None,
                 async=False,
                 callable=True):
        self.obj = obj
        self.name = name
        self.ret_val = ret_val
        self.ret_factory = ret_factory and _load(ret_factory)
        self.async = async
        self.callable = callable

    def __iter__(self):
        yield self.obj
        yield self.name
        if self.callable:
            yield self
        else:
            yield self.ret_val

    def __call__(self, *args, **kwargs):
        if self.ret_factory:
            factory = self.ret_factory(*args, **kwargs)
            ret_val = factory.product()
        else:
            ret_val = self.ret_val

        if self.async:
            loop = asyncio.get_event_loop()
            future = loop.create_future()
            future.set_result(ret_val)
            return future
        else:
            return ret_val


class Object(object):

    def __init__(self, mock):
        self.obj_name = mock["obj"]
        self.obj = _load(self.obj_name)
        self.elements = set()
        for prop in mock.get("props", []):
            self.elements.add(Prop(self.obj, **prop))

    def find(self, obj_name, name):
        if self.obj_name == obj_name:
            for element in self.elements:
                if element.name == name:
                    return element


class Parser(object):

    def __init__(self, config_path):
        self.meta = json.load(open(config_path))
        self.objects = [Object(mock) for mock in self.meta["mocks"]]

    def find_mock(self, *mock_names):
        for mock_name in mock_names:
            obj_name, _, prop = mock_name.rpartition(".")

            for obj in self.objects:
                mock = obj.find(obj_name, prop)
                if mock:
                    yield mock
                    break
            else:
                print(f"Mock of {mock_name} not found. ")
