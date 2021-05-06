# cowin-tracker
monitor the vaccine appointment availability near you and will send message in telegram (bot) as soon as slots become available.


Todo: 
1. create a telegram bot https://core.telegram.org/bots
2.  



# Prepare docker compose 
run the following in terminal
```
DISTRICT_ID= <your_district_id>
LOCATION=<your_district_id> [ If multiple sep by comma, Ex. konnagar,uttarpara ]
TELEGRAM_TOKEN_ID= <your_telegram_token>
TELEGRAM_CHAT_ID=<your_telegram_chat_id>

sed -i.bak "s/DISTRICT_ID=.*/DISTRICT_ID=$DISTRICT_ID/g" docker-compose.yml
sed -i.bak "s/LOCATION=.*/LOCATION=$LOCATION/g" docker-compose.yml
sed -i.bak "s/TELEGRAM_TOKEN_ID=.*/TELEGRAM_TOKEN_ID=$TELEGRAM_TOKEN_ID/g" docker-compose.yml
sed -i.bak "s/TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID/g" docker-compose.yml


sudo docker-compose build up -d

```