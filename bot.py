import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator, LANGUAGES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменных окружения Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logging.error("❌ BOT_TOKEN не установлен!")
    exit(1)

# Инициализация переводчика
translator = Translator()

# Список поддерживаемых языков с эмодзи
LANGUAGE_EMOJIS = {
    'en': '🇺🇸', 'ru': '🇷🇺', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
    'it': '🇮🇹', 'pt': '🇵🇹', 'zh-cn': '🇨🇳', 'ja': '🇯🇵', 'ko': '🇰🇷',
    'ar': '🇸🇦', 'tr': '🇹🇷', 'hi': '🇮🇳', 'uk': '🇺🇦'
}

DEFAULT_TARGET_LANGUAGES = ['en', 'ru', 'es', 'fr', 'de']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🤖 **Бот-переводчик с автоопределением языка**

**Просто напиши сообщение в группе - я переведу его на несколько языков!**

**Также можно:**
- `текст /язык` - перевод на конкретный язык
- `/setlang en ru es` - настроить языки перевода
- `/lang` - список всех языков

**Пример:**
`Привет всем /en` → переведет на английский
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def set_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите языки: `/setlang en ru es`", parse_mode='Markdown')
        return
    
    valid_langs = [lang for lang in context.args if lang in LANGUAGES]
    
    if not valid_langs:
        await update.message.reply_text("❌ Не указано валидных языков")
        return
    
    chat_id = update.message.chat_id
    if 'chat_settings' not in context.bot_data:
        context.bot_data['chat_settings'] = {}
    
    context.bot_data['chat_settings'][chat_id] = {'target_languages': valid_langs}
    
    response = f"✅ Установлены языки:\n"
    for lang in valid_langs:
        emoji = LANGUAGE_EMOJIS.get(lang, '🌐')
        response += f"{emoji} {LANGUAGES[lang]}\n"
    
    await update.message.reply_text(response)

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список языков"""
    languages_text = "🌍 **Поддерживаемые языки:**\n\n"
    for code, name in LANGUAGES.items():
        if code in LANGUAGE_EMOJIS:
            emoji = LANGUAGE_EMOJIS[code]
            languages_text += f"{emoji} `{code}` - {name}\n"
        else:
            languages_text += f"`{code}` - {name}\n"
    
    await update.message.reply_text(languages_text[:4000], parse_mode='Markdown')

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
        
        if original_text and target_lang and target_lang in LANGUAGES:
            try:
                translation = translator.translate(original_text, dest=target_lang)
                source_emoji = LANGUAGE_EMOJIS.get(translation.src, '🌐')
                target_emoji = LANGUAGE_EMOJIS.get(target_lang, '🌐')
                
                response = f"""
{source_emoji} **Исходный текст**:
{original_text}

{target_emoji} **Перевод ({LANGUAGES[target_lang]})**:
{translation.text}
                """
                await update.message.reply_text(response)
                return
            except Exception as e:
                logging.error(f"Translation error: {e}")
    
    # Автоматический перевод
    try:
        detected = translator.detect(text)
        source_lang = detected.lang
        
        chat_id = update.message.chat_id
        target_languages = DEFAULT_TARGET_LANGUAGES
        
        if ('chat_settings' in context.bot_data and 
            chat_id in context.bot_data['chat_settings']):
            target_languages = context.bot_data['chat_settings'][chat_id]['target_languages']
        
        target_languages = [lang for lang in target_languages if lang != source_lang][:3]
        
        if not target_languages:
            target_languages = ['en', 'ru']
        
        source_emoji = LANGUAGE_EMOJIS.get(source_lang, '🌐')
        response = f"{source_emoji} **Исходный текст**:\n{text}\n\n**Переводы:**\n\n"
        
        for target_lang in target_languages:
            translation = translator.translate(text, src=source_lang, dest=target_lang)
            target_emoji = LANGUAGE_EMOJIS.get(target_lang, '🌐')
            response += f"{target_emoji} **{LANGUAGES[target_lang]}**:\n{translation.text}\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Auto-translate error: {e}")
        await update.message.reply_text("❌ Ошибка перевода")

def main():
    # Проверяем токен
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logging.error("❌ BOT_TOKEN не установлен!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlang", set_languages))
    application.add_handler(CommandHandler("lang", show_languages))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_translate))
    
    # Запускаем бота
    logging.info("🤖 Бот запущен на Railway!")
    application.run_polling()

if __name__ == '__main__':
    main()
