docker_config_umbra:
	sleep 10.0
	docker exec -it umbra-container psql -h /tmp -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres'"

build_up_databases:
	docker-compose -f databases/compose-postgres.yml -f databases/compose-mysql.yml -f databases/compose-sqlserver.yml -f databases/compose-umbra.yml -f databases/compose-db2.yml up --remove-orphans -d

restore_start_databases:
	make remove_all_database_instances
	make start_databases
	
start_databases:
	docker rm -f postgres-container mysql-container sqlserver-container umbra-container
	make build_up_databases
	make docker_config_umbra
	make start_db2
	make info_docker_instances

remove_databases:
	docker rm -f postgres-container mysql-container sqlserver-container umbra-container db2-container

start_db2:
	docker rm -f db2-container
	docker-compose -f databases/compose-db2.yml up -d

info_docker_instances:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

info_databases_port_process:
	sudo netstat -tulpn | grep :5100
	sudo netstat -tulpn | grep :5200
	sudo netstat -tulpn | grep :5300
	sudo netstat -tulpn | grep :5400
	sudo netstat -tulpn | grep :5500

remove_all_database_instances:
	docker rm -f postgres-container mysql-container sqlserver-container umbra-container db2-container
	docker-compose -f databases/compose-postgres.yml -f databases/compose-mysql.yml -f databases/compose-sqlserver.yml -f databases/compose-umbra.yml -f databases/compose-db2.yml down --rmi local

pipeline:
	python pipeline.py

info:
	mpstat -P ALL 2 5

stop_databases:
	@if [ -n "$$(docker ps -q)" ]; then \
		docker stop $$(docker ps -q); \
	else \
		echo "No running containers to stop."; \
	fi