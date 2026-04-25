up:
	docker-compose up -d

down:
	docker-compose down

deploy: up uvicorn-up

redeploy: down up

uvicorn-up:
	./venv/Scripts/python -m uvicorn app.main:app --reload

ps:
	docker ps

mongo-logs:
	docker exec -it iot_mongo mongosh iot_logs --eval "db.analysis_logs.find().pretty()"

venv: python-venv venv-install-requirements

python-venv:
	python -m venv venv

venv-install-requirements:
	./venv/Scripts/pip install -r requirements.txt

kafka-logs:
	docker-compose logs kafka

kafka-health:
	docker exec iot_kafka kafka-topics --bootstrap-server localhost:9092 --list