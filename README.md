# Video Question Generator

Автоматический скрипт для обработки видео и генерации вопросов из интервью.

## Возможности

- 📹 Обрабатывает все видео файлы в текущей папке
- 🎯 Транскрибирует аудио с помощью OpenAI Whisper
- 🌍 Поддерживает русский и английский языки (автоопределение)
- 🤖 Генерирует вопросы с помощью Ollama
- 👥 Определяет роли говорящих (интервьюер/интервьюируемый)
- 📁 Организует выходные файлы в папки

## Требования

- Python 3.8+
- macOS (оптимизировано для MacBook M4 Pro)
- Установленный Ollama
- Ffmpeg (для обработки видео)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd CreateQuestionsFromVideos
```

2. Установите зависимости Python:
```bash
pip install -r requirements.txt
```

3. Установите Ollama:
```bash
# На macOS
brew install ollama

# Запустите сервис Ollama
ollama serve
```

4. Установите ffmpeg:
```bash
brew install ffmpeg
```

## Использование

1. Поместите видео файлы в папку со скриптом
2. Запустите скрипт:
```bash
python video_processor.py
```

3. Дождитесь завершения обработки
4. Проверьте результаты:
   - `transcribed/` - папка с транскрипциями
   - `questions/` - папка с вопросами

## Поддерживаемые форматы видео

- MP4, AVI, MOV, MKV, WMV, FLV
- WebM, M4V, 3GP, OGV

## Структура выходных файлов

### Транскрипции (`transcribed/`)
- `video_name_transcript.txt` - полная транскрипция видео

### Вопросы (`questions/`)
- `video_name_questions.json` - структурированные вопросы с метаданными

## Формат файла вопросов

```json
{
  "video_name": "interview.mp4",
  "total_questions": 15,
  "by_speaker": {
    "interviewer": [...],
    "interviewee": [...],
    "unknown": [...]
  },
  "by_type": {
    "technical": [...],
    "behavioral": [...],
    "general": [...]
  },
  "all_questions": [
    {
      "question": "Расскажите о своем опыте работы с Python",
      "speaker": "interviewer",
      "type": "technical"
    }
  ]
}
```

## Настройки

### Модель Ollama
По умолчанию используется `llama3.1:8b` для баланса производительности и качества на M4 MacBook Pro.

### Размер чанков
Текст разбивается на части по ~3000 токенов для оптимальной обработки.

## Логирование

Скрипт создает файл `video_processor.log` с подробной информацией о процессе обработки.

## Troubleshooting

### Ошибка "Ollama model not found"
```bash
ollama pull llama3.1:8b
```

### Ошибка с ffmpeg
```bash
brew install ffmpeg
```

### Ошибка с правами доступа
```bash
chmod +x video_processor.py
```

## Лицензия

MIT License