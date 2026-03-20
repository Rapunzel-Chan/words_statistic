import asyncio
import os
from collections import defaultdict
from typing import List, Dict
import re
from ...domain.entities.words_statistic import WordStatistics
from ...domain.interfaces.repos import IFileProcessor


class WordProcessor(IFileProcessor):
    """Процессор для обработки слов в файле"""

    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunk_size = chunk_size
        self.use_lemmatization = False

        try:
            import pymorphy3
            self.morph = pymorphy3.MorphAnalyzer()
            self.use_lemmatization = True
            print("Lemmatization enabled with pymorphy3")
        except ImportError:
            try:
                import pymorphy2
                self.morph = pymorphy2.MorphAnalyzer()
                self.use_lemmatization = True
                print("Lemmatization enabled with pymorphy2")
            except ImportError:
                print("Lemmatization not available, using simple normalization")

    async def process_file(self, file_path: str) -> List[WordStatistics]:
        """
        Обрабатывает файл и собирает статистику по словам
        """

        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Processing file: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")

        word_stats = defaultdict(lambda: {"total": 0, "lines": []})
        line_number = 0

        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    print(f"Using encoding: {encoding}")
                    while True:
                        line = await self._read_line_async(file)
                        if not line:
                            break

                        # Убираем лишние пробелы и переносы
                        line = line.strip()
                        if not line:
                            line_number += 1
                            continue

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

                        # Периодически выводим прогресс
                        if line_number % 100 == 0:
                            print(f"Processed {line_number} lines...")
                            await asyncio.sleep(0)
                break
            except UnicodeDecodeError:
                continue  # Пробуем следующую кодировку

        if line_number == 0:
            raise Exception("Could not read file with any encoding")

        print(f"Processed {line_number} lines, found {len(word_stats)} unique words")

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

        # Сортируем по убыванию частоты
        result.sort(key=lambda x: x.total_count, reverse=True)

        # Выводим топ-10 слов
        print("\nTop 10 words:")
        for i, stat in enumerate(result[:10], 1):
            print(f"  {i}. {stat.word_form}: {stat.total_count}")

        return result

    async def _read_line_async(self, file):
        """Асинхронное чтение строки"""
        line = file.readline()
        await asyncio.sleep(0)
        return line

    def _extract_words(self, line: str) -> List[str]:
        """Извлекает слова из строки"""
        # Разделяем по пробельным символам и убираем пустые строки
        words = re.findall(r'\b[а-яА-ЯёЁa-zA-Z]+\b', line)
        return words

    def _normalize_word(self, word: str) -> str:
        """
        Нормализует слово (приводит к начальной форме)
        """
        word_lower = word.lower()

        if self.use_lemmatization:
            try:
                parsed = self.morph.parse(word_lower)[0]
                return parsed.normal_form
            except:
                return word_lower
        else:
            # Упрощенная нормализация для русского языка
            # Удаляем типичные окончания
            word_lower = re.sub(r'(ами|ями|ах|ях|ов|ев|ей|ом|ем|е|у|ю|а|я|и|ы)$', '', word_lower)
            # Удаляем "ь" на конце
            word_lower = re.sub(r'ь$', '', word_lower)
            return word_lower
