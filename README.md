# You're Cute Genes: Which Genes are Being Discovered and When?

This project is compiled of three Python scripts that build a Flask application, provide different routes for the user to query that return different pieces of information about the HGNC data, using the HGNC complete set from HUGO, and create jobs as prompted by the user. The project also includes a Dockerfile that allows any user to pull the image from Docker Hub and run an instance of the image into a container on their personal machine, as well as a docker-compose file that allows a user to start the container easily and succinctly.

The project also includes .yml files that include a Redis service, deployment, and pvc, as well as a Flask service, deployment, and worker deployment for job workers, and a nodeport and ingress for public functionality. These files allow the project to be deployed into Kubernetes.

The Flask application routes are important because the HGNC data contains loads of information that may not be interesting to the user. The Flask application and the routes allow users to quickly query the information that they may be looking for without having to comb through the data manually. The application also utilizes the Redis database, making it possible to store the data and return to it, even after restaring the application. The Jobs and Worker api files are how we get a queue going for our larger app route for building our images with specific data ranges. The Dockerfile allows any user to have access to these capabilities through running an instance of the image on their own machine, plus the docker-compose file automates the deployment of the application, so the container is easy to start. 

## Accessing and Describing the Data
 
The HGNC data is loaded in from this link, https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc\_complete\_set.json , where the data is in json format. The application uses requests to access the data, and the POST route puts the data into the Redis database. The data contains lots of unique and interesting information about every hgnc\_id that the HGNC has approved.

## Flask App and Its Routes

The Flask application contains many different functions for users to query. There is a route that originally loads the data into the Redis database. From there, users can query different routes depending on the type of information they would like to access, including a route that generates a plot of the data. Users can also delete data from the database using routes. 

## Pulling the Image and Running the App on a VM

Install the project by cloning the repository. 

Use ```docker pull avlavelle/gene_api``` to pull a copy of the container.
Then, ```docker-compose up --build``` will get the container running using the compose file, build the image, and bind the appropriate port inside the container to the appropriate port on the host.

In a separate window, you can use ``` curl localhost:5000/<route> ``` to call the routes.

## Building a New Image from the Dockerfile

In order to build a new image from the Dockerfile, use the same ```docker pull``` command from above. 
Then, use ```docker-compose build``` to build the image and use ```docker images``` to check that a copy of the image has been built.

## Using and Deploying into Kubernetes

Clone the repository and pull the image in a Kubernetes cluster using instructions from above. No changes should be required for the Kubernetes files or the Python script because an environment variable should dynamically set the Redis host IP. 

Users must then ```kubectl apply -f <file_name.yml>``` for each service, deployment, and pvc. 

Then, users should exec into the debug pod. Using ```kubectl get pods```, the debug bod name should become available. Exec into this pod using ```kubectl exec -it <debug_pod_name> -- /bin/bash```.

Users should then be able to ```curl avlav-test-flask-service:5000/<route>``` all of the routes from within the debug pod.

In addition, it is possible to ```curl``` the routes from the commandline in kube-access without having to exec into a pod. Users should check the port of their NodePort using kubectl get services. This port number should match the port number for the prod-service-nodeport in the gene-prod-ingress.yml file, as well. Using that port, users can curl the routes with ```curl avlav.coe332.tacc.cloud:<port>/route```. The curl with the current specified port for the NodePort and Ingress is ```curl avlav.coe332.tacc.cloud:31817/routes```.

## ```/image``` Route

The ```/image?start=int&end=int -X POST``` route reads the date each unique gene entry was first approved from the database, tabulates how many genes were approved each year, and creates a bar graph of the data, which it writes into another database. When parameters are not used, the bar graph includes every year for which there is data. When parameters are used, the bar graph only includes the desired years.

The ```/image``` route is the default GET request. It returns the plot to the user, so when the route is called, the user must name their plot in the ```curl``` request, just like ```curl localhost:5000/image>>myimage.png```. After that, the image should be created and available within the repository on the VM. Two ```scp``` actions are then required to see the image.

The first takes place on the VM:
```
scp ./ <image_name.png> username@address.edu:./
```
The commandline should return confirmation of the ```scp```. 

On the user's local machine in the intended folder or repository:
```
scp username@address.edu:./<image_name.png> ./
```
The commandline should return confirmation of the ```scp```, and the user should be able to access the plot image from their file explorer.

The ```/image -X DELETE``` route deletes the image from the database.

## Example Queries and Interpretation of Results

For the ```/data``` POST route which puts the data into Redis:
```
Data loaded
```

For the ```/data``` DELETE route which deletes the data in Redis:
```
Data deleted, there are 0 keys in the db
```

For the ```/data``` GET route which returns all the data from Redis:
```
[{"version": ..., "alias\_symbol": [...], "data\_approved\_reserved": ...}...]
```

For the ```/genes``` route which returns a json-formatted list of all hgnc_ids:
```
[..., "HGNC:13195", ..., "HGNC:24523"]
```

For the ```/genes/<hgnc_id>``` route which returns all the data associated with <hgnc_id>:
```
{["hgnc\_id": "HGNC:24523", "location": ..., ...]}
```

For the ```/image?start=int&end=int``` POST route which creates a plot image for the desired years and loads it into Redis:
```
Image created
```

For the ```/image``` GET route which retrieves the plot:
The user should follow the instructions above to retreive the image.
The return of this route will not be visible to the user. 

For the ```/image``` DELETE route which deletes the plot from the database:
```
Image deleted, there are 0 keys in the db
```

For the ```/help``` route which returns help text for the user:
```
These are the routes for the gene_api.py.

post data to the database
    /data (POST)              Post the data to the database
    ...
retrieve elements from the data in the database
    /data (GET)               Return all the data in the database
    ...
delete data from the database
    /data (DELETE)            Delete the data from the database
    ...
get help
    /help (GET)               Return help text for the user
```

For the ```/when/<hgnc_id>``` route which returns the approval and modification dates of a specified gene:
```
{
 "date first approved": "1989-06-30",
 "date last modified": "2023-01-20"
}
```

For the ```/imagedata``` route which returns the data used to create the plot in the ```/image``` POST route:
```
{
 "1986": 307,
 "1987": 8,
 "1988": 156,
 ...,
 "2023": 124,
 "Years": "Number of Entries Approved"
}
```

For the ```/locus/<hgnc_id>``` route which returns the locus group of a specified gene:
```
{
 "locus group": "protein-coding gene"
}
```

For the ```/locusdata``` route which returns the tabulated values for the amount of genes in each locus group:
```
{
 "Locus Group": "Number of Entries",
 "non-coding RNA": 9056"
 ...
}
```

For the ```/jobs``` route which creates a new job to perform an analysis of the data:
