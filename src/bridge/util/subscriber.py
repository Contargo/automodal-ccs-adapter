from abc import abstractmethod

from overrides import EnforceOverrides

from .types import Collision, Position


class MqttClientSubscriber(EnforceOverrides):
    @abstractmethod
    def push_collision(self, data: Collision) -> None:
        pass
    
    
class SPSClientSubscriber(EnforceOverrides):
    @abstractmethod
    def push_position(self, data: Position) -> None:
        pass