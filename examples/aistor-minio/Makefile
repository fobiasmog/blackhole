run-aistor:
	docker run -dt \
		-p 9000:9000 -p 9001:9001 \
		-v $(PWD)/data:/mnt/data \
		-v $(PWD)/license:/minio.license \
		--name "aistor-server" \
		quay.io/minio/aistor/minio:latest minio server /mnt/data \
		--license /minio.license
