<div align="center">
  <img src="./logo-white.png" alt="Edurata Logo" width="150" />
  
  # **Edurata Functions**
  
  _Open-source workflow templates for orchestrating Python and Node.js functions._

  ![License](https://img.shields.io/github/license/Edurata/edurata-workflows)
  ![Last Commit](https://img.shields.io/github/last-commit/Edurata/edurata-workflows)
  ![Issues](https://img.shields.io/github/issues/Edurata/edurata-workflows)
</div>

---

# **About Edurata Functions**

Edurata Functions is a collection of data processing functions designed for the Edurata platform. These functions are written in **Python** and **Node.js**, available for public use, and optimized for automation and integration tasks.

---

## **Repository Structure**

### 📂 `clients`
- **Purpose:** Generic functions that interact with entire third-party APIs.
- **Example:** A function interfacing with Google Docs API, offering extensive API functionality beyond writing to a single document.

### 📂 `general`
- **Purpose:** API-agnostic functions providing essential utilities.
- **Example:** An HTTP client function like `axios` for sending general HTTP requests.

### 📂 `internals`
- **Purpose:** Internal functions used by the Edurata platform, shared for transparency.
- **Example:** Workflow automation scripts for internal builds or deployments.

### 📂 `etl`
- **Purpose:** Functions structured into `extract`, `transform`, and `load` categories.
- **Example:** Extracting data from a Google Doc, transforming it to JSON, and loading it into a Google Sheet.

---

**🚀 Get Started:** Use these functions as a foundation for your automation projects on the Edurata platform. Contributions and enhancements are always welcome!

