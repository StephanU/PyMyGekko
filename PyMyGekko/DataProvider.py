class DataSubscriberInterface:
    def update_status(self, status):
        pass

    def update_resources(self, resource):
        pass


class DataProvider:
    _subscriber: list[DataSubscriberInterface] = []

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, resources):
        self._resources = resources
        for subscriber in self._subscriber:
            subscriber.update_resources(self._resources)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        for subscriber in self._subscriber:
            subscriber.update_status(self._status)

    def subscribe(self, subscriber: DataSubscriberInterface):
        self._subscriber.append(subscriber)
