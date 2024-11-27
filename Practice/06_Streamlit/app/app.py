import streamlit as st
import duckdb
import matplotlib.pyplot as plt


st.title("Streamlit practice session")

con = duckdb.connect("sales.db", read_only=True)

# ---- Filters ----
st.sidebar.header("Filters")

# Filter by Year
query_years = "SELECT DISTINCT year FROM dim_date WHERE date_id IN (SELECT date_id FROM fact_sales) ORDER BY year;"
years = [row[0] for row in con.execute(query_years).fetchall()]
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)


# Filter by Sales Amount
min_sales, max_sales = 100, 1000 
selected_sales = st.sidebar.slider(
    "Filter by Sales Amount",
    min_value=min_sales,
    max_value=max_sales,
    value=(min_sales, max_sales),
)

if not selected_years:
    st.write("Please select at least one year to display results.")
else:

    # Query to fetch data
    query_1 = f"""
    SELECT 
        d.year, d.month, 
        SUM(f.sales_amount) AS total_sales
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE d.year IN ({','.join(map(str, selected_years))})
    AND f.sales_amount BETWEEN {selected_sales[0]} AND {selected_sales[1]}
    GROUP BY d.year, d.month
    ORDER BY d.year, d.month;
    """
    data_1 = con.execute(query_1).fetchall()

    # Ensure the data is available
    if data_1:
        # Extract Year-Month as formatted strings and Total Sales
        year_month = [f"{row[0]}-{row[1]:02d}" for row in data_1]  # Format as "YYYY-MM"
        total_sales = [row[2] for row in data_1]

        # Create a dictionary for plotting
        chart_data = {
            "Year-Month": year_month,
            "Total Sales": total_sales,
        }

        # Plot using st.line_chart
        st.line_chart(data=chart_data, x="Year-Month", y="Total Sales")
    else:
        st.write("No data available for the selected filters.")

    # Query for Top 5 Products by Total Sales
    query_2 = f"""
    SELECT 
        p.product_name, 
        SUM(f.sales_amount) AS total_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE d.year IN ({','.join(map(str, selected_years))})
    AND f.sales_amount BETWEEN {selected_sales[0]} AND {selected_sales[1]}
    GROUP BY p.product_name
    ORDER BY total_sales DESC
    LIMIT 5;
    """
    data_2 = con.execute(query_2).fetchall()

    # Ensure there is data to display
    if data_2:
        # Extract data for plotting
        product_names = [row[0] for row in data_2]
        total_sales = [row[1] for row in data_2]

        # Create a horizontal bar chart
        fig, ax = plt.subplots(facecolor="none", edgecolor="none")  # Transparent background
        ax.barh(product_names, total_sales, color="skyblue")
        ax.set_xlabel("Total Sales", color="white")
        ax.set_ylabel("Product Name", color="white")
        ax.set_title("Top 5 Products by Total Sales", color="white")
        ax.tick_params(colors="white")

        # Set figure transparency
        fig.patch.set_alpha(0.0)  # Fully transparent figure background
        ax.set_facecolor("none")  # Transparent plot background

        st.pyplot(fig)
    else:
        st.write("No data available for the selected filters.")


    # Query for Customer Type Distribution
    query_3 = f"""
    SELECT 
        c.customer_type, 
        SUM(f.sales_amount) AS total_sales
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_date d ON f.date_id = d.date_id
    WHERE d.year IN ({','.join(map(str, selected_years))})
    AND f.sales_amount BETWEEN {selected_sales[0]} AND {selected_sales[1]}
    GROUP BY c.customer_type;
    """
    data_3 = con.execute(query_3).fetchall()

    # Ensure there is data to display
    if data_3:
        # Extract data for plotting
        customer_types = [row[0] for row in data_3]
        total_sales = [row[1] for row in data_3]

        # Create a horizontal bar chart
        fig, ax = plt.subplots(facecolor="none", edgecolor="none")
        bars = ax.barh(customer_types, total_sales, color="skyblue")

        # Add labels to the bars
        for bar, value in zip(bars, total_sales):
            ax.text(
                bar.get_width() + 5000,  # Position slightly after the bar
                bar.get_y() + bar.get_height() / 2,  # Center vertically
                f"{value:,}",  # Format number with commas
                va="center",
                ha="left",
                color="white"
            )

        # Set axis labels and title
        ax.set_xlabel("Total Sales", color="white")
        ax.set_ylabel("Customer Type", color="white")
        ax.set_title("Sales Contribution by Customer Type", color="white")

        # Update tick colors
        ax.tick_params(colors="white")

        # Set figure transparency
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

        # Display chart in Streamlit
        st.pyplot(fig)
    else:
        st.write("No data available for the selected filters.")

