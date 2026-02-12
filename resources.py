from typing import Dict


class ResourceTransaction:
    """Просто хранит стоимость чего-либо в виде словаря"""

    def __init__(self, cost_dict: Dict[str, int] = None):
        self.cost = cost_dict.copy() if cost_dict else {}

    def can_afford(self, storage: Dict[str, int]) -> bool:
        """Хватает ли ресурсов в хранилище?"""
        for resource, amount in self.cost.items():
            if storage.get(resource, 0) < amount:
                return False
        return True

    def apply(self, storage: Dict[str, int], add: bool = False) -> bool:
        """
        Применить транзакцию к хранилищу
        add=True: добавляем ресурсы (возврат)
        add=False: вычитаем ресурсы (оплата)
        """
        if not add and not self.can_afford(storage):
            return False

        for resource, amount in self.cost.items():
            if add:
                storage[resource] = storage.get(resource, 0) + amount
            else:
                storage[resource] = storage.get(resource, 0) - amount
        return True

    def get_refund(self, percentage: float = 0.5) -> 'ResourceTransaction':
        """Получить часть стоимости назад"""
        refund = {}
        for resource, amount in self.cost.items():
            refund[resource] = int(amount * percentage)
        return ResourceTransaction(refund)

    def __str__(self):
        if not self.cost:
            return "Бесплатно"
        return ", ".join(f"{amount} {res}" for res, amount in self.cost.items())


class ResourceStorage:
    """Простое хранилище ресурсов внутри здания"""

    def __init__(self, capacity: Dict[str, int] = None):
        """
        capacity: {'Медь': 10, 'Уголь': 5}
        None или пустой словарь = бесконечное хранилище (для ядра)
        """
        self.capacity = capacity.copy() if capacity else {}
        self.resources = {res: 0 for res in self.capacity.keys()}
        self.is_infinite = not bool(capacity)  # Если capacity пустой - бесконечное

    def can_add(self, resource: str, amount: int = 1) -> bool:
        """Можно ли добавить ресурс?"""
        if self.is_infinite:
            return True
        if resource not in self.capacity:
            return False
        return self.resources.get(resource, 0) + amount <= self.capacity[resource]

    def add(self, resource: str, amount: int = 1) -> bool:
        """Добавить ресурс"""
        if not self.can_add(resource, amount):
            return False
        self.resources[resource] = self.resources.get(resource, 0) + amount
        return True

    def has(self, resource: str, amount: int = 1) -> bool:
        """Есть ли ресурс в нужном количестве?"""
        return self.resources.get(resource, 0) >= amount

    def remove(self, resource: str, amount: int = 1) -> bool:
        """Забрать ресурс"""
        if not self.has(resource, amount):
            return False
        self.resources[resource] -= amount
        return True

    def get_amount(self, resource: str) -> int:
        """Сколько есть ресурса?"""
        return self.resources.get(resource, 0)

    def clear(self):
        """Очистить хранилище"""
        self.resources = {res: 0 for res in self.resources.keys()}

    def is_empty(self) -> bool:
        """Пустое ли хранилище?"""
        return all(amount == 0 for amount in self.resources.values())

    def is_full(self, resource: str = None) -> bool:
        """Заполнено ли хранилище?"""
        if self.is_infinite:
            return False
        if resource:
            return self.resources.get(resource, 0) >= self.capacity.get(resource, 0)
        return all(self.resources.get(res, 0) >= self.capacity.get(res, 0)
                   for res in self.capacity.keys())

    def get_all(self) -> Dict[str, int]:
        """Получить все ресурсы"""
        return self.resources.copy()

    def __str__(self):
        items = [f"{res}: {amt}" for res, amt in self.resources.items() if amt > 0]
        return " | ".join(items) if items else "Пусто"