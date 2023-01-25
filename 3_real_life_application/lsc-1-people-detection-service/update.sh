docker build -t jaceken/lsc-1-people-detection-service . &&
docker image push docker.io/jaceken/lsc-1-people-detection-service:latest && 
kubectl delete -f ../lsc-1-service.yml &&
kubectl apply -f ../lsc-1-service.yml