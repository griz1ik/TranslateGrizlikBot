import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs, LangDetectException

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменных окружения Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не установлен!")
    exit(1)

# Список поддерживаемых языков с эмодзи
LANGUAGE_EMOJIS = {
    'en': '🇺🇸', 'ru': '🇷🇺', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
    'it': '🇮🇹', 'pt': '🇵🇹', 'zh-cn': '🇨🇳', 'ja': '🇯🇵', 'ko': '🇰🇷',
    'ar': '🇸🇦', 'tr': '🇹🇷', 'hi': '🇮🇳', 'uk': '🇺🇦', 'pl': '🇵🇱',
    'nl': '🇳🇱', 'sv': '🇸🇪', 'no': '🇳🇴', 'da': '🇩🇰', 'fi': '🇫🇮',
    'cs': '🇨🇿', 'sk': '🇸🇰', 'hu': '🇭🇺', 'ro': '🇷🇴', 'bg': '🇧🇬',
    'el': '🇬🇷', 'he': '🇮🇱', 'id': '🇮🇩', 'th': '🇹🇭', 'vi': '🇻🇳'
}

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ru': 'Russian', 
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh-cn': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'hi': 'Hindi',
    'uk': 'Ukrainian',
    'pl': 'Polish',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'cs': 'Czech',
    'sk': 'Slovak',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'el': 'Greek',
    'he': 'Hebrew',
    'id': 'Indonesian',
    'th': 'Thai',
    'vi': 'Vietnamese'
}

DEFAULT_TARGET_LANGUAGES = ['en', 'ru', 'es', 'fr', 'de']

def detect_language_advanced(text):
    """Улучшенное определение языка с использованием langdetect"""
    try:
        # Если текст слишком короткий, используем упрощенный метод
        if len(text.strip()) < 3:
            return detect_language_simple(text)
        
        # Получаем все возможные языки с вероятностями
        languages = detect_langs(text)
        
        # Берем язык с наибольшей вероятностью
        best_lang = str(languages[0]).split(':')[0]
        
        # Проверяем, что язык поддерживается
        if best_lang in SUPPORTED_LANGUAGES:
            return best_lang
        else:
            # Если основной язык не поддерживается, пробуем альтернативы
            for lang_prob in languages:
                lang_code = str(lang_prob).split(':')[0]
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code
            
            # Если ничего не найдено, используем упрощенный метод
            return detect_language_simple(text)
            
    except LangDetectException:
        # Если langdetect не смог определить, используем упрощенный метод
        return detect_language_simple(text)
    except Exception as e:
        logging.error(f"Language detection error: {e}")
        return detect_language_simple(text)

def detect_language_simple(text):
    """Резервное определение языка по символам"""
    # Счетчики для разных алфавитов
    cyrillic_count = 0
    latin_count = 0
    arabic_count = 0
    hebrew_count = 0
    greek_count = 0
    
    for char in text:
        # Кириллица (русский, украинский, и т.д.)
        if '\u0400' <= char <= '\u04FF':
            cyrillic_count += 1
        # Латиница (английский, французский, и т.д.)
        elif '\u0041' <= char <= '\u007A' or '\u00C0' <= char <= '\u00FF':
            latin_count += 1
        # Арабский
        elif '\u0600' <= char <= '\u06FF':
            arabic_count += 1
        # Иврит
        elif '\u0590' <= char <= '\u05FF':
            hebrew_count += 1
        # Греческий
        elif '\u0370' <= char <= '\u03FF':
            greek_count += 1
    
    # Определяем преобладающий алфавит
    if cyrillic_count > latin_count and cyrillic_count > 0:
        return 'ru'  # По умолчанию русский для кириллицы
    elif arabic_count > 0:
        return 'ar'
    elif hebrew_count > 0:
        return 'he'
    elif greek_count > 0:
        return 'el'
    else:
        return 'en'  # По умолчанию английский

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🤖 **Бот-переводчик с улучшенным определением языка**

**Возможности:**
• Автоматическое определение языка сообщения
• Перевод на несколько языков одновременно
• Высокая точность распознавания

**Как использовать:**
1. Просто напиши сообщение - бот сам определит язык и переведет
2. Или укажи язык: `текст /язык`
3. Пример: `Hello world /ru`

**Команды:**
/setlang - настроить языки перевода
/lang - список всех языков
/help - помощь
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def set_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите языки через пробел\n"
            "Пример: `/setlang en ru es fr de`",
            parse_mode='Markdown'
        )
        return
    
    valid_langs = [lang for lang in context.args if lang in SUPPORTED_LANGUAGES]
    invalid_langs = [lang for lang in context.args if lang not in SUPPORTED_LANGUAGES]
    
    if not valid_langs:
        await update.message.reply_text("❌ Не указано валидных языков")
        return
    
    chat_id = update.message.chat_id
    if 'chat_settings' not in context.bot_data:
        context.bot_data['chat_settings'] = {}
    
    context.bot_data['chat_settings'][chat_id] = {'target_languages': valid_langs}
    
    response = f"✅ Установлены языки для перевода:\n"
    for lang in valid_langs:
        emoji = LANGUAGE_EMOJIS.get(lang, '🌐')
        response += f"{emoji} {SUPPORTED_LANGUAGES[lang]}\n"
    
    if invalid_langs:
        response += f"\n❌ Неподдерживаемые языки: {', '.join(invalid_langs)}"
    
    await update.message.reply_text(response)

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список языков"""
    languages_text = "🌍 **Поддерживаемые языки:**\n\n"
    
    # Группируем по популярности
    popular_langs = ['en', 'ru', 'es', 'fr', 'de', 'it', 'pt', 'zh-cn', 'ja', 'ko']
    other_langs = [code for code in SUPPORTED_LANGUAGES.keys() if code not in popular_langs]
    
    languages_text += "**Популярные:**\n"
    for code in popular_langs:
        emoji = LANGUAGE_EMOJIS.get(code, '🌐')
        languages_text += f"{emoji} `{code}` - {SUPPORTED_LANGUAGES[code]}\n"
    
    languages_text += "\n**Другие языки:**\n"
    for code in sorted(other_langs):
        emoji = LANGUAGE_EMOJIS.get(code, '🌐')
        languages_text += f"{emoji} `{code}` - {SUPPORTED_LANGUAGES[code]}\n"
    
    await update.message.reply_text(languages_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    help_text = """
📖 **Помощь по использованию бота-переводчика**

**Автоматический режим:**
Просто напишите любое сообщение - бот определит язык и переведет на установленные языки

**Ручной режим:**
`текст /язык` - перевод на конкретный язык
Пример: `Bonjour /en` → Hello

**Настройка:**
`/setlang en ru es` - установить языки для автоперевода
`/lang` - посмотреть все доступные языки

**Поддержка 30+ языков** с высокой точностью определения!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def auto_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    
    # Игнорируем команды
    if text.startswith('/'):
        return
    
    # Перевод на конкретный язык
    if ' /' in text and len(text.split(' /')) == 2:
        parts = text.split(' /')
        original_text, target_lang = parts[0].strip(), parts[1].strip().lower()
        
        if original_text and target_lang and target_lang in SUPPORTED_LANGUAGES:
            try:
                # Определяем исходный язык
                source_lang = detect_language_advanced(original_text)
                
                # Выполняем перевод
                translation = GoogleTranslator(source=source_lang, target=target_lang).translate(original_text)
                
                source_emoji = LANGUAGE_EMOJIS.get(source_lang, '🌐')
                target_emoji = LANGUAGE_EMOJIS.get(target_lang, '🌐')
                
                response = f"""
{source_emoji} **Исходный текст** ({SUPPORTED_LANGUAGES.get(source_lang, source_lang)}):
{original_text}

{target_emoji} **Перевод** ({SUPPORTED_LANGUAGES[target_lang]}):
{translation}
"""
                await update.message.reply_text(response)
                return
            except Exception as e:
                logging.error(f"Translation error: {e}")
                await update.message.reply_text("❌ Ошибка перевода")
                return
    
    # Автоматический перевод на несколько языков
    try:
        # Определяем исходный язык
        source_lang = detect_language_advanced(text)
        source_lang_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        
        # Получаем настройки для чата
        chat_id = update.message.chat_id
        target_languages = DEFAULT_TARGET_LANGUAGES
        
        if ('chat_settings' in context.bot_data and 
            chat_id in context.bot_data['chat_settings']):
            target_languages = context.bot_data['chat_settings'][chat_id]['target_languages']
        
        # Исключаем исходный язык и ограничиваем количество
        target_languages = [lang for lang in target_languages if lang != source_lang][:4]
        
        if not target_languages:
            target_languages = ['en', 'ru', 'es']
        
        source_emoji = LANGUAGE_EMOJIS.get(source_lang, '🌐')
        response = f"{source_emoji} **Обнаружен язык**: {source_lang_name}\n"
        response += f"**Исходный текст**:\n{text}\n\n**Переводы:**\n\n"
        
        successful_translations = 0
        
        for target_lang in target_languages:
            try:
                translation = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
                target_emoji = LANGUAGE_EMOJIS.get(target_lang, '🌐')
                response += f"{target_emoji} **{SUPPORTED_LANGUAGES[target_lang]}**:\n{translation}\n\n"
                successful_translations += 1
            except Exception as e:
                logging.error(f"Error translating to {target_lang}: {e}")
                continue
        
        if successful_translations > 0:
            response += f"---\n"
            response += f"💡 *Для перевода на другой язык: текст /язык*\n"
            response += f"⚙️ *Изменить языки: /setlang*"
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Не удалось выполнить перевод на указанные языки")
        
    except Exception as e:
        logging.error(f"Auto-translate error: {e}")
        await update.message.reply_text("❌ Произошла ошибка при переводе")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlang", set_languages))
    application.add_handler(CommandHandler("lang", show_languages))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_translate))
    
    # Запускаем бота
    logging.info("🤖 Бот с улучшенным определением языка запущен!")
    logging.info("🌍 Поддержка 30+ языков")
    application.run_polling()

if __name__ == '__main__':
    main()
