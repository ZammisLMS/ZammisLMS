import logging
import os
from datetime import datetime
import tempfile # For creating temporary files securely

from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Adjust imports based on actual project structure.
try:
    # Assuming 'personal_finance_bot' is the root for these imports
    from database.db_handler import init_db, add_expense, get_expenses_by_category_for_month, get_expenses_for_month
    from bot.categorizer import categorizar_gasto
    from utils.helpers import parse_expense_message, generate_pie_chart, generate_expenses_csv
except (ImportError, ModuleNotFoundError) as e_import:
    logger = logging.getLogger(__name__) # temp logger for import error
    logger.debug(f"Import error: {e_import}. Attempting relative imports for local dev.")
    import sys
    PROJECT_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if PROJECT_ROOT_PATH not in sys.path:
        sys.path.append(PROJECT_ROOT_PATH)
    from database.db_handler import init_db, add_expense, get_expenses_by_category_for_month, get_expenses_for_month
    from bot.categorizer import categorizar_gasto
    from utils.helpers import parse_expense_message, generate_pie_chart, generate_expenses_csv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Re-assign logger after basicConfig is set, in case it was used in import error block
logger = logging.getLogger(__name__)

# Environment variable for the token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Olá! Sou seu bot de organização financeira.\n\n"
        "Envie despesas como 'Café 5,50' e eu salvarei para você.\n\n"
        "Comandos disponíveis:\n"
        "/resumo - Vê o resumo de gastos do mês atual.\n"
        "/pizza - Gera um gráfico de pizza dos gastos do mês.\n"
        "/exportar - Exporta os gastos do mês atual como um arquivo CSV."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles non-command text messages to parse and record expenses."""
    user = update.effective_user
    message_text = update.message.text
    user_id = user.id

    logger.info(f"Received message from user {user_id} ('{user.full_name}'): {message_text}")

    description, value = parse_expense_message(message_text)

    if description and value is not None:
        category = categorizar_gasto(description)
        try:
            add_expense(user_id, value, description, category)
            reply_text = f"Despesa '{description}' de R${value:.2f} adicionada à categoria '{category}'."
            logger.info(f"Expense added for user {user_id}: Description='{description}', Value={value:.2f}, Category='{category}'")
        except Exception as e:
            logger.error(f"Error adding expense for user {user_id} (Description: {description}, Value: {value}): {e}", exc_info=True)
            reply_text = "Desculpe, ocorreu um erro ao salvar sua despesa. Tente novamente."
    elif " " not in message_text.strip().replace(",","."):
        if not description and value is not None:
             reply_text = "Hmm, parece que você enviou um valor sem descrição. Por favor, envie no formato 'Descrição Valor' (ex: 'Café 3.50')."
        else:
            reply_text = "Por favor, envie a despesa no formato 'Descrição Valor' (ex: 'Café 3.50')."
    else:
        reply_text = "Não entendi. Por favor, envie a despesa no formato 'Descrição Valor' (ex: 'Café 3.50')."
        logger.warning(f"Failed to parse message from user {user_id}: '{message_text}'")

    await update.message.reply_text(reply_text)

async def resumo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a summary of expenses for the current month."""
    user_id = update.effective_user.id
    now = datetime.now()
    month, year = now.month, now.year

    logger.info(f"User {user_id} requested /resumo for {month}/{year}.")

    try:
        expenses = get_expenses_by_category_for_month(user_id, month, year)
        if not expenses:
            await update.message.reply_text("Você não tem despesas registradas para este mês.")
            return

        message = f"Resumo de gastos para {month:02d}/{year}:\n\n"
        total_geral = 0.0
        for category, total_value in expenses:
            message += f"{category}: R${total_value:.2f}\n"
            total_geral += total_value
        message += f"\nTotal: R${total_geral:.2f}"

        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error generating summary for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text("Desculpe, ocorreu um erro ao gerar o resumo.")

async def pizza_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a pie chart of expenses for the current month."""
    user_id = update.effective_user.id
    now = datetime.now()
    month, year = now.month, now.year

    logger.info(f"User {user_id} requested /pizza for {month}/{year}.")

    try:
        expenses_by_cat = get_expenses_by_category_for_month(user_id, month, year)
        if not expenses_by_cat:
            await update.message.reply_text("Sem dados para gerar o gráfico de pizza este mês.")
            return

        # Use a temporary file for the chart
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            chart_path = tmp_file.name

        logger.debug(f"Temporary chart path for user {user_id}: {chart_path}")

        chart_file_path = generate_pie_chart(expenses_by_cat, chart_path)

        if chart_file_path:
            try:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(chart_file_path, 'rb'))
                logger.info(f"Pie chart sent to user {user_id}.")
            finally: # Ensure cleanup even if sending fails
                if os.path.exists(chart_file_path):
                    os.remove(chart_file_path)
                    logger.debug(f"Temporary chart file {chart_file_path} removed.")
        else:
            await update.message.reply_text("Desculpe, não consegui gerar o gráfico de pizza.")
            logger.error(f"Pie chart generation failed for user {user_id} (returned None).")

    except Exception as e:
        logger.error(f"Error generating pie chart for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text("Desculpe, ocorreu um erro ao gerar o gráfico de pizza.")
        # Clean up temp file if it was created and an error occurred afterwards
        if 'chart_path' in locals() and os.path.exists(chart_path):
            os.remove(chart_path)
            logger.debug(f"Temporary chart file {chart_path} removed due to error.")


async def exportar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exports expenses for the current month as a CSV file."""
    user_id = update.effective_user.id
    now = datetime.now()
    month, year = now.month, now.year

    logger.info(f"User {user_id} requested /exportar for {month}/{year}.")

    try:
        expenses_data = get_expenses_for_month(user_id, month, year)
        if not expenses_data:
            await update.message.reply_text("Sem dados para exportar este mês.")
            return

        # Use a temporary file for the CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False, encoding='utf-8') as tmp_file:
            csv_path = tmp_file.name # Path to the temporary file

        logger.debug(f"Temporary CSV path for user {user_id}: {csv_path}")

        csv_file_path = generate_expenses_csv(expenses_data, csv_path)

        if csv_file_path:
            try:
                document = InputFile(open(csv_file_path, 'rb'), filename=f"despesas_{month:02d}_{year}.csv")
                await context.bot.send_document(chat_id=update.effective_chat.id, document=document)
                logger.info(f"CSV export sent to user {user_id}.")
            finally:
                if os.path.exists(csv_file_path):
                    os.remove(csv_file_path)
                    logger.debug(f"Temporary CSV file {csv_file_path} removed.")
        else:
            await update.message.reply_text("Desculpe, não consegui gerar o arquivo CSV.")
            logger.error(f"CSV generation failed for user {user_id} (returned None).")

    except Exception as e:
        logger.error(f"Error generating CSV export for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text("Desculpe, ocorreu um erro ao exportar os dados.")
        if 'csv_path' in locals() and os.path.exists(csv_path): # Check if csv_path was defined
            os.remove(csv_path)
            logger.debug(f"Temporary CSV file {csv_path} removed due to error.")


def run_bot() -> None:
    """Starts the bot."""
    if not TELEGRAM_TOKEN:
        logger.critical("TELEGRAM_TOKEN environment variable not set!")
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable not set. The bot cannot start.")
        return

    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        print(f"CRITICAL ERROR: Failed to initialize database. Bot cannot start. Error: {e}")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("resumo", resumo_command))
    application.add_handler(CommandHandler("pizza", pizza_command))
    application.add_handler(CommandHandler("exportar", exportar_command))

    # Message Handler for expense messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot polling...")
    print("Bot is starting. Press Ctrl-C to stop.")
    try:
        application.run_polling()
    except Exception as e:
        logger.critical(f"Bot encountered a fatal error: {e}", exc_info=True)
        print(f"Bot stopped due to a critical error: {e}")

if __name__ == "__main__":
    # Load .env for local development if needed (python-dotenv)
    # from dotenv import load_dotenv
    # project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # dotenv_path = os.path.join(project_dir, '.env')
    # if os.path.exists(dotenv_path):
    #     logger.info(f"Loading .env file from {dotenv_path}")
    #     load_dotenv(dotenv_path)
    #     TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") # Reload after loading .env
    # else:
    #     logger.info(f".env file not found at {dotenv_path}. Ensuring TELEGRAM_TOKEN is set globally.")

    if not TELEGRAM_TOKEN:
         print("WARNING: TELEGRAM_TOKEN is not set. The bot will not be able to connect to Telegram.")
         print("For development, you can set it in your shell, a .env file in the project root, or ensure this main.py is run from a context where it's set.")

    print("Attempting to run the bot...")
    run_bot()
