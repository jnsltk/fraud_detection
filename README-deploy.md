## Commands for building, running and pushing the docker image to the registry
`
```zsh
# Must be run in the root directory of the project
docker login registry.git.chalmers.se

# Will build for amd64, only this platform is supported for our kubernetes cluster
docker build --platform linux/amd64 -t backend -f ./fraud_detection/dockerfile .
docker run --rm -it -p 8000:8000 -e DB_PASSWORD="<omidded>" -e RUN_MODE="dev" backend:latest

# To push:
docker tag backend:latest registry.git.chalmers.se/courses/dit826/2024/group1/backend:latest
docker push registry.git.chalmers.se/courses/dit826/2024/group1/backend:latest
```

## Commands for deploying to a kubernetes cluster
>Not particularly useful as you probably can't access the cluster, but here they are anyway.

```zsh

# After logging in to the cluster...

kubectl apply -f deployment.yaml

kubectl delete pods -l app=backend # ensures new image is pulled

```

## Other useful commands:

```zsh
kubectl create secret generic db-credentials --from-literal=DB_PASSWORD='<omidded>'

kubectl create secret docker-registry docker-registry --docker-server=registry.git.chalmers.se --docker-username='<your CID>' --docker-password='<your-chalmers-password>'

```
