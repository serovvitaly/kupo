from abc import ABCMeta, abstractmethod, abstractproperty
import urllib.request


class AbstractOffer:
    """
    Базовый класс для всех моделей офферов
    """
    def __init__(self):
        pass


class AbstractProvider:
    __metaclass__ = ABCMeta

    def get_content_by_url(self, url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            return f.read().decode('utf-8')

    @abstractproperty
    def find(self):
        pass
