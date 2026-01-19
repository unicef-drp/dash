
# TransMonEE Dashboard

The **TransMonEE Dashboard** is an interactive visualization tool for monitoring child rights across Europe and Central Asia. It provides access to a wide range of disaggregated data and CRC recommendations aligned with the Regional Child Rights Monitoring (CRM) Framework.

🌍 **Live Dashboard:**  
[https://www.transmonee.org/europe-central-asia-child-rights-data-dashboard](https://www.transmonee.org/europe-central-asia-child-rights-data-dashboard)


---

## Features

- Explore indicators by domain and sub-domain, aligned with the CRM Framework
- View interactive charts, maps, and trends over time
- Filter by country, region, disaggregations (sex, age, residence, wealth), and year
- Access and filter CRC recommendations linked to child rights bottlenecks
- Download charts and datasets directly from the dashboard

---

## Technology Stack

- **Dash** and **Flask** for the web framework
- **Plotly** for interactive data visualizations
- **pandasdmx** for accessing SDMX API data from UNICEF
- **Docker** and **VS Code Dev Containers** for streamlined development
- **GitHub Actions** for automated deployment

---

## Getting Started (VS Code Dev Container)

1. **Install prerequisites:**
   - [Docker](https://www.docker.com/products/docker-desktop)
   - [Visual Studio Code](https://code.visualstudio.com/)
   - VS Code extension: _Dev Containers_

2. **Clone the repository:**

   ```bash
   git clone https://github.com/unicef-drp/dash.git
   cd dash
   ```

3. **Open the folder in VS Code** and choose **“Reopen in Container”**.  
   This will automatically build the environment and install dependencies.

4. **Run the app locally:**

   Open [http://localhost:8000/?prj=tm](http://localhost:8000/?prj=tm) in your browser once the container is running.

> Ensure Docker is running before opening VS Code.

---

## Continuous Deployment

Changes pushed to the `main` branch automatically trigger a GitHub Actions workflow that redeploys the live dashboard at:

👉 [https://www.transmonee.org/europe-central-asia-child-rights-data-dashboard](https://www.transmonee.org/europe-central-asia-child-rights-data-dashboard)

No manual deployment steps are required.

---

## Maintainers

This dashboard is maintained by the UNICEF Europe and Central Asia Regional Office and UNICEF Division of Data, Analytics, Planning and Monitoring. For any feedback or issues, please contact us at transmonee@unicef.org.

