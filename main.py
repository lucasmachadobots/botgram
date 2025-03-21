from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import datetime
import os  # Adicionado para pegar variável de ambiente

# Variável global para controlar o estado do usuário
user_states = {}

# Lista de perguntas e respostas para o quiz
quiz_questions = [
    {"question": "Qual time venceu a Copa do Mundo de 1998?", "answer": "França"},
    {"question": "Quem é o maior artilheiro da história da Seleção Brasileira?", "answer": "Pelé"},
    {"question": "Qual clube brasileiro tem mais títulos mundiais?", "answer": "São Paulo"},
    {"question": "Quem ganhou a Bola de Ouro em 2021?", "answer": "Lionel Messi"},
    {"question": "Qual jogador tem mais gols na história do futebol?", "answer": "Cristiano Ronaldo"},
    {"question": "Qual time venceu a Copa do Mundo de 2002?", "answer": "Brasil"},
    {"question": "Quem foi o artilheiro da Copa do Mundo de 2014?", "answer": "James Rodríguez"},
    {"question": "Qual time venceu a UEFA Champions League em 2020?", "answer": "Bayern de Munique"},
    {"question": "Quem é o técnico do Liverpool desde 2015?", "answer": "Jürgen Klopp"},
    {"question": "Qual jogador brasileiro é conhecido como 'Rei do Futebol'?", "answer": "Pelé"}
]

async def greet_user(update: Update):
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Bom dia"
    elif current_hour < 18:
        greeting = "Boa tarde"
    else:
        greeting = "Boa noite"
    
    await update.message.reply_text(f"{greeting}, {update.message.from_user.first_name}! 😊⚽️")

async def start(update: Update, context: CallbackContext):
    await greet_user(update)

    keyboard = [
        [InlineKeyboardButton("Assistir Jogos Ao Vivo", url='https://whatsapp.com/channel/0029Vb6Spns9RZARAUYXbB1N')],
        [InlineKeyboardButton("Entrar no Grupo de Futebol", url='https://chat.whatsapp.com/CIyXd6fUqmKFBlOPb23Adi')],
        [InlineKeyboardButton("Acessar Canal do Telegram", url="https://t.me/acessotorcedor")],
        [InlineKeyboardButton("Seguir no Instagram", url="https://instagram.com/acessotorcedorbr")],
        [InlineKeyboardButton("Quiz Futebol", callback_data='quiz')],
        [InlineKeyboardButton("Feedback", callback_data='feedback')],
        [InlineKeyboardButton("Ajuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Olá! Bem-vindo ao Acesso Torcedor. Escolha uma opção abaixo:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await query.edit_message_text(
            "Aqui estão as opções que você pode usar:\n\n"
            "1. Assistir Jogos Ao Vivo\n"
            "2. Entrar no Grupo de Futebol\n"
            "3. Acessar Canal do Telegram\n"
            "4. Seguir no Instagram\n"
            "5. Dar Feedback sobre o bot\n"
            "6. Participar de um Quiz de Futebol\n\n"
            "Clique nos botões para interagir com o bot!"
        )
    
    elif query.data == 'feedback':
        await query.edit_message_text("Por favor, envie sua sugestão ou comentário sobre o bot. O que você acha que pode melhorar? 🤔")
        user_states[update.effective_user.id] = 'waiting_feedback'
    
    elif query.data == 'quiz':
        await start_quiz(update, context)

async def start_quiz(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states[user_id] = {'state': 'in_quiz', 'score': 0, 'current_question': 0}
    await ask_question(update, context)

async def ask_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_state = user_states[user_id]
    question_index = user_state['current_question']
    question = quiz_questions[question_index]['question']

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❓ Pergunta {question_index + 1}: {question}")

async def process_quiz_answer(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_state = user_states.get(user_id)

    if user_state and user_state['state'] == 'in_quiz':
        user_answer = update.message.text
        correct_answer = quiz_questions[user_state['current_question']]['answer']

        if user_answer.lower() == correct_answer.lower():
            user_state['score'] += 1
            await update.message.reply_text("🎉 Correto! Você acertou! 🥳")
        else:
            await update.message.reply_text(f"❌ Errado! A resposta correta era: {correct_answer}.")

        user_state['current_question'] += 1

        if user_state['current_question'] < len(quiz_questions):
            await ask_question(update, context)
        else:
            await update.message.reply_text(f"🏆 Quiz terminado! Você acertou {user_state['score']} de {len(quiz_questions)} perguntas. 🎉")
            await update.message.reply_text("Deseja jogar novamente? (Digite 'sim' para jogar ou 'não' para voltar ao menu.)")
            user_states[user_id] = {'state': 'waiting_quiz_restart'}

async def restart_quiz(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if update.message.text.lower() == 'sim':
        await start_quiz(update, context)
    elif update.message.text.lower() == 'não':
        await update.message.reply_text("Ok, voltando ao menu principal! 😊")
        await start(update, context)
    else:
        await update.message.reply_text("Por favor, responda com 'sim' ou 'não'.")

async def respond_to_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_states.get(user_id) == 'waiting_feedback':
        await update.message.reply_text("Obrigado pelo seu feedback! 😊")
        await update.message.reply_text("Deseja algo mais? (Digite 'sim' para continuar ou 'não' para finalizar)")
        user_states[user_id] = 'waiting_for_more'
        return

    if user_states.get(user_id) and user_states[user_id]['state'] == 'in_quiz':
        await process_quiz_answer(update, context)
        return

    if user_states.get(user_id) and user_states[user_id]['state'] == 'waiting_quiz_restart':
        await restart_quiz(update, context)
        return

    await start(update, context)

async def process_more(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if update.message.text.lower() == 'sim':
        await start(update, context)
        user_states[user_id] = None
    elif update.message.text.lower() == 'não':
        await update.message.reply_text("Acesso Torcedor agradece o seu contato! Até logo! 👋")
        user_states[user_id] = None
    else:
        await update.message.reply_text("Por favor, responda com 'sim' ou 'não'.")

def main():
    # Pega o token da variável de ambiente
    token = os.getenv("TELEGRAM_TOKEN")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_more))

    application.run_polling()

if __name__ == '__main__':
    main()
