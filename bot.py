from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Configura le API Key
TELEGRAM_BOT_TOKEN = "7574217510:AAHdLAdzc4VICVkayLHgA7QDWXs4YvJ2uLY"
GOOGLE_PLACES_API_KEY = "AIzaSyBRvc9IGLGyDU9QUujqHsBGaVTQTQpL09s"

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
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Ciao! Condividi la tua posizione e un tipo di ristorante (es. pizza, sushi) per iniziare!"
    )

# Comando per cercare ristoranti
async def search(update: Update, context: CallbackContext) -> None:
    if "location" not in context.user_data:
        await update.message.reply_text("Prima condividi la tua posizione!")
        return

    user_location = context.user_data["location"]
    category = " ".join(context.args) if context.args else ""
    if not category:
        await update.message.reply_text("Specifica una categoria di ristorante! Esempio: /search pizza")
        return

    # Cerca ristoranti
    restaurants = get_restaurants(user_location, keyword=category)
    if not restaurants:
        await update.message.reply_text("Nessun ristorante trovato.")
        return

    # Formatta i risultati
    for restaurant in restaurants[:5]:  # Mostra solo i primi 5 risultati
        name = restaurant.get("name", "Senza nome")
        rating = restaurant.get("rating", "N/A")
        address = restaurant.get("vicinity", "Indirizzo non disponibile")
        await update.message.reply_text(
            f"🍴 {name}\n⭐ Rating: {rating}\n📍 {address}"
        )

# Gestione della posizione
async def handle_location(update: Update, context: CallbackContext) -> None:
    user_location = f"{update.message.location.latitude},{update.message.location.longitude}"
    context.user_data["location"] = user_location
    await update.message.reply_text("Posizione ricevuta! Ora invia una categoria di ristorante (es. pizza, sushi).")

# Configura il bot
def main():
    # Crea l'istanza dell'applicazione
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Aggiungi i gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Avvia il bot
    application.run_polling()

if __name__ == "__main__":
    main()
