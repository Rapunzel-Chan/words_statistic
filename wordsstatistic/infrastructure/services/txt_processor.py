import asyncio
from collections import defaultdict
from typing import List, Dict
import re
from ...domain.entities.words_statistic import WordStatistics
from ...domain.interfaces.repos import IFileProcessor


class WordProcessor(IFileProcessor):
    """Процессор для обработки слов в файле"""

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size

    async def process_file(self, file_path: str) -> List[WordStatistics]:
        """
        Обрабатывает файл и собирает статистику по словам
        Использует потоковую обработку для больших файлов
        """
        word_stats = defaultdict(lambda: {"total": 0, "lines": []})
        line_number = 0

        # Открываем файл и читаем построчно
        with open(file_path, 'r', encoding='utf-8') as file:
            while True:
                line = await self._read_line_async(file)
                if not line:
                    break

                # Обрабатываем строку
                words = self._extract_words(line)

                # Собираем статистику по словам в строке
                line_word_count = defaultdict(int)
                for word in words:
                    normalized = self._normalize_word(word)
                    line_word_count[normalized] += 1

                # Обновляем общую статистику
                for word, count in line_word_count.items():
                    stats = word_stats[word]
                    stats["total"] += count
                    # Добавляем счет для текущей строки
                    while len(stats["lines"]) <= line_number:
                        stats["lines"].append(0)
                    stats["lines"][line_number] = count

                line_number += 1

                # Периодически делаем yield для предотвращения блокировки
                if line_number % 100 == 0:
                    await asyncio.sleep(0)

        # Преобразуем результат
        result = []
        for word, stats in word_stats.items():
            # Заполняем нулями пропущенные строки
            while len(stats["lines"]) < line_number:
                stats["lines"].append(0)

            result.append(WordStatistics(
                word_form=word,
                total_count=stats["total"],
                line_counts=stats["lines"]
            ))

        return result

    async def _read_line_async(self, file):
        """Асинхронное чтение строки из файла"""
        # Имитация асинхронного чтения
        line = file.readline()
        await asyncio.sleep(0)  # Даем возможность переключиться другим задачам
        return line

    def _extract_words(self, line: str) -> List[str]:
        """Извлекает слова из строки"""
        # Разделяем по пробельным символам и убираем пустые строки
        words = re.findall(r'\b[а-яА-ЯёЁa-zA-Z]+\b', line)
        return words

    def _normalize_word(self, word: str) -> str:
        """Нормализует слово (приводит к начальной форме)"""
        # Простая нормализация - приводим к нижнему регистру
        # В реальном проекте здесь должна быть более сложная логика
        return word.lower()
