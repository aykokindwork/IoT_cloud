up:
	docker-compose up -d

down:
	docker-compose down

redeploy: down up

uvicorn-up:
	uvicorn app.main:app --reload

ps:
	docker ps

mongo-logs:
	docker exec -it iot_mongo mongosh iot_logs --eval "db.analysis_logs.find().pretty()"