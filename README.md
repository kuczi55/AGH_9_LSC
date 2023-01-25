# AGH_9_LSC

The files were grouped into three project stages:

- `1_initial_tests` - first evaluation of `knative` features
- `2_events_tests` - configuration used to testing external AWS eventing functions
- `3_real_life_application` - configuration of ML pipeline 

To run the project, Kubernetes distribution (e.g. Minikube) with installed knative eventing and serving and TriggerMesh CRDs is required.
Also, AWS keys needs to be provided and `model` archive needs to be unpacked.