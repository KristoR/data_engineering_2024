## Streamlit walkthrough

Start the container with `docker compose up -d`

Review the `Dockerfile` and `compose.yml`

Once the service has started, you can navigate to `localhost:8501` in your browser.

Review the example app and the associated code in `app/app.py` 

If you make any changes in `app.py` it should be populated to the UI immediately.

### Options in the UI

To create a tutorial or share insights you can use the following options from the UI:
* Print
* Screencast

### Streamlit Hello World 

For more advanced examples, you can go into the container using:  
`docker exec -it sl bash` 

In the container run `streamlit hello`

Then, navigate to `localhost:8502`

### Assignment
