from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Configura le API Key
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
GOOGLE_PLACES_API_KEY = "your_google_api_key"

# Funzione per ottenere ristoranti
def get_restaurants(location, radius=5000, keyword=""):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": radius,
        "type": "restaurant",
        "keyword": keyword,
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params).json()
    return response.get("results", [])

# Comando /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Ciao! Condividi la tua posizione e un tipo di ristorante (es. pizza, sushi) per iniziare!"
    )

# Comando per cercare ristoranti
def search(update: Update, context: CallbackContext) -> None:
    if "location" not in context.user_data:
        update.message.reply_text("Prima condividi la tua posizione!")
        return

    user_location = context.user_data["location"]
    category = " ".join(context.args) if context.args else ""
    if not category:
        update.message.reply_text("Specifica una categoria di ristorante! Esempio: /search pizza")
        return

    # Cerca ristoranti
    restaurants = get_restaurants(user_location, keyword=category)
    if not restaurants:
        update.message.reply_text("Nessun ristorante trovato.")
        return

    # Formatta i risultati
    for restaurant in restaurants[:5]:  # Mostra solo i primi 5 risultati
        name = restaurant.get("name", "Senza nome")
        rating = restaurant.get("rating", "N/A")
        address = restaurant.get("vicinity", "Indirizzo non disponibile")
        update.message.reply_text(
            f"🍴 {name}\n⭐ Rating: {rating}\n📍 {address}"
        )

# Gestione della posizione
def handle_location(update: Update, context: CallbackContext) -> None:
    user_location = f"{update.message.location.latitude},{update.message.location.longitude}"
    context.user_data["location"] = user_location
    update.message.reply_text("Posizione ricevuta! Ora invia una categoria di ristorante (es. pizza, sushi).")

# Configura il bot
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("search", search))
    updater.dispatcher.add_handler(MessageHandler(filters.LOCATION, handle_location))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
