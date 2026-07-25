# LPU Food Booking Bot

Flask-based food ordering MVP with a WhatsApp chatbot, MySQL order storage,
an admin dashboard, and a student ordering portal.

## Start locally

1. Create a MySQL database named `food_booking_bot` and run `database/schema.sql`.
2. Copy the required credentials into `.env` (this file must never be committed).
3. Install packages: `venv\\Scripts\\pip install -r requirements.txt`
4. For an existing database, run: `venv\\Scripts\\python -m database.migrate`
5. Start the app: `venv\\Scripts\\python app.py`

Open `/student/login` for the student portal and `/admin/login` for the admin dashboard.

## Current scope

Student login, menu search, cart, pickup selection, order history, cancellation,
WhatsApp ordering, and admin order management are implemented in this MVP.
Natural-language food requests on WhatsApp use Gemini when `GEMINI_API_KEY` is configured;
the bot still supports the numbered menu flow if Gemini is unavailable.
Generate a valid API key in Google AI Studio and replace the current value in `.env` to enable
Gemini intent extraction.
AI recommendations, RAG, live notifications, demand prediction, and queue-based
slot recommendations require a separate data/AI phase after real order history exists.
