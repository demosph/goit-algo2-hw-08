import time
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Очищає застарілі повідомлення у вікні користувача"""
        if user_id in self.user_messages:
            while self.user_messages[user_id] and self.user_messages[user_id][0] <= current_time - self.window_size:
                self.user_messages[user_id].popleft()
            if not self.user_messages[user_id]:
                del self.user_messages[user_id]  # Видалення користувача, якщо немає повідомлень

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи може користувач надіслати повідомлення"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_messages or len(self.user_messages[user_id]) < self.max_requests:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        """Записує нове повідомлення користувача, якщо це дозволено"""
        current_time = time.time()
        if self.can_send_message(user_id):
            if user_id not in self.user_messages:
                self.user_messages[user_id] = deque()
            self.user_messages[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Розраховує час очікування до можливості відправлення наступного повідомлення"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_messages or len(self.user_messages[user_id]) < self.max_requests:
            return 0.0
        return self.window_size - (current_time - self.user_messages[user_id][0])

# Демонстрація роботи
import random
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
