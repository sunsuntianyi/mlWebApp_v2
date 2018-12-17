# mlWebApp_v2 (Dec_17_2018)

## Demo: http://35.227.20.196:3000 (server is up and running)

This is the implementation of the deep convolutional neural network model, Inception.
Tech involved: GCP, Kubernetes, Docker(Compose), TensorFlow(Serving), Node.js, MongoDB, Python, JavaScript, HTML, CSS, Jade(pug).

![alt text](https://github.com/sunsuntianyi/mlWebApp_v2/blob/master/demo/1.png)

![alt text](https://github.com/sunsuntianyi/mlWebApp_v2/blob/master/demo/2.png)


Steps for using the web app locally on your computer:


Step 1: Install MongoDB 

    # First you need to install MongoDB on your system, Please visit MonogoDB site and download it.


Step 2: Install NodeJS 
 
     # Please visit NodeJS site and download installer. Install on your system, it also installs NPM.


Step 3: Install required dependencies

    # build node_modules:

    # first build an package.json file, then cd to the file dir and run:
    
    npm install     
    

Step 4: Running the application:

    # Change directory to the webapp dir ad run using command npm:
    
    cd ./WEBAPP
    npm start
    (or)
    nodemon
    
    # Your local webapp can then be accessed at 0.0.0.0:3000
    
    
EXTRA:

The neural network model is up in the GCP and running 24/7, therefore, if you just want to use the model, feel free to use it.

Download the "MLmodel" folder, remove the '.py' extension

Call the file in the terminal:

    MLmodel/inception_client --server=35.196.81.176:9000  --image= absolute/path/to/your/image
    
![alt text](https://github.com/sunsuntianyi/webapp/blob/master/demo3.png)
