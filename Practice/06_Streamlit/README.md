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

Using the practice session Docker container, app, and database as baseline, add the following:
* New filter based on the Product Category ("Home", etc)
  * If none are selected, the app should direct the user to choose at least one product category.
* Add coordinates to the `dim_customer` table based on the column `location` -- the coordinates should match roughly the location in Estonia (e.g. you can make location=North match coordinates in Harjumaa, Lääne-Virumaa, Ida-Virumaa)
* Add a new map chart
  * The point on the map should be customer location.
  * The size of the point on the map should correspond to the sales amount by the customer.

To earn a bonus point:
* Submit a working and executable GitHub repo. Your repo should contain:
  * The app with the requirements from above
  * The script you used for modifying the `dim_customer` table
  * A screencast showing that the added filter works for all four charts (3 from the walkthrough and the new map you added)

The repo should be sent to e-mail at latest by 11:44.  
NB! Make sure that your solution matches all the requirements of the assignment.