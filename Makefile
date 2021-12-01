make server:
	uvicorn main:app --reload

make build-kepler:
	cd frontend/kepler.gl; npm run build; cd ../..;