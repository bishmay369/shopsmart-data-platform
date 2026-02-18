# 🛍️ ShopSmart AI — Intelligent Data Platform on Azure

End-to-end **enterprise-grade Data Engineering project** built on Azure implementing a cloud-native **Medallion Architecture (Bronze → Silver → Gold)**.

This platform simulates a real-world e-commerce ecosystem with:

- ✅ Batch ingestion + transformations  
- ✅ Real-time streaming via Azure Event Hubs  
- ✅ PII masking + quarantine-based data quality framework  
- ✅ Star Schema modeling in Gold layer  
- ✅ ML use cases: RFM segmentation + payment anomaly detection  
- ✅ CI/CD with GitHub Actions → Databricks deployment  

---

# 🏗️ Architecture

| Layer | Technology |
|-------|------------|
| Storage | Azure Data Lake Storage Gen2 (ADLS) |
| Compute | Azure Databricks (PySpark + Spark SQL + Delta Lake) |
| Orchestration | Azure Data Factory (ADF) |
| Streaming | Azure Event Hubs |
| Secrets | Azure Key Vault + Databricks Secret Scope |
| Monitoring | Azure Monitor + Log Analytics |
| Infrastructure | Terraform (IaC) |
| CI/CD | GitHub Actions |

---

# 📊 Data Sources (6 + Streaming)

Synthetic enterprise e-commerce dataset simulating real production systems:

1. **Orders** (CSV — PostgreSQL export/CDC simulation)
2. **Order Items** (CSV)
3. **Customers** (Nested JSON — REST API simulation)
4. **Products** (Nested JSON — MongoDB simulation)
5. **Inventory** (CSV — daily snapshot)
6. **Payments** (JSON — payment gateway API simulation)
7. **Clickstream Events** (Real-time via Azure Event Hub)

---

# 🥉 Bronze Layer (Raw Zone)

- Stores raw source data **as-is**
- Immutable ingestion
- Includes **quarantine area** for rejected records
- Stored in Delta format

---

# 🥈 Silver Layer (Cleaned & Validated)

### Data Engineering Features Implemented

- Type casting & schema enforcement  
- Standardization (trim, lower/upper case normalization)  
- Nested JSON flattening  
- Business logic transformations  
- Data quality validation rules  
- Quarantine pattern for invalid records  

### 🔐 PII Governance

- `email` → SHA-256 hash (`email_hash`)
- `phone` → masked
- Null emails flagged for review

---

## Silver Tables Created

| Table | Records | Notes |
|-------|---------|-------|
| silver/orders | 1,948 | 52 quarantined (NULL order_status) |
| silver/order_items | 4,904 | Cleaned |
| silver/customers | 500 | PII masked; 53 null emails flagged |
| silver/products | 50 | Nested attributes flattened |
| silver/inventory | 150 | 4 negative stock corrected |
| silver/payments | 2,000 | Fraud signals engineered |
| silver/clickstream | 3,000 | Cleaned |
| silver/sessions | 3,000 | Session aggregates |
| silver/streaming_clickstream | Streaming | Event Hub ingestion |

---

# 🥇 Gold Layer (Business-Ready Analytics)

Implements **Star Schema Modeling**

## Dimension Tables

- `gold/dim_date` (2024–2026)
- `gold/dim_customer` (SCD2-ready, surrogate keys)
- `gold/dim_product`

## Fact Tables

- `gold/fact_sales` (grain = 1 order line item)
- `gold/agg_daily_sales`

---
# 🤖 Machine Learning / Advanced Analytics

## 1️⃣ Customer Segmentation — RFM Model

Built using:

- Recency
- Frequency
- Monetary value

Quintile scoring (1–5) applied.

### Segment Distribution

- Champions → 87
- Loyal Customers → 132
- Potential Loyalists → 150
- At Risk → 67
- Hibernating → 52

Output Table: `gold/ml_customer_rfm`

---

## 2️⃣ Payment Anomaly Detection

Hybrid approach:

- Z-score anomaly detection (per payment method)
- Rule-based fraud indicators:
  - Off-hours transactions
  - High transaction amount
  - High risk score
  - International payments

### Example Output

- Statistical anomalies: 77
- CRITICAL risk: 106
- HIGH risk: 325

Output Table: `gold/ml_anomaly_detection`

---

# ⚡ Real-Time Streaming (Azure Event Hub)

### Flow

1. Python producer sends clickstream JSON events
2. Event Hub ingests events
3. Databricks streaming notebook consumes events
4. Data written to:
   - `bronze/streaming_clickstream`
   - `silver/streaming_clickstream`

> Demonstrates near real-time ingestion architecture

---

# 📈 Monitoring & Observability

Log Analytics Workspace: `log-shopsmart-dev`

Enabled diagnostics:

- ADLS transaction metrics
- ADF PipelineRuns
- ADF ActivityRuns
- TriggerRuns

---

# 🚀 CI/CD Pipeline

GitHub Actions automatically:

- Deploys notebooks to Databricks
- Maintains workspace sync
- Supports production-ready workflow

---
# 🔮 Future Enhancements

- Native Spark Structured Streaming connector (single-user cluster)
- Demand forecasting ML model
- Power BI dashboard connected to Gold layer
- Microsoft Purview for data lineage
- Advanced fraud detection using ML classifiers

---

# 🎯 Key Takeaways

This project demonstrates:

- Enterprise Data Engineering best practices  
- Cloud-native architecture on Azure  
- Data quality + governance  
- Streaming + batch integration  
- Dimensional modeling  
- ML integration inside data platform  
- CI/CD automation  

---

# 👨‍💻 Author

**Bishmay Kumar**  
Data Engineering Enthusiast | Azure | Databricks | ML Integration  
