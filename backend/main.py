from flask import Flask, request, jsonify
from backend.database import Database
from datetime import datetime
app = Flask(__name__)

# Словарь для хранения ID платежей и их статусов
payment_ids = {}

def convert_iso_to_mysql_datetime(iso_str):
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

# Основной вебхук, который обрабатывает все события
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    event_type = data.get('event', {}).get('type')

    db_handler = Database()

    # Обработка события создания платежа (charge:created)
    if event_type == 'charge:created':
        charge_id = data.get('event', {}).get('data', {}).get('id')
        description = data.get('event', {}).get('data', {}).get('description')
        name = data.get('event', {}).get('data', {}).get('name')
        amount = data.get('event', {}).get('data', {}).get('pricing', {}).get('local', {}).get('amount')
        currency = data.get('event', {}).get('data', {}).get('pricing', {}).get('local', {}).get('currency')
        created_at = data.get('event', {}).get('data', {}).get('created_at')
        expires_at = data.get('event', {}).get('data', {}).get('expires_at')
        success_url = data.get('event', {}).get('data', {}).get('redirects', {}).get('success_url')
        failure_url = data.get('event', {}).get('data', {}).get('redirects', {}).get('cancel_url')
        user_id = description.split(' ')[-1]  # Предполагается, что ID пользователя в описании

        # Преобразуем даты из формата ISO в формат MySQL
        created_at_mysql = convert_iso_to_mysql_datetime(created_at)
        expires_at_mysql = convert_iso_to_mysql_datetime(expires_at)

        if charge_id:
            # Вставляем данные в базу
            db_handler.insert_payment(
                payment_id=charge_id,
                user_id=user_id,
                description=description,
                name=name,
                amount=amount,
                currency=currency,
                status='created',
                created_at=created_at_mysql,
                expires_at=expires_at_mysql,
                success_url=success_url,
                failure_url=failure_url
            )
            payment_ids[charge_id] = 'created'
            print(f"Payment created with ID: {charge_id}")
            return jsonify({"status": "Payment created", "charge_id": charge_id}), 200

    # Обработка события подтверждения оплаты (charge:confirmed)
    elif event_type == 'charge:confirmed':
        charge_id = data.get('event', {}).get('data', {}).get('id')
        description = data.get('event', {}).get('data', {}).get('description')  # Добавляем описание
        subscription = data.get('event', {}).get('data', {}).get('name')

        user_id = None

        if description:
            user_id = int(description.split(' ')[-1])  # ID пользователя из описания платежа

        if charge_id and charge_id in payment_ids:
            # Обновляем статус платежа в базе данных
            db_handler.update_payment_status(charge_id, 'confirmed')

            # Обновляем подписку и имя пользователя в базе данных
            if subscription == 'standard':
                db_handler.update_user_savailable_openings(user_id, 10)
                db_handler.set_subscription_expiration(user_id)
            elif subscription == "month_unlimited":
                db_handler.set_subscription_expiration(user_id)
            db_handler.update_user_subscription(user_id, subscription)

            payment_ids[charge_id] = 'confirmed'
            print(f"Payment confirmed with ID: {charge_id}, subscription: {subscription} for user ID: {user_id}")
            return jsonify({"status": "Payment confirmed", "charge_id": charge_id}), 200
        else:
            return jsonify({"error": "Charge ID not found"}), 404


# Эндпоинт для проверки статуса платежа по его ID
@app.route('/payment_status/<charge_id>', methods=['GET'])
def payment_status(charge_id):
    status = payment_ids.get(charge_id)
    if status:
        return jsonify({"charge_id": charge_id, "status": status}), 200
    else:
        return jsonify({"error": "Charge ID not found"}), 404


if __name__ == '__main__':
    # Запуск сервиса на локальном хосте, порт 5000
    app.run(host='0.0.0.0', port=5005)