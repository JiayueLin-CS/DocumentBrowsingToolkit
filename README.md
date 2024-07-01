# Welcome to the Topic Modeling Toolkit

The Topic Modeling Toolkit serves as an essential instrument in enhancing the accessibility and discoverability of text documents.

## Obtaining the Sample Data
- Download the sample [SQL database](https://drive.google.com/drive/folders/150xE6kxM5UXO902Tk_IoqdfOJIYb8S2O?usp=share_link) and place the `sql` folder in the `root` directory.
- Download the sample [json](https://drive.google.com/file/d/1eNem1IIACiVoNU2DcPGvL0DcPcTQzeVj/view?usp=share_link) and [csv](https://drive.google.com/file/d/1CNfQiyyLr8_e-hqS7kCqJslWsbnhkEKd/view?usp=share_link) files and place them under `back_end/TopicModelingKit`.

## Installing Dependencies

The following is a set of instructions to set up the environment for running the backend and frontend on a Linux server or Unix machine. For optimal performance, it is recommended to create a new Conda virtual environment to prevent package conflicts. It is important to note that a Python version of 3.7 or higher is required for all necessary packages.
- The environment can be set up using Anaconda as follows:
    - Confirm that Anaconda is installed and available. Then, execute the following command to create and activate the environment:
    - Create a Conda virtual environment
        ```bash 
        $ conda create −−name <env> −−file requirements_conda.txt
        ```
    - Activate the virtual environment
        ```bash 
        $ conda activate <env>
        ```
- Alternatively, the environment can also be set up using pip by executing the following command:
    - Install all required packages.
        ```bash 
        $ pip install -r requirements_pip.txt
        ```


## Starting the Backend

- To start the backend, navigate to the project directory and then to the back_end
folder by entering the following command:
    ```bash 
    $ cd back_end
    ```
- Once you’re in the back_end folder, start the search service by navigating to the
Search.java file located in the following directory:
    ```bash
    $ cd TopicModelingKit/src/utils/SearchEngine/src/Search.java
    ```
- After navigating to the Search.java file, start the search service by running the
Java file.
- Next, navigate back to the back_end folder and start the backend server by
running the following command:
    ```bash
    $ python server.py
    ```
- Access the API: 
    - Once the backend server is running, you can access the API by using the URL http://localhost:5000/.

##  Starting the Frontend

- To get started with the frontend, make sure you are in the project directory.
Then, navigate to the topic_modeling_toolkit folder by entering the following
command:
    ```bash
    $ cd front_end/topic_modeling_toolkit
    ```
- Once you’re in the correct folder, install the required dependencies by entering
the following command:
    ```bash
    $ npm install
    ```
- After the installation is complete, start the frontend by entering the following
command:
    ```bash
    $ npm start
    ```
- Access the application on personal machine: 
    - Open your web browser and navigate to http://localhost:3000/ to access the application.