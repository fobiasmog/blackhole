run-aistor:
	docker run -dt \
		-p 9000:9000 -p 9001:9001 \
		-v $(PWD)/data:/mnt/data \
		-v $(PWD)/license:/minio.license \
		--name "aistor-server" \
		quay.io/minio/aistor/minio:latest minio server /mnt/data \
		--license /minio.license

run-api:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --loop uvloop
