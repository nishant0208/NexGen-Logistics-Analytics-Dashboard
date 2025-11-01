# 🚚 NexGen Logistics Analytics Platform

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io)

An interactive web dashboard for analyzing a logistics company's complete operational data. This platform transforms 7 separate CSV datasets into a single, unified application, providing actionable insights into performance, cost, and customer satisfaction.

This dashboard serves as a "single source of truth" for managers to get a high-level overview or deep-dive into specific areas to identify problems and make data-driven decisions.

## ✨ Features

* **Unified Data:** Loads and merges 7 distinct CSV files (orders, delivery, cost, fleet, inventory, routes, and feedback).
* **Interactive Filtering:** A persistent sidebar allows filtering the entire dashboard by **Date Range**, **Carrier**, **Priority**, and **Location**.
* **KPI Dashboard:** A high-level overview with key metrics like *Total Orders*, *On-Time Delivery %*, *Avg. Customer Rating*, and *NPS Score*.
* **9 Analytic Tabs:** A deep dive into every aspect of the business:
    * 🚛 Delivery Performance
    * 💰 Cost Analysis
    * 🗺️ Routes & Distance
    * 📦 Inventory
    * ⭐ Customer Experience
    * 🚐 Fleet Analytics
    * 💡 Automated Insights
    * 🌱 Sustainability

## 📸 Screenshots

Here are a few views of the dashboard in action:

| Dashboard Overview | Cost Analysis |
| :---: | :---: |
| <img src="screenshots/Screenshot 2025-11-01 232929.png" alt="Dashboard Overview" width="400"> | <img src="screenshots/Screenshot 2025-11-01 233000.png" alt="Cost Analysis" width="400"> |

| Delivery Performance | Customer Experience |
| :---: | :---: |
| <img src="screenshots/Screenshot 2025-11-01 233028.png" alt="Delivery Performance" width="400"> | <img src="screenshots/Screenshot 2025-11-01 233046.png" alt="Customer Experience" width="400"> |

*Note: You may need to create a `screenshots` folder in your repository and update the paths above.*

## 🛠️ Tech Stack

* **Python:** Core programming language.
* **Streamlit:** For building the interactive web UI.
* **Pandas:** For data loading, manipulation, and analysis.
* **Plotly:** For creating all interactive charts and visualizations.

## 📊 Data

The dashboard is powered by 7 core CSV files, which are loaded and merged at runtime:
1.  `orders.csv`
2.  `delivery_performance.csv`
3.  `cost_breakdown.csv`
4.  `routes_distance.csv`
5.  `customer_feedback.csv`
6.  `vehicle_fleet.csv`
7.  `warehouse_inventory.csv`

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nishant0208/NexGen-Logistics-Analytics-Dashboard.git)
    cd YOUR_REPOSITORY
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have a `requirements.txt` file with `streamlit`, `pandas`, and `plotly` listed)*

3.  **Run the app:**
    ```bash
    streamlit run nexgen-logistics-app.py
    ```

4.  Open your browser and navigate to `http://localhost:8501`.

## 📄 License

This project is licensed under the MIT License.
